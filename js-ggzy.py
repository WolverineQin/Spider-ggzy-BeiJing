# -*- encoding:utf-8 -*-

import requests
from lxml import html
from bs4 import BeautifulSoup
import use_api as api
import random
import pymysql as py
import time

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
    for i in range(1,21):
        url_base1 = 'http://www.ccgp-jiangsu.gov.cn'
        url_base2 = 'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg'
        patten = '//*[@id="newsList"]/ul/li['+str(i)+']/a/@href'
        url_path = selector.xpath(patten)
        url_str = ''.join(url_path)
        if url_str[0:6]  == '../../':
            url = url_base1 + url_str[5:]
            urllist.append(url)
        else:
            url = url_base2 + url_str[1:]
            urllist.append(url)
    return urllist

def get_data(url):
    page = get_page(url)
    page.encoding = 'utf-8'
    data = page.text
    soup = BeautifulSoup(data,'lxml')
    title_list = soup.select('.dtit h1')
    if len(title_list) == 1:
        title_str = title_list[0].get_text()
        title_str = title_str.strip()
        title = ''.join('%s' % id for id in title_str)
    else:
        print("查询标题失败,该URL标题不为1!")
        return None,None
    content_list = soup.select('.content')
    if len(content_list) == 1:
        content = ''.join('%s' % id for id in content_list)
    else:
        print("查询内容失败,该URL无内容!")
        return None, None
    return title,content

def insert_db(title,article,url,web):
    db = py.connect(host='******', port=3306, user='root', password='******', db='user_prd')
    cursor = db.cursor()
    sql = "insert into `js_ggzy` (`title`, `article`, `url`, `websitename`)  value(%s,%s,%s,%s)"
    try:
        print("插入数据库开始")
        cursor.execute(sql,(title,article,url,web))
        db.commit()
        print("插入数据库结束")
    except Exception as e:
        print("Error is %s" % e)
    db.close()

def main():
    web = "江苏政府采购信息网"
    for i in range(182,1500):
        url = 'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/index_'+str(i)+'.html'
        urllist = get_urllist(url)
        print("第%s页的urllist收集完毕！"%(i+1))
        print(urllist)

        for j in range(0,len(urllist)):
            title,content = get_data(urllist[j])
            if title != None and content != None:
                insert_db(title,content,urllist[j],web)

    #urllist = ['http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/wuxi/201910/t20191008_527119.html', 'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/wuxi/201910/t20191008_527117.html', 'http://www.ccgp-jiangsu.gov.cn/ggxx/gkzbgg/wuxi/201910/t20191008_527116.html']

    #第一页
    # for i in range(0,len(urllist)):
    #     title,content = get_data(urllist[i])
    #     insert_db(title, content, urllist[i], web)

if __name__ == '__main__':
    main()
