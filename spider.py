# -*- encoding:utf-8 -*-

import requests
from lxml import html
from bs4 import BeautifulSoup
import use_api as api
import random
import pymysql as py

def get_page(url):
    ip = api.get_proxy()
    proxies = {
        "http:": str("http://" + str(ip))
    }
    cookies_pool = [
        'clientlanguage=zh_CN; _gscu_1277169039=734418782e5a5y13; _gscbrs_1277169039=1; JSESSIONID=EF357A16AC7A01A2403D2D1350AF8EF4; _gscs_1277169039=t73471259hjdm1u14|pv:3',
        'clientlanguage=zh_CN; _gscu_1277169039=734418782e5a5y13; _gscbrs_1277169039=1; JSESSIONID=EF357A16AC7A01A2403D2D1350AF8EF4; _gscs_1277169039=t73471259hjdm1u14|pv:1'
        'clientlanguage=zh_CN; _gscu_1277169039=734418782e5a5y13; _gscbrs_1277169039=1; JSESSIONID=EF357A16AC7A01A2403D2D1350AF8EF4; _gscs_1277169039=t73471259hjdm1u14|pv:4',
        'JSESSIONID=5CA8366002EA83F2AF7CE402B500980E; clientlanguage=zh_CN; _gscu_1277169039=734719104w69nr75; _gscs_1277169039=73471910uevkfx75|pv:4; _gscbrs_1277169039=1'
        'JSESSIONID=5CA8366002EA83F2AF7CE402B500980E; clientlanguage=zh_CN; _gscu_1277169039=734719104w69nr75; _gscs_1277169039=73471910uevkfx75|pv:7; _gscbrs_1277169039=1'
    ]
    headers = {
        "Cookie": random.choice(cookies_pool)
        , "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0"
    }
    print(proxies)
    page = requests.get(url, proxies=proxies, headers=headers)
    return page

def get_urllist(url):
    page = get_page(url)
    page.encoding = 'utf-8'
    data = page.text
    etree = html.etree
    selector = etree.HTML(data)
    urllist = []
    title_list = []
    for i in range(1,3):
        patten_url = '/html/body/div[2]/div[5]/ul/li['+str(i)+']/a/@href'
        patten_title = '/html/body/div[2]/div[5]/ul/li['+str(i)+']/a/@title'
        content = selector.xpath(patten_url)
        title = selector.xpath(patten_title)
        urllist.extend(content)
        title_list.extend(title)
    return urllist,title_list

def get_content(url):
    page = get_page(url)
    page.encoding = 'utf-8'
    data = page.text
    etree = html.etree
    selector = etree.HTML(data)
    soup = BeautifulSoup(data,'lxml')
    content = soup.select('.content-list')
    content_str = ''.join('%s' % id for id in content)
    return content_str

def insert_db(title,article,url,web):
    db = py.connect(host='******', port=3306, user='root', password='******', db='user_prd')
    cursor = db.cursor()
    sql = "insert into `bj_ggzy` (`title`, `article`, `url`, `websitename`)  value(%s,%s,%s,%s)"
    try:
        print("插入数据库开始")
        cursor.execute(sql,(title,article,url,web))
        db.commit()
        print("插入数据库结束")
    except Exception as e:
        print("Error is %s" % e)
    db.close()

def main():
    web = '北京市公共资源交易平台'
    for i in  range(38,39):
        url = 'https://ggzyfw.beijing.gov.cn/jylczfcg/index_'+str(i)+'.html'
        url_base = 'https://ggzyfw.beijing.gov.cn'
        urllist,title_list = get_urllist(url)

        for j in range(0,len(urllist)):
            urllist[j] = url_base + urllist[j]
        print("第%d页的urllist收集完毕！" % i)

        for k in range(0,len(urllist)):
            content = get_content(urllist[k])
            insert_db(title_list[k],content,urllist[k],web)

if __name__ == '__main__':
    main()
