#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/7 18:46
# @Author  : lichenxiao

import os
import logging
from conf.settings import get_result_path, get_log_path, email_list_str
from db.process_number import re_process_number
from db.operate_db import insert, connect_to_db, close_connection, delete_all
from lib.utils import send_email

# middleman_list = ['woaiwojia','maitian','souhujiaodian','anjuke','tuitui99','fangtianxia']
middleman_list = ['woaiwojia', 'maitian', 'sohujiaodian', 'anjuke', 'tuitui99']
middleman_cn_list = ['我爱我家', '麦田', '搜狐焦点', '安居客', '推推99']

middleman_to_source_dict = {
    'woaiwojia': 171,
    'maitian': 172,
    'sohujiaodian': 173,
    'anjuke': 174,
    'tuitui99': 175}
# 'fangtianxia': 176}

middleman_count_dict = {
    'woaiwojia': 0,
    'maitian': 0,
    'sohujiaodian': 0,
    'anjuke': 0,
    'tuitui99': 0}
# 'fangtianxia': 0}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=get_log_path('middleman'),
                    filemode='a')


def update_db():
    conn = connect_to_db()
    for basedir, subdirs, filenames in os.walk(get_result_path()):
        for filename in filenames:
            middleman = os.path.splitext(filename)[0].lstrip('u_')
            source = middleman_to_source_dict[middleman]
            delete_all(source)
            with open(os.path.join(basedir, filename), 'rb') as f_in:
                for line in f_in:
                    line = line.lstrip('\n')
                    if not line:
                        continue
                    line_list = line.split('\t')
                    try:
                        number = line_list[1]
                        company = line_list[2]
                    except IndexError:
                        continue
                    number_list = re_process_number(number)
                    for number_type, number, extension in number_list:
                        if not number_type == 'wrong':
                            res = insert(conn, number=number, source=source, tag=company)
                            if not res:
                                for i in range(0, 3):
                                    conn = connect_to_db()
                                    res = insert(conn, number=number, source=source, tag=company)
                                    if res:
                                        middleman_count_dict[middleman] += 1
                                        break
                                    if not conn:
                                        logging.error('%s, cannot connect to db ,%s' % (source, line))
                                        exit()
                            else:
                                middleman_count_dict[middleman] += 1

    close_connection(conn)


def generate_email_str():
    head = '''<html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=gb2312"/>
    <title>中介爬虫统计</title>
    </head>
    <body>
    <p>中介爬虫爬取周期为三个月，本次抓取入库结果如下：</p>
    <table border="1">
        <tr>
            <th>名称</th>
            <th>入库数量</th>
        </tr>
    '''
    tail = '''</table>
    </body>
    </html>'''
    content_str_list = []
    for i, item in enumerate(middleman_list):
        content_str_list.append('<tr>')
        content_str_list.append('<td>' + middleman_cn_list[i] + '</td>')
        content_str_list.append('<td>' + str(middleman_count_dict[item]) + '</td>')
        content_str_list.append('</tr>')
    content_str = '\n'.join(content_str_list)
    return head + content_str + tail


if __name__ == "__main__":
    # update_db()
    send_email(email_list_str, '中介爬虫结果统计', generate_email_str(), 'html')
