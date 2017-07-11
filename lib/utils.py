#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/2/9 19:36
# @Author  : lichenxiao


import smtplib
import logging
from email.mime.text import MIMEText
from lxml import html

from conf.settings import email_list_str, smtp, get_data_path


def get_xpath_content(origin_url, page_text, xpath_str):
    """
    从html内容中获取xpath对应的结果
    :param origin_url:
    :param page_text:
    :param xpath_str:
    :return:list
    """
    if not page_text:
        return None
    page_tree = html.document_fromstring(page_text)
    page_tree.make_links_absolute(origin_url)
    try:
        res_list = page_tree.xpath(xpath_str)
    except Exception as e:
        return None
    if not res_list:
        return None
    if type(res_list) != list:
        res_list = list(res_list)
    return res_list


def record_res(page_res_list, middleman_type):
    """
    记录抓取结果
    :param page_res_list:
    :param middleman_type:
    :return:
    """
    try:
        file_obj = open(get_data_path(middleman_type), 'ab')
        for item in page_res_list:
            file_obj.write('\t'.join(item) + '\n')
            file_obj.flush()
        return True
    except Exception, e:
        return False


def send_email(receiver, subject, content, content_type):
    """
    发送邮件
    :param receiver:string 逗号分隔的，邮件的接受者
    :param subject: string 邮件主题
    :param content: string 邮件的内容
    :return:
    """
    msg = MIMEText(content, content_type)
    msg.set_charset('utf8')
    sender = smtp['user'] + r"@sogou-inc.com"
    receiver_list = list(receiver)
    msg['To'] = ','.join(receiver_list)
    msg['From'] = sender
    msg['Subject'] = subject

    # try:
    smtpObj = smtplib.SMTP()
    smtpObj.connect(smtp['host'], 25)  # 25 为 SMTP 端口号
    smtpObj.login(smtp['user'], smtp['password'])
    smtpObj.sendmail(sender, receiver_list, msg.as_string())
    # except Exception, e:
    #     err = "Send email from %s to %s failed!\n Exception: %s!" \
    #           % (sender, receiver, e)
    #     logging.error(err)



if __name__ == '__main__':
    send_email(email_list_str, 'nihao', 'lalala','plain')
