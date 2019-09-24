# -*- coding: UTF-8 -*-
#!/usr/bin/env python
import requests
import re
from bs4 import BeautifulSoup
import time
import argparse
import sys
import datetime
from multiprocessing import Pool

def crawl(url):
    all_data = open("all_articles.txt", "wb+")
    popular_data = open("all_popular.txt", "wb+")
    starttime = datetime.datetime.now()
    num_page = 435

    while(num_page > 0):
        response = requests.get(url, cookies={"over18": "1"})
        time.sleep(0.05)
        soup = BeautifulSoup(response.text, "html.parser")
        r_ent = soup.find_all(class_="r-ent")
        
        for ent in r_ent:
            date = ent.find_all(class_='date')
            day_str = date[0].string.split('/')
            day = int(day_str[0] + day_str[1])
            if url == "https://www.ptt.cc/bbs/Beauty/index2324.html" and int(day_str[0])==12 :
                continue
            if url == "https://www.ptt.cc/bbs/Beauty/index2758.html" and int(day_str[0])==1 :
                continue

            link = ent.find("a")
            url_info = "https://www.ptt.cc" + link.get("href")
            title = list(link.strings)
            finish_1 = str(day)+","+"".join(title)+","+url_info+"\n"
            print(finish_1.rstrip())
            if re.search("[公告]",finish_1):
                continue
            all_data.write(finish_1.encode("utf-8"))

            nrec = ent.find_all("span")
            if re.search("爆",str(nrec)):
                popular_data.write((finish_1).encode('utf-8'))
                          
        url = "https://www.ptt.cc" + \
            soup.find_all(class_='btn wide')[2].get('href')
        num_page = num_page-1
    all_data.close()
    popular_data.close()
    endtime = datetime.datetime.now()
    print ("Spend Time: ", endtime - starttime)


def push(start,end):
    time.sleep(0.05)
    starttime = datetime.datetime.now()
    like = 0
    boo = 0
    push_dict = {}
    all_data = open('all_articles.txt', 'r')
    push_data = open("push[%d-%d].txt" %(start, end), "wb+")
    data = all_data.readlines()
    all_data.close()
    
    for data_search in data: 
        data_select = data_search.split(',')
        day = int(data_select[0])
        #title = str(data_select[1])
        url = str(data_select[-1]).rstrip()

        if day > end:
            break
        if day >= start:
            response = requests.get(url, cookies={"over18": "1"})
            soup = BeautifulSoup(response.text, "html.parser")
            class_push = soup.find_all(class_="push")
            
            for push in class_push:
                push_info = push.find_all("span")
                if len(push_info) != 0:    
                    #tag = push_info[0].string
                    userid = push_info[1].string
                
                if re.search("推 ",str(push_info)):
                    like += 1
                    if userid in push_dict:
                        push_dict[userid]["like"] +=1
                    else:
                        push_dict[userid] = {"like": 1, "boo": 0}
                        
                
                if re.search("噓 ",str(push_info)):
                    boo += 1
                    if userid in push_dict:
                        push_dict[userid]["boo"] +=1
                    else:
                        push_dict[userid] = {"like": 0, "boo": 1}
        
    finish_2 = []
    finish_2.append("all like: %d\n" %like )
    finish_2.append("all boo: %d\n" %boo )

    like_rank = sorted(push_dict, key=lambda x: (push_dict[x]["like"]*-1,x), reverse=True)
    for i, j in enumerate(reversed(like_rank[-10:])):
        temp = "like #%d: %s %d\n" % ((i+1), j, push_dict[j]["like"])
        #print(temp.rstrip())
        finish_2.append(temp)

    boo_rank = sorted(push_dict, key=lambda x: (push_dict[x]["boo"]*-1,x), reverse=True)
    for i, j in enumerate(reversed(boo_rank[-10:])):
        temp = "boo #%d: %s %d\n" % ((i+1), j, push_dict[j]["boo"])
        #print(temp.rstrip())
        finish_2.append(temp)

    finish_2 = "".join(finish_2)+"\n"
    push_data.write((finish_2).encode('utf-8'))
    push_data.close()
    endtime = datetime.datetime.now()
    print ("Spend Time: ", endtime - starttime)















       
    
                
                
                
                
                
                
     






   

















if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mod",type=str,nargs="+")
    args = parser.parse_args()

    if args.mod[0]=="crawl":
        print("2018 Beauty crawler") 
        url = "https://www.ptt.cc/bbs/Beauty/index2324.html"
        crawl(url)

    elif args.mod[0]=="push":
        print('crawl push and boo from', int(args.mod[1]), 'to', int(args.mod[2]))
        push(int(args.mod[1]),int(args.mod[2]))
    
    elif args.mod[0]=='popular': 
        print('popular from', int(args.mod[1]), 'to', int(args.mod[2]))
        
    
    elif args.mod[0]=='keyword':
        print('search',args.cmd[1], 'from', int(args.cmd[2]), 'to', int(args.cmd[3]))
       


