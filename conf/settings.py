#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 16:23
# @Author  : lichenxiao

import os
import time

#debug = False
debug = True

format_date = time.strftime('%Y%m%d', time.localtime())
base_path = os.path.abspath('.')
base_data_path = os.path.join(base_path, 'data')
base_log_path = os.path.join(base_path, 'log')
base_result_path = os.path.join(base_path, 'result')

smtp = {
    'host': 'mail.sogou-inc.com',
    'user': 'lichenxiao',
    'password': '1991Lcx-',
    'duration': 30,
    'tls': False,
}

if not debug:
    db_conf = {'DB_ip': 'haoma06.dt.mysql.db',
               'DB_user': 'sogouhaoma',
               'DB_pwd': 'sogouhaoma@2012',
               'DB_database': 'mobile_haoma', }
    email_list_str = 'liushuai207839@sogou-inc.com,' \
                     'shubaihan@sogou-inc.com,' \
                     'yiyating@sogou-inc.com,' \
                     'liangying@sogou-inc.com,' \
                     'wujian@sogou-inc.com,' \
                     'lichenxiao@sogou-inc.com,'


    def get_log_path(middleman_type):
        current_log_path = os.path.join(base_log_path, format_date)
        if not os.path.exists(current_log_path):
            os.makedirs(current_log_path)
        log_path = os.path.join(current_log_path, middleman_type + '.log')
        return log_path


else:
    db_conf = {'DB_ip': '10.134.99.212',
               'DB_user': 'test',
               'DB_pwd': 'test',
               'DB_database': 'telephone_blacklist', }
    email_list_str = 'lichenxiao@sogou-inc.com'


    def get_log_path(middleman_type):
        log_path = os.path.join(base_log_path, middleman_type + '.log')
        return log_path


def get_data_path(middleman_type):
    data_path = os.path.join(base_data_path, middleman_type + '.txt')
    return data_path


def get_result_path():
    return base_result_path
