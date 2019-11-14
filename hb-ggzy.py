# -*- encoding:utf-8 -*-

import requests
from lxml import html
from bs4 import BeautifulSoup
import use_api as api
import random
import pymysql as py
from urllib.parse import urlencode

def get_page(p,url_base):
    ip = api.get_proxy()
    proxies = {
        "http:": str("http://" + str(ip))
    }
    cookies_pool = [
        "JSESSIONID=07ED51FF896B91B67295A08D1390D11E; JSESSIONID=2559C93BF631DA8BB83E38BE1526E73B",
        "JSESSIONID=25F0BB2841820ADE0C1C64455A7E730F; JSESSIONID=B47E922BFADF7043C43012DC19BF8812",
        "JSESSIONID=C15C0B57D2CB402EED8C625646FE06F9; JSESSIONID=A91BF8E16B7454D3C74D8BEA09834BF1"
    ]

    headers = {
        "Cookie": "JSESSIONID=7E6DCDFFAAA4B6FF862204E7A4230266; JSESSIONID=B47E922BFADF7043C43012DC19BF8812",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
    }

    data = {
        'queryInfo.type': 'xmgg',
        'queryInfo.key': '',
        'queryInfo.jhhh': '',
        'queryInfo.gglx': '招标公告',
        'queryInfo.cglx': '',
        'queryInfo.cgfs': '',
        'queryInfo.qybm': '420001',
        'queryInfo.begin': '2018 / 11 / 12',
        'queryInfo.end': '2019 / 11 / 13',
        'queryInfo.pageNo': p,
        'queryInfo.pageSize': '15',
        'queryInfo.pageTotle': '610'
    }

    print(proxies)

    try:
        page = requests.post(url_base,data=data,headers=headers,proxies=proxies)
        if page.status_code == 200:
            return page
    except Exception as e:
        print(e)

def get_data_page(url):
    ip = api.get_proxy()
    proxies = {
        "http:": str("http://" + str(ip))
    }
    cookies_pool = [
        "2559C93BF631DA8BB83E38BE1526E73B",
        "C15C0B57D2CB402EED8C625646FE06F9",
        "JSESSIONID=B47E922BFADF7043C43012DC19BF8812"
    ]
    headers = {
        "Cookie": random.choice(cookies_pool)
        , "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0"
    }
    print(proxies)
    try:
        page = requests.get(url, proxies=proxies, headers=headers)
        if page.status_code == 200:
            return page
    except Exception as e:
        print(e)

def get_urllist(p,url):
    page = get_page(p,url)
    page.encoding = 'utf-8'
    data = page.text.strip()
    etree = html.etree
    selector = etree.HTML(data)
    urllist = []
    for i in range(1,16):
        patten = '//*[@id="main"]/div/div/div[2]/div[2]/div/ul/li['+str(i)+']/a/@href'
        url_base = selector.xpath(patten)
        #print(url_base)
        urllist.extend(url_base)
    if len(urllist) != 0:
        return urllist
    else:
        print("Cookie已经失效！")

def get_data(url):
    page = get_data_page(url)
    page.encoding = 'utf-8'
    data = page.text
    soup = BeautifulSoup(data,'lxml')
    title_list = soup.select('.flfg .title')
    if len(title_list) != 0:
        title = ''.join('%s' % id.get_text() for id in title_list)
    else:
        print("查询该URL标题失败！")

    content_list = soup.select('#main')
    if len(content_list) == 1:
        content = ''.join('%s' % id for id in content_list)
    else:
        print("查询URL内容失败，无法得到页面内容!")
    return title,content

def insert_db(title,article,url,web):
    db = py.connect(host='******', port=3306, user='root', password='******', db='user_prd')
    cursor = db.cursor()
    sql = "insert into `hb_ggzy` (`title`, `article`, `url`, `websitename`)  value(%s,%s,%s,%s)"
    try:
        print("插入数据库开始")
        cursor.execute(sql,(title,article,url,web))
        db.commit()
        print("插入数据库结束")
    except Exception as e:
        print("Error is %s" % e)
    db.close()

def main():
    web = "湖北政府采购信息网"
    url_page = 'http://www.ccgp-hubei.gov.cn:8050/quSer/search'
    for i in range(2,600):
        urllist = []
        urllist = get_urllist(i,url_page)
        print("第%s页urllist收集完毕!" % i)
        print(urllist)

        for url in urllist:
            title,content = get_data(url)
            insert_db(title,content,url,web)

if __name__ == '__main__':
    main()
