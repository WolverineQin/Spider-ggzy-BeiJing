# -*- encoding:utf-8 -*-

import requests
from lxml import html
from bs4 import BeautifulSoup
import use_api as api
import random
import pymysql as py
import time
from urllib.parse import urlencode

class NMG:
    def __init__(self,url_base,url_data_base):
        self.url_base = url_base
        self.url_data_base = url_data_base

    def get_page(self,url,k):
        ip = api.get_proxy()
        proxies = {
            "http:": str("http://" + str(ip))
        }

        headers = {
            "Cookie": "userDeviceType=pc",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
        }
        print(proxies)

        data = {
            "type_name": "3",
            "annstartdate_S": "2016-11-18",
            "annstartdate_E": "2019-11-18",
            "byf_page": k,
            "fun": "cggg"
        }

        try:
            page = requests.post(url,data=data,headers=headers,proxies=proxies)
            if page.status_code == 200:
                return page.json()
            else:
                print("访问URL失败!")
        except Exception as e:
            print(e)

    def get_data_page(self,url,tb_id,p_id):
        ip = api.get_proxy()
        proxies = {
            "http:": str("http://" + str(ip))
        }
        headers = {
            "Cookie": "userDeviceType=pc",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36"
        }
        print(proxies)
        data = {
            "tb_id": tb_id,
            "p_id": p_id
        }
        try:
            page = requests.get(url,params=data,proxies=proxies,headers=headers)
            if page.status_code == 200:
                return page
            else:
                print("访问单独URL失败!")
        except Exception as e:
            print(e)

    def get_urllist(self,k):
        url = self.url_base
        data = self.get_page(url,k)[0]
        title_list = []
        tb_id_list = []
        p_id_list = []
        for item in data:
            title_list.append(item['TITLE_ALL'])
            tb_id_list.append(item['ay_table_tag'])
            p_id_list.append(item['wp_mark_id'])

        return title_list,tb_id_list,p_id_list

    def get_data(self,tb_id,p_id,k):
        url  = self.url_data_base
        page = self.get_data_page(url,tb_id,p_id)
        page.encoding = 'UTF-8'
        url_result = page.url
        data = page.text
        soup = BeautifulSoup(data,'lxml')
        content_list = soup.select('#center')
        if len(content_list) != 0:
            content = ''.join('%s' % id for id in content_list[0])
        else:
            print("第%s个URL查询单独内容失败！"%k)
        return content,url_result

def insert_db(title,article,url,web,sfbg,k,i):
    db = py.connect(host='******', port=3306, user='root', password='******', db='user_prd')
    cursor = db.cursor()
    sql = "insert into `nmg_ggzy` (`title`, `article`, `url`, `websitename`, `sfbg`)  value(%s,%s,%s,%s,%s)"
    try:
        print("插入第%s页第%s页的数据开始"%(k,i+1))
        cursor.execute(sql,(title,article,url,web,sfbg))
        db.commit()
        print("插入第%s页第%s页的数据结束"%(k,i+1))
    except Exception as e:
        print("Error is %s" % e)
    db.close()

if __name__ == '__main__':
    web = '内蒙古自治区政府采购网'
    sfbg = 0 #0代表不是变更的数据
    url_base = 'http://www.nmgp.gov.cn/zfcgwslave/web/index.php?r=new-data%2Fanndata'
    url_data_base = 'http://www.nmgp.gov.cn/category/cggg?'
    nmg = NMG(url_base,url_data_base)
    for k in range(53,4355):
        title_list,tb_id_list,p_id_list = nmg.get_urllist(k)
        print(title_list)
        content_list = []
        print("第%s页已URL已收集完毕!"%k)
        for i in range(0,len(tb_id_list)):
            content,url = nmg.get_data(tb_id_list[i],p_id_list[i],k)
            #print(type(title_list[i]),type(content),type(url),type(web))
            print(url)
            insert_db(title_list[i],content,url,web,sfbg,k,i)
            time.sleep(1)
