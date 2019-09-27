import requests
from bs4 import BeautifulSoup
import time
from collections import OrderedDict
from operator import getitem
import re
import argparse
import sys

headers = {
    'User-Agent': 'Mozilla/5.0 \
        (Macintosh; Intel Mac OS X 10_13_4) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/35.0.1916.47 Safari/537.36'}


def decode(cfemail):
    enc = bytes.fromhex(cfemail)
    return bytes([c ^ enc[0] for c in enc[1:]]).decode('utf8')


def deobfuscate_cf_email(soup):
    for encrypted_email in soup.select('span.__cf_email__'):
        print(encrypted_email['data-cfemail'])
        decrypted = decode(encrypted_email['data-cfemail'])
        encrypted_email.replace_with(decrypted)


def crawl(url):
    f_data = open('all_articles.txt', 'wb+')
    popular_data = open('all_popular.txt', 'wb+')
    start_time = time.time()
    save = False
    url1 = url
    month = 12
    done = False
    while not done:
        time.sleep(0.01)
        try:
            r = requests.get(url1, headers=headers, cookies={'over18': '1'})
        except Exception as e: print(e)
        content = r.text.encode('utf-8')
        soup = BeautifulSoup(content, "html.parser")
        url1 = "https://www.ptt.cc" + \
            soup.find_all(class_='btn wide')[1].get('href')
        r_ent = soup.find_all(class_="r-ent")
        for ent in reversed(r_ent):
            # check date
            date = ent.find_all(class_='date')
            if len(date) != 1:
                print('date error:'+url1)
                break
            day_str = date[0].string.split('/')
            day = int(day_str[0] + day_str[-1])
            mon_n = day//100
            if month != mon_n:
                if mon_n == 1 and month == 12:
                    save = False
                elif mon_n == 12 and month == 1:
                    save = False
                    done = True
                else:
                    month -= 1
                    save = True
            else:
                save = True
            # save to file
            if save:
                link = ent.find_next('a')
                deobfuscate_cf_email(link)
                url = 'https://www.ptt.cc' + link.get('href')
                title = list(link.strings)
                nrecs = ent.find_all('span')
                nrec = ''
                if len(nrecs) != 0:
                    nrec = nrecs[0].string
                info = str(day)+','+''.join(title)+','+url+'\n'
                # print(nrec+','+info)
                if re.search("[公告]",info) is not None:
                    continue

                f_data.write(info.encode('utf-8'))
                if nrec == '爆':
                    popular_data.write(info.encode('utf-8'))
    print('last url:' + url1)
    print('finish in : ' + str(time.time() - start_time))
    f_data.close()
    popular_data.close()


def get_data(url, data):
    try:
        r = requests.get(url, headers=headers, cookies={'over18': '1'})
    except Exception as e: print(e)
    time.sleep(0.01)
    content = r.text.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    for push in soup.find_all(class_='push'):
        p = push.find_all('span')
        if len(p) != 0:
            tag = p[0].string
            user = p[1].string
            # print(tag, user)
            if user in data:
                if tag == "推 ":
                    data[user]['like'] += 1
                elif tag == "噓 ":
                    data[user]['boo'] += 1
            else:
                if tag == "推 ":
                    data[user] = {'like': 1, 'boo': 0}
                elif tag == "噓 ":
                    data[user] = {'like': 0, 'boo': 1}


def push(start, end):
    if start > end:
        print('error: start day > end day')
        return
    start_time = time.time()
    f_data = open('all_articles.txt', 'r')
    data = f_data.readlines()
    f_data.close()
    user_dict = {}
    for art in reversed(data):
        info = art.split(',')
        day = int(info[0])
        url = info[-1].rstrip()
        if day > end:
            break
        if day >= start:
            # print(url)
            get_data(url, user_dict)

    # print(user_dict)
    info = []
    likes = 0
    boos = 0
    for user, data in user_dict.items():
        likes += data['like']
        boos += data['boo']
    print('all like:', likes)
    print('all boo:', boos)
    info.append('all like: %d\n' % likes)
    info.append('all boo: %d\n' % boos)

    like = sorted(user_dict, key=lambda x: (
        user_dict[x]['like']*-1, x), reverse=True)
    boo = sorted(user_dict, key=lambda x: (
        user_dict[x]['boo']*-1, x), reverse=True)

    for i, l in enumerate(reversed(like[-10:])):
        l_info = "like #%d: %s %d\n" % ((i+1), l, user_dict[l]['like'])
        print(l_info.rstrip())
        info.append(l_info)

    for i, b in enumerate(reversed(boo[-10:])):
        b_info = "boo #%d: %s %d\n" % ((i+1), b, user_dict[b]['boo'])
        print(b_info.rstrip())
        info.append(b_info)

    push_txt = open('push[%d-%d].txt' % (start, end), 'w+')
    push_txt.writelines(info)
    push_txt.close()
    print('finish in : ' + str(time.time() - start_time))


def get_img_url_content(soup, data):
    patt = 'href="(http|https)(.*)?(jpg|jpeg|png|gif)'
    img_url = re.findall(patt, soup.prettify())
    for s in img_url:
        data.append(''.join(s)+'\n')


def get_img_url(url, data):
    try:
        r = requests.get(url, headers=headers, cookies={'over18': '1'})
    except Exception as e: print(e)
    time.sleep(0.01)
    content = r.text.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    get_img_url_content(soup, data)


def popular(start, end):
    if start > end:
        print('error: start day > end day')
        return
    start_time = time.time()
    f_data = open('all_popular.txt', 'r')
    popular_txt = open('popular[%d-%d].txt' % (start, end), 'w+')
    data = f_data.readlines()
    f_data.close()
    arti = []
    for art in reversed(data):
        info = art.split(',')
        day = int(info[0])
        url = info[-1].rstrip()
        if day > end:
            break
        if day >= start:
            arti.append(url)
    popular_txt.write("number of popular articles: %d\n" % len(arti))

    for url in arti:
        img_url = []
        get_img_url(url, img_url)
        popular_txt.writelines(img_url)

    popular_txt.close()
    print('finish in : ' + str(time.time() - start_time))


def extract_content(kw, url, img_url):
    try:
        r = requests.get(url, headers=headers, cookies={'over18': '1'})
    except Exception as e: print(e)
    time.sleep(0.01)
    content = r.text.encode('utf-8')
    soup = BeautifulSoup(content, 'html.parser')
    main = soup.find(id='main-content').text
    patt = '發信站'
    starting = re.search(patt, main)
    if starting is None:
        print('missing sending station',url)
        return
    search_area = main.split('\n')
    for sentence in search_area:
        if re.search(patt, sentence) is not None:
            break
        else:
            if re.search(kw, sentence) is not None:
                print('match', url)
                get_img_url_content(soup, img_url)
                break


def keyword(kw, start, end):
    if start > end:
        print('error: start day > end day')
        return
    start_time = time.time()
    keyword_txt = open('keyword(%s)[%d-%d].txt' % (kw, start, end), 'w+')
    f_data = open('all_articles.txt', 'r')
    data = f_data.readlines()
    f_data.close()

    for art in reversed(data):
        info = art.split(',')
        day = int(info[0])
        url = info[-1].rstrip()
        if day > end:
            break
        if day >= start:
            img_url = []
            extract_content(kw, url, img_url)
            keyword_txt.writelines(img_url)

    keyword_txt.close()
    print('finish in : ' + str(time.time() - start_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ptt crawler')
    parser.add_argument('cmd', type=str, nargs='+',help='ptt crawler')
    args = parser.parse_args()

    if args.cmd[0]=='crawl':
        print('crawl 2018 beauty') 
        url = "https://www.ptt.cc/bbs/Beauty/index2759.html"
        crawl(url)

    elif args.cmd[0]=='push':
        print('rank push & boo from', int(args.cmd[1]), 'to', int(args.cmd[2]))
        # user_dict = {}
        # get_data('https://www.ptt.cc/bbs/Beauty/M.1514888280.A.84D.html',user_dict)
        # print(user_dict)
        push(int(args.cmd[1]), int(args.cmd[2]))

    elif args.cmd[0]=='popular': 
        print('search popular image from', int(args.cmd[1]), 'to', int(args.cmd[2]))
        # data = []
        # get_img_url('https://www.ptt.cc/bbs/Beauty/M.1527424010.A.ACB.html',data)
        # print(data)
        # print(len(data))
        popular(int(args.cmd[1]), int(args.cmd[2]))
    
    elif args.cmd[0]=='keyword':
        print('search',args.cmd[1], 'from', int(args.cmd[2]), 'to', int(args.cmd[3]))
        # img = []
        # extract_content("伊東紗冶子", 'https://www.ptt.cc/bbs/Beauty/M.1545491264.A.B68.html', img)
        keyword(args.cmd[1], int(args.cmd[2]), int(args.cmd[3]))