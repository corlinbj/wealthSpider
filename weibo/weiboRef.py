# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
#import pymysql.cursors

cookie = {"Cookie": "ALF=1545792338; SCF=Aqu7xbXYY-usKtX1PrjLZaAj8_H8FN-_nXNIkKLvu4FcDZYT0IGGIm5FotgwxJw2v1ei5FVwB2cpaObTvj268Mw.; SUB=_2A252_xG-DeRhGedK61IX9CfIyj-IHXVSA7_2rDV6PUJbktANLWKskW1NJafeEUjaxn17itS-vLmBNDRonCRPpCDq; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFqdyJdF9IGi5esVxffnA7T5JpX5K-hUgL.Fo2Xeh5cSh.XeKe2dJLoI79odNijIgRt; SUHB=0k10gCqwFZHJ-M; SSOLoginState=1543201262; _T_WM=5082106ce4f91a03f6592e71e3a68c2f"}

#获取博主关注的人的urls
def get_guanzhu_urls(url):

    url_g = url+ "/follow?page="
    count="1"
    url_init=url_g+count
    html = requests.get(url_init, cookies=cookie, verify=False).content #cookie登录
    selector = etree.HTML(html)
    pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value']) #获取关注人页数

    for i in range(1,pageNum+1):
        url_new=url_g+ (str)(i)
        html = requests.get(url_new, cookies=cookie, verify=False).content
        soup = BeautifulSoup(html, 'html5lib')
        person=soup.find_all('td')

        in_val=[]

        ##try:
           ## conn = pymysql.connect(host='localhost', user='root', passwd='xxx', db='weibo_spider', charset='utf8mb4')
           ## with conn.cursor() as cursor:
        for i in range(0, len(person)):
            if (i + 1) % 2 == 0:
                user = (person[i].a.string , person[i].a.get("href"), url)
                in_val.append(user)
                print(user)

                ##sql = "insert into `gurls`(`weiboid`,`url`,`prewid`) VALUES(%s,%s,%s)"
               ## cursor.executemany(sql,in_val)#将数据批量导入数据库
                ##conn.commit()
        ##finally:
           ## conn.close()

#获取博主个人信息：ID、粉丝数、关注数、关注列表URL
def get_host_user_info(url):

    html = requests.get(url, cookies=cookie, verify=False).content
    soup = BeautifulSoup(html,'html5lib')
    weiboid=soup.find_all('span',class_='ctt')[0].get_text().split()[0] #span标签
    myurl=url

    info=soup.find('div', class_='tip2')
    infolist=info.find_all('a')
    guanzhu_url = infolist[0].get("href")
    pattern_num = re.compile(r'.*\[(.*)\]')
    guanzhu_num = re.findall(pattern_num,(infolist[0].string))[0]
    fan_num = re.findall(pattern_num, (infolist[1].string))[0]

    print(weiboid,myurl,guanzhu_url,guanzhu_num,fan_num)

   ## try:
        ##conn = pymysql.connect(host='localhost', user='root', passwd='xxx', db='weibo_spider', charset='utf8mb4')
        ##with conn.cursor() as cursor:
            ##sql="insert into `wusers`(`weiboid`,`myurl`,`follower_num`,`guanzhu_num`,`guanzhu_url`) VALUES (%s,%s,%s,%s,%s)"
           ## cursor.execute(sql,(weiboid,myurl,fan_num,guanzhu_num,guanzhu_url))
          ##  conn.commit()
    ##finally:
        ##conn.close()

#获取博主微博博文
def get_weibo_contents(url):

    #只爬取原创微博
    html = requests.get(url, cookies=cookie, verify=False).content
    selector = etree.HTML(html)
    pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])
    soup=BeautifulSoup(html, 'html5lib')
    weiboid=soup.find_all('span',class_='ctt')[0].get_text().split()[0] #span标签
    print(weiboid)

    word_count = 1
    print(pageNum)

    for page in range(1, pageNum + 1):

        # 获取lxml页面
        url_new = url+"?filter=1&page="+(str)(page)
        print(url_new)
        lxml = requests.get(url_new, cookies=cookie, verify=False).content
        soup = BeautifulSoup(lxml, 'html5lib')


        content=soup.find_all('span',class_="ctt")
        comment=soup.find_all('a',class_="cc")

        in_weibo=[]

        ##try:
            ##conn = pymysql.connect(host='localhost', user='root', passwd='xxx', db='weibo_spider', charset='utf8mb4')
            ##with conn.cursor() as cursor:
        for (con,com) in zip(content,comment):
            pattern_num = re.compile(r'.*\[(.*)\]')
            com_num = re.findall(pattern_num, (com.string))[0]
            weibo=(weiboid,con.get_text(),com_num)
            in_weibo.append(weibo)

                ##sql = "insert into `weibos`(`weiboid`,`weibo_content`,`comment`) VALUES(%s,%s,%s)"
                ##cursor.executemany(sql,in_weibo)#将数据批量导入数据库
               ## conn.commit()
       ## finally:
          ##  conn.close()


if __name__ == '__main__':
    url = "https://weibo.cn/1774800467"
   # get_host_user_info(url)
    get_guanzhu_urls(url)
  #  get_weibo_contents(url)
