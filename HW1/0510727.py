# -*- coding: UTF-8 -*-
#!/usr/bin/env python
import requests
import re
from bs4 import BeautifulSoup
import time
import argparse
import sys
from multiprocessing import Pool

def crawl(url):
    all_data = open("all_articles.txt", "wb+")
    popular_data = open("all_popular.txt", "wb+")
   #start_time = time.time()
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
            print(finish_1)
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
        
    
    elif args.mod[0]=='popular': 
        print('popular from', int(args.mod[1]), 'to', int(args.mod[2]))
        
    
    elif args.mod[0]=='keyword':
        print('search',args.cmd[1], 'from', int(args.cmd[2]), 'to', int(args.cmd[3]))
       


