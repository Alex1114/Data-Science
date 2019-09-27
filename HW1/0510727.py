# -*- coding: UTF-8 -*-
#!/usr/bin/env python3
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
    starttime = datetime.datetime.now()         #執行時間起點
    num_page = 435          #2018年頁數      

    while(num_page > 0):
        response = requests.get(url, cookies={"over18": "1"})
        time.sleep(0.05)
        soup = BeautifulSoup(response.text, "html.parser")
        r_ent = soup.find_all(class_="r-ent")
        
        for ent in r_ent:
            date = ent.find_all(class_="date")
            day_str = date[0].string.split("/")
            day = int(day_str[0] + day_str[1])
            if url == "https://www.ptt.cc/bbs/Beauty/index2324.html" and int(day_str[0])==12 :
                continue
            if url == "https://www.ptt.cc/bbs/Beauty/index2758.html" and int(day_str[0])==1 :
                continue

            link = ent.find("a")
            if link:
                url_info = "https://www.ptt.cc" + link.get("href")
            else:
                continue
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
            soup.find_all(class_="btn wide")[2].get("href")
        num_page = num_page-1
    all_data.close()
    popular_data.close()
    endtime = datetime.datetime.now()
    print ("Spend Time: ", endtime - starttime)


def push(start,end):
    starttime = datetime.datetime.now()
    like = 0
    boo = 0
    push_dict = {}
    all_data = open("all_articles.txt", "r")
    push_data = open("push[%d-%d].txt" %(start, end), "wb+")
    data = all_data.readlines()
    all_data.close()
    
    for data_search in data: 
        data_select = data_search.split(",")
        day = int(data_select[0])
        #title = str(data_select[1])
        url = str(data_select[-1]).rstrip()

        if day > end:
            break
        if day >= start:
            time.sleep(0.05)
            response = requests.get(url, cookies={"over18": "1"})
            soup = BeautifulSoup(response.text, "html.parser")
            class_push = soup.find_all(class_="push")
            content = soup.find(class_="bbs-screen bbs-content").text
            stop = "※ 發信站"
            check = re.search(stop, content)
            
            if check:
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
            else:
                print("no 發信站",url)
                continue
        
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



def popular(start,end):
    starttime = datetime.datetime.now()
    popular_number = 0
    all_data = open('all_popular.txt', 'r')
    popular_data = open("popular[%d-%d].txt" %(start, end), "wb+")
    data = all_data.readlines()
    all_data.close()
    finish_3 = []
    img_url = []
    temp = []
    
    for data_search in data: 
        data_select = data_search.split(',')
        day = int(data_select[0])
        url = str(data_select[-1]).rstrip()

        if day > end:
            break
        if day >= start:
            popular_number +=1
            
            time.sleep(0.05)
            try:
                response = requests.get(url, cookies={"over18": "1"})
            except Exception as e: print(e)
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.find(class_="bbs-screen bbs-content").text
            stop = "※ 發信站"
            check = re.search(stop, content)
            
            if check:
                condition = 'href="(http|https)(.*)?(jpg|jpeg|png|gif)'
                img_url = re.findall(condition, soup.prettify())
                for string in img_url:
                    temp.append("".join(string)+"\n")

            else:
                print("no 發信站",url)
                continue

    finish_3.append("number of popular articles: %d\n" %popular_number )  
    finish_3.append("".join(temp)+"\n")           
    finish_3 = "".join(finish_3)+"\n"
    popular_data.write((finish_3).encode('utf-8'))
    popular_data.close()       
    endtime = datetime.datetime.now()
    print ("Spend Time: ", endtime - starttime)




def keyword(key,start,end):
    starttime = datetime.datetime.now()
    all_data = open('all_articles.txt', 'r')
    keyword_data = open("keyword(%s)[%d-%d].txt" %(key, start, end), "wb+")
    data = all_data.readlines()
    all_data.close()
    finish_4 = []
    temp = []

    for data_search in data: 
        data_select = data_search.split(',')
        day = int(data_select[0])
        url = str(data_select[-1]).rstrip()
        if day > end:
            break
        if day >= start:
            time.sleep(0.05)
            response = requests.get(url, cookies={"over18": "1"})
            soup = BeautifulSoup(response.text, "html.parser")
            content = soup.find(class_="bbs-screen bbs-content").text
            
            stop = "※ 發信站"
            check = re.search(stop, content)
            if check:
                content_list = content.split('\n')
                
                for match in content_list:
                    if re.search(stop, match):                      
                        break
                    else:
                        if re.search(key,match):
                            print("Get!",url)
                            condition = 'href="(http|https)(.*)?(jpg|jpeg|png|gif)'
                            img_url = re.findall(condition, soup.prettify())
                            for string in img_url:
                                temp.append("".join(string)+"\n")
                            break
            else:
                print("no 發信站",url)
                continue
     
    finish_4.append("".join(temp)+"\n")           
    finish_4 = "".join(finish_4)+"\n"
    keyword_data.write((finish_4).encode('utf-8'))
    keyword_data.close()       
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
        print("crawl push and boo from", int(args.mod[1]), "to", int(args.mod[2]))
        push(int(args.mod[1]),int(args.mod[2]))
    
    elif args.mod[0]=="popular": 
        print("crawl popular from", int(args.mod[1]), "to", int(args.mod[2]))
        popular(int(args.mod[1]),int(args.mod[2]))
    
    elif args.mod[0]=="keyword":
        print("crawl and search",args.mod[1], "from", int(args.mod[2]), "to", int(args.mod[3]))
        keyword(str(args.mod[1]),int(args.mod[2]),int(args.mod[3]))
