#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/1/15 17:26
# @Author  : Sa.Song
# @Desc    : 
# @File    : get_mess.py
# @Software: PyCharm

import json
import pymysql
import time
import datetime
from lxml import etree
from zhihu_login import login
from concurrent.futures import ThreadPoolExecutor, wait,ALL_COMPLETED

header = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}


basic_url = 'https://www.zhihu.com/people/'
start_name = 'deng-tu-zi-38'
url_module = ['activities', 'following', 'followers']  # [用户详情页面、用户关注页面、用户粉丝页面]

user_name_list = []  # 存放用户的username(唯一) 主要是循环遍历这个
on_name_list = []  # 方法级list，用来存放当前url获取到的关注者名单，用来和当前用户组成字典，便于入库
following_dict = {}  # {"用户":"关注的用户"}

def conn_mysql(user_name):
    user_list = following_dict[user_name]
    for i in user_list:
        sql = "insert into user_following (user_name,following_name) VALUES ('{0}','{1}')".format(user_name,i)
        try:
            db = pymysql.connect('118.24.26.224', 'root', '123456', 'zhihu')
            cursor = db.cursor()
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            pass



def get_page_num(session, module_num,user_name=start_name):  # 获取关注列表的总页数
    num = 0
    first_url = basic_url + user_name + '/' + module_num
    result = session.get(first_url, headers=header)
    html = result.text
    html = etree.HTML(html)
    try:
        page_button = html.xpath('//div[@class="Pagination"]/button[contains(@class,"PaginationButton") and contains(@class," Button--plain")]')
        page_num = int(page_button[-2].xpath('.//text()')[0])  # 关注列表总页数
    except:
        print('只有一页')
        page_num = 1
    return page_num

def main_logic(session,url,user_name):  # 将关注的username存入user_name_list
    num = 0
    result = session.get(url, headers=header)
    html = result.text
    html = etree.HTML(html)
    try:
        data_json = json.loads(html.xpath('//script[@id="js-initialData"]/text()')[0])
        user_details = data_json['initialState']['entities']['users']
    except Exception as e:
        print(e)
        print('----------------')
    for i in user_details:  # i是各个username
        num += 1
        if num == 1 or i == user_name:
            continue
        else:
            if i in user_name_list:
                continue
            else:
                user_name_list.append(i)
                on_name_list.append(i)
    following_dict[user_name] = on_name_list



def user_detail(session, user_name = start_name):  # 使用session循环获取用户username以及用户的关注列表
    # print(session)
    # print(user_name)
    try:
        page_num = get_page_num(session, url_module[1],user_name)  # 获取总页数
    except Exception as e:
        print('》》》》》》》》》',e)
    # print("页数：",str(page_num))

    for page in range(page_num):
        new_url = 'https://www.zhihu.com/people/{0}/{1}?page={2}'.format(user_name,url_module[1],str(page+1))  #拼接目标url
        print(new_url)
        #  url拼接原理：原始路径 + username + 页面模块标识 + page
        main_logic(session,new_url,user_name)
        conn_mysql(user_name)
        on_name_list.clear()
        following_dict.clear()


if __name__ == '__main__':
    print(datetime.datetime.now())
    t_list = []
    session = login()  # 获取serssion
    user_detail(session)
    for i in user_name_list:
        user_detail(session,i)
    # pool = ThreadPoolExecutor(max_workers=21)
    # for i in user_name_list:
    #     print('当前用户：',i)
    #     t = pool.submit(user_detail,session,i)
    #     t_list.append(t)
    # wait(t_list, return_when=ALL_COMPLETED)
    print('user_name_list列表长度：'+ str(len(user_name_list)))
    print(datetime.datetime.now())
    # try:
    #     school = data_json['initialState']['entities']['users']['qi-peng-yu']['educations'][0]['school']['name']
    #     print(school)
    # except:
    #     school = ''
    # try:
    #     business = data_json['initialState']['entities']['users']['qi-peng-yu']['business']['name']
    #     print(business)
    # except:
    #     business = ''
    # try:
    #     name = data_json['initialState']['entities']['users']['qi-peng-yu']['name']
    #     print(name)
    # except:
    #     name = ''
    # try:
    #     address = data_json['initialState']['entities']['users']['qi-peng-yu']['locations'][0]['name']
    #     print(address)
    # except:
    #     address = ''
