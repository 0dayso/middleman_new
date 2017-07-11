#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/12 18:36
# @Author  : lichenxiao

import os
import time
import logging

import MySQLdb
from conf.settings import db_conf


def get_now_time():
    """
    获取当前时间
    :return: string, 时间字符串
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")


def connect_to_db():
    """

    :return:
    """
    try:
        conn = MySQLdb.connect(db_conf['DB_ip'], db_conf['DB_user'], db_conf['DB_pwd'], port=3306,
                               charset="utf8")
        conn.select_db(db_conf['DB_database'])
        return conn
    except Exception, e:
        logging.error("connect to database fail, %s " % e)
        return False


def close_connection(conn):
    """

    :param cur:
    :return:
    """
    try:
        conn.close()
        return True
    except Exception, e:
        logging.error("close connection to database fail, %s " % e)
        return False


def insert(conn, number, source, tag, info=''):
    """
    插入大量数据
    :param conn:
    :param number: string，号码
    :param source: int，数据源
    :param tag: string，标记
    :param info: string, info字段，一般是个json结构
    :return: boolen, 更新结果
    """
    try:
        # info = '{"partner_id":"5029","title":"","icon":""}'
        # tag = u'顺丰速运'
        ctime = get_now_time()
        utime = ctime
        status = 1
        db_num = str(int(number) % 500)
        db_name = 'tbl_number_box' + db_num
        cur = conn.cursor()
        res = cur.execute(
            'insert into '+db_name+' (number,tag,info,source,status,ctime,utime) values (%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE tag=%s,info=%s,utime=%s '
            , ( number, tag, info, source, status, ctime, utime, tag, info, utime))
        logging.info('insert %s rows, source %s, db_name: %s ,number: %s' % (res, source, db_name, number))
        conn.commit()
        cur.close()
        return True
    except MySQLdb.Error, e:
        logging.error("insert source %s, %s db error, %s " % (source, number, e))
        cur.close()
        conn.close()
        return False


def get_insert_sql(number, source, tag, info=''):
    """
    插入大量数据
    :param number: string，号码
    :param source: int，数据源
    :param tag: string，标记
    :param info: string, info字段，一般是个json结构
    :return: string, insert的sql语句
    """
    try:
        # info = '{"partner_id":"5029","title":"","icon":""}'
        # tag = u'顺丰速运'
        ctime = get_now_time()
        utime = ctime
        status = 1
        db_num = str(int(number) % 500)
        db_name = 'tbl_number_box' + db_num
        insert_sql = "insert into %s (number,tag,info,source,status,ctime,utime) values ('%s','%s','%s',%s,%s,'%s','%s') ON DUPLICATE KEY UPDATE tag='%s',info='%s',utime='%s';" % ( db_name, number, tag, info, source, status, ctime, utime, tag, info, utime)
        return insert_sql
    except Exception, e:
        logging.error("generate insert sql source %s, %s error, %s " % (source, number, e))
        return None


def delete_one(conn, number, source):
    """
    删除某个数据源的某个号码
    :param number:
    :param source:
    :return: boolen, 更新结果
    """
    cur = conn.cursor()
    try:
        db_num = str(int(number) % 500)
        db_name = 'tbl_number_box' + db_num
        res = cur.execute(
            "delete from "+db_name+" where source=%s and number=%s", (source, number))
        logging.info('delete %s rows, source %s, db_name: %s ,number: %s' % (res, source, db_name, number))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception, e:
        logging.error("delete source %s, %s to database fail, %s " % (source, number, e))
        return False


def delete_all(source):
    """
    删除某个数据源的所有数据
    :param source: int,数据源
    :return: boolen, 更新结果
    """
    try:
        conn = MySQLdb.connect(db_conf['DB_ip'], db_conf['DB_user'], db_conf['DB_pwd'], port=3306,
                               charset="utf8")
        conn.select_db(db_conf['DB_database'])
        cur = conn.cursor()
    except Exception, e:
        logging.error("connect to database fail, %s " % e)
        return False
    try:
        for i in range(0, 500):
            db_name = 'tbl_number_box' + str(i)
            res = cur.execute(
                "delete from tbl_number_box%s where source=%s", (i, source))
            logging.info('delete %s rows, source %s, db_name: %s' % (res, source, db_name))
            conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception, e:
        logging.error("delete source %s, all number to database fail, %s " % (source, e))
        return False


def update_one(conn, source, info, number):
    """
    更新某个数据源的info字段
    :param source: int, 数据源
    :param info: string, info字段
    :param number: string, 可指定，也可不指定，若指定则更新这个数据源特定号码的info字段
    :return: boolen, 更新结果
    """
    cur = conn.cursor()
    try:
        db_num = str(int(number) % 500)
        db_name = 'tbl_number_box' + db_num
        res = cur.execute(
            "update "+db_name+" set info=%s where source=%s and number=%s", (info, source, number))
        logging.info('update %s rows, source %s, db_name: %s, number: %s' % (res, source, db_name, number))
        conn.commit()
        cur.close()
        return True
    except Exception, e:
        logging.error("update source %s, %s to database fail, %s " % (source, number, e))
        return False


def update_all(source, info):
    """
    更新某个数据源的info字段
    :param source: int, 数据源
    :param info: string, info字段
    :return: boolen, 更新结果
    """
    try:
        conn = MySQLdb.connect(db_conf['DB_ip'], db_conf['DB_user'], db_conf['DB_pwd'], port=3306,
                               charset="utf8")
        conn.select_db(db_conf['DB_database'])
        cur = conn.cursor()
    except Exception, e:
        logging.error("connect to database fail, %s " % e)
        return False
    try:
        for db_num in range(500):
            db_num = str(db_num)
            db_name = 'tbl_number_box' + db_num
            res = cur.execute(
                "update "+db_name+" set info=%s where source=%s", (info, source))
            logging.info('update %s rows, source %s, db_name: %s' % (res, source, db_name))
            conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception, e:
        logging.error("update source %s, all number to database fail, %s " % (source, e))
        return False


def insert_one(number, source, tag, info=''):
    """
    插入一条数据
    :param number: string，号码
    :param source: int，数据源
    :param tag: string，标记
    :param info: string, info字段，一般是个json结构
    :return: boolen, 更新结果
    """
    try:
        conn = MySQLdb.connect(db_conf['DB_ip'], db_conf['DB_user'], db_conf['DB_pwd'], port=3306,
                               charset="utf8")
        conn.select_db(db_conf['DB_database'])
        cur = conn.cursor()
    except Exception, e:
        logging.error("connect to database fail, %s " % e)
        return False
    try:
        # info = '{"partner_id":"5029","title":"","icon":""}'
        # tag = u'顺丰速运'
        ctime = get_now_time()
        utime = ctime
        status = 1
        db_num = str(int(number) % 500)
        db_name = 'tbl_number_box' + db_num
        params = [number, tag, info, source, status, ctime, utime]
        res = cur.execute(
            'insert into ' + db_name + ' (number,tag,info,source,status,ctime,utime) values (%s,%s,%s,%s,%s,%s,%s)',
            params)
        logging.info('insert %s rows, source %s, db_name: %s ,number: %s' % (res, source, db_name, number))
        conn.commit()
        cur.close()
        conn.close()
        if res:
            return True
    except Exception, e:
        logging.error("insert source %s, %s to database fail, %s " % (source, number, e))
        return False


if __name__ == '__main__':
    conn = MySQLdb.connect(db_conf['DB_ip'], db_conf['DB_user'], db_conf['DB_pwd'], port=3306, charset="utf8")
    conn.select_db(db_conf['DB_database'])
