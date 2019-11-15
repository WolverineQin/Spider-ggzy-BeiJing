# -*- encoding:utf-8 -*-

import requests
from lxml import html
from bs4 import BeautifulSoup
import use_api as api
import random
import pymysql as py
import time
import json
from urllib.parse import urlencode

class HN_GGZY:

    def get_ip(self):
        ip = api.get_proxy()
        return ip

    def __init__(self,url_base,url_content_base):
        self.url_base = url_base
        self.url_content_base = url_content_base

    def get_page(self,url,p):
        ip = self.get_ip()
        proxies = {
            "http:": str("http://" + str(ip))
        }
        print(proxies)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie":"JSESSIONID=f75s8irm-Ki7Et_cjatqyWeyO9XcMPiaH3WRASG_5jvckE5uY7H0!1895184666",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.7.1000"
        }

        Fromdata = {
            "nType": "prcmNotices",
            "startDate": "2019-01-01",
            "endDate": "2019-11-14",
            "page": p,
            "pageSize": "18"
        }

        data = urlencode(Fromdata)

        try:
            page = requests.post(url,headers=headers,data=data,proxies=proxies)
            if page.status_code == 200:
                return page
        except Exception as e:
            print(e)

    def get_data_page(self,url_add):
        ip = self.get_ip()
        proxies = {
            "http:": str("http://" + str(ip))
        }
        print(proxies)
        headers = {
            "Cookie": "JSESSIONID=f75s8irm-Ki7Et_cjatqyWeyO9XcMPiaH3WRASG_5jvckE5uY7H0!1895184666",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36 Maxthon/5.2.7.1000"
        }

        data = {
            "noticeId": str(url_add)
        }

        url = self.url_content_base + urlencode(data)
        print(url)
        try:
            page = requests.get(url,headers=headers,proxies=proxies)
            if page.status_code == 200:
                return page,url
        except Exception as e:
            print(e)

    def get_urllist(self,p):
        url = self.url_base
        page = self.get_page(url,p)
        data = json.loads(page.text)
        rows = data['rows']
        urllist = []
        titlelist = []
        for row in rows:
            url_add = row['NOTICE_ID']
            title = row['NOTICE_TITLE']
            urllist.append(url_add)
            titlelist.append(title)
        if len(urllist) != 0 and len(titlelist) != 0:
            return titlelist,urllist
        else:
            print("未获取到urllist！")

    def get_data(self,url_add):
        page,url = self.get_data_page(url_add)
        page.encoding = 'utf-8'
        data = page.text
        etree = html.etree
        selector = etree.HTML(data)
        patten_content = '/html/body'
        content_list = selector.xpath(patten_content)
        if len(content_list) != 0:
            content_b = etree.tostring(content_list[0],encoding="utf-8", pretty_print=True, method="html")
            content = content_b.decode()
            return content,url
        else:
            print("content获取失败!")

    def insert_db(self,title,article,url,web):
        db = py.connect(host='172.23.7.172', port=3306, user='root', password='BDL@BDL.123', db='user_prd')
        cursor = db.cursor()
        sql = "insert into `hn_ggzy` (`title`, `article`, `url`, `websitename`)  value(%s,%s,%s,%s)"
        try:
            print("插入数据库开始")
            for i in range(0,len(title)):
                cursor.execute(sql, (title[i], article[i], url[i], web))
            db.commit()
            print("插入数据库结束")
        except Exception as e:
            print("Error is %s" % e)
        db.close()

if __name__ == '__main__':
    web = '湖南政府采购信息网'
    url_base = 'http://www.ccgp-hunan.gov.cn/mvc/getNoticeList4Web.do'
    url_content_base = 'http://www.ccgp-hunan.gov.cn/mvc/viewNoticeContent.do?'
    hn = HN_GGZY(url_base,url_content_base)
    for p in range(3,166):
        titlelist,urllist_add = hn.get_urllist(p)
        print("第%s页的URL收集完毕!" % p)
        content_list = []
        urllist = []
        for url_add in urllist_add:
            content,url = hn.get_data(url_add)
            content_list.append(content)
            urllist.append(url)
        hn.insert_db(titlelist,content_list,urllist,web)
