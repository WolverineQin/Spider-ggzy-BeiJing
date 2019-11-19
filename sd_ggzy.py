# -*- encoding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pymysql as py
from lxml import html
import time
import json
import use_api as api

class ShanDong:
    def __init__(self,url_base,url_data_base):
        self.url_base = url_base
        self.url_data_base = url_data_base

    def get_page(self,url,p):
        ip = api.get_proxy()
        proxies = {
            "http:": str("http://" + str(ip))
        }
        print(proxies)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": "JSESSIONID=36D8414E84F48944C936D76BEFA7353B; insert_cookie=83172026",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
        }
        data = {
            "colcode": "0302",
            "curpage": p
        }
        try:
            page = requests.post(url,proxies=proxies,headers=headers,data=data)
            if page.status_code == 200:
                return page
            else:
                print("访问主URL失败!")
        except Exception as e:
            print(e)

    def get_data_page(self,url):
        ip = api.get_proxy()
        proxies = {
            "http:": str("http://" + str(ip))
        }
        print(proxies)
        headers = {
            "Cookie": "JSESSIONID=B0491D841F79BBD9AE1616ECBE582F72; insert_cookie=83172026",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
        }
        try:
            page = requests.get(url,headers=headers,proxies=proxies)
            if page.status_code == 200:
                return page
            else:
                print("The Error page's status_code is %s"%page.status_code)
        except Exception as e:
            print(e)

    def get_urllist(self,p):
        page = self.get_page(self.url_base,p)
        while page is None:
            print("搜索不到URL列表，暂停5秒!")
            time.sleep(5)
            page = self.get_page(self.url_base, p)
        page.encoding = 'UTF-8'
        data = page.text.strip()
        etree = html.etree
        soup = BeautifulSoup(data,'lxml')
        result = soup.find_all(attrs={"background": "images/main/table_bk_04.jpg"})
        urllist = []
        titlelist = []
        for re in result:
            selector = etree.HTML(str(re))
            patten_url = '//*[@class="five"]/@href'
            url = selector.xpath(patten_url)
            if len(url) == 1:
                urllist.extend(url)
            else:
                print("用soup搜寻URL失败!")
            patten_title = '//*[@class="five"]/@title'
            title = selector.xpath(patten_title)
            if len(title) == 1:
                titlelist.extend(title)
            else:
                print("用soup搜寻title失败!")
        if len(urllist) == 20 and len(titlelist) == 20:
            return urllist,titlelist
        else:
            print("查询URLlist和Titlelist失败!")

    def get_data(self,urllist,p):
        content_list = []
        url_result = []
        for i in range(0,len(urllist)):
            url = self.url_data_base + urllist[i]
            url_result.append(url)
            page = self.get_data_page(url)
            while page is None:
                print("搜索不到第i个URL，暂停5秒!")
                time.sleep(5)
                page = self.get_data_page(url)
            time.sleep(1)
            page.encoding = 'utf-8'
            data = page.text.strip()
            soup = BeautifulSoup(data,'lxml')
            content_soup = soup.select('.whole')
            if len(content_soup) == 1:
                content = ''.join('%s' % id for id in content_soup)
                content_list.append(content)
            else:
                print("第%s页查询第%s个内容失败!" % (p,i+1))
        if len(content_list) == 20:
            return content_list,url_result
        else:
            print("查询内容失败!")

    def insert_db(self,title, article, url, web,p,k):
        db = py.connect(host='******', port=3306, user='root', password='******', db='user_prd')
        cursor = db.cursor()
        sql = "insert into `sd_ggzy` (`title`, `article`, `url`, `websitename`)  value(%s,%s,%s,%s)"
        try:
            print("第%s页插入第%s个数据开始" % (p,k+1))
            cursor.execute(sql, (title, article, url, web))
            db.commit()
            print("第%s页插入第%s个数据结束" % (p,k+1))
        except Exception as e:
            print("Error is %s" % e)
        db.close()

if __name__ == '__main__':
    web = '山东省政府采购信息公开平台'
    url_base = 'http://www.ccgp-shandong.gov.cn/sdgp2017/site/channelall.jsp'
    url_data_base = 'http://www.ccgp-shandong.gov.cn'
    sd = ShanDong(url_base,url_data_base)
    for p in range(22,1000):
        urllist,titlelist = sd.get_urllist(p)
        print(urllist)
        print("第%s页URL收集完毕!" % p)
        content_list,url_result = sd.get_data(urllist,p)
        print("第%s页content收集完毕!" % p)
        for k in range(0,len(content_list)):
            print(url_result[k])
            sd.insert_db(titlelist[k],content_list[k],url_result[k],web,p,k)
        time.sleep(1)
