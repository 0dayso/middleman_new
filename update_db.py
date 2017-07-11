#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/7/7 18:46
# @Author  : lichenxiao

import os
import logging
from conf.settings import get_result_path, get_log_path
from db.process_number import re_process_number
from db.operate_db import insert, connect_to_db, close_connection,delete_all

source_to_name_dict = {
    'woaiwojia': 171,
    'maitian': 172,
    'souhujiaodian': 173,
    'anjuke': 174,
    'tuitui99': 175}
    #'fangtianxia': 176}

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=get_log_path('middleman'),
                    filemode='a')

if __name__ == "__main__":
    conn = connect_to_db()
    for basedir, subdirs, filenames in os.walk(get_result_path()):
        for filename in filenames:
            source = source_to_name_dict[os.path.splitext(filename)[0].lstrip('u_')]
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
                                    if conn:
                                        break
                                    if not conn:
                                        logging.error('%s, cannot connect to db ,%s' % (source, line))
                                        exit()
    close_connection(conn)
