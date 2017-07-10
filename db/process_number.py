#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/10 15:27
# @Author  : lichenxiao

import phonenumbers
import re

# 常用的短号码
common_number_list = ['110', '120', '119', '122', '114', '160', '117', '170', '189', '184', '106', '108', '115', '221',
                      '999', '2580', '2585']


def pre_process_number(phone):
    """
    预处理号码，
    去除中文字符，空格，
    将括号(可能是区号分机号被括号括起来)转为-，
    将斜线和逗号（可能是两个号码连接起来）都转为\
    :param phone: string,号码字符串
    :return: list,list的每一项是一个string,[号码1，号码2 。。。]
    """
    if not phone:
        return []
    # 去除'转'，空格
    phone = phone.replace('转', '-').replace('－', '-').replace(' ', '').replace('　', '')

    # 去除括号，变为-
    re_pattern = ur'^(\d*)[\(|（|\[|【](\d+)[\)|）|\]|】]-?(\d*)$'
    m = re.search(re_pattern, phone)
    if m:
        phone = m.group(1) + '-' + m.group(2) + '-' + m.group(3)
        phone = phone.strip('-')

    # 去除、\/
    phone = phone.replace('＼', '\\').replace('、', '\\').replace('/', '\\').replace(',', '\\').replace('，',
                                                                                                      '\\').replace(';',
                                                                                                                    '\\')
    phone = phone.strip('\\')

    phone_list = phone.split('\\')
    number_pattern = ur'^((\+|00)86)?([0-9-+]+)$'
    new_phone_list = []
    for item in phone_list:
        m = re.search(number_pattern, item)
        if m:
            new_number = m.group(3)
            if new_number:
                new_number = new_number.replace('+', '')
                new_phone_list.append(new_number)
    return new_phone_list


def re_process_number(phone):
    """
    正则表达式格式化号码
    :param phone: string,电话号码
    :return:返回一个号码的列表，列表的每一项是一个元组，(号码类型，格式化的号码，分机号)
    号码类型：mobile,fixed-no-areacode,fixed-areacode,short,800,400,wrong
    """
    phone_list = pre_process_number(phone)
    if not phone_list:
        return [('wrong', '', '')]
    new_list = []
    extension = ''
    for phone in phone_list:
        if re.match(ur'^1[3456789]\d{9}$', phone):
            type = 'mobile'
        else:
            # 将分机号解析出来，认为分机号是一位到四位
            # 只有座机才有分机号
            extension_pattern = ur'^(0)?(\d{2,3})-?(\d{7,8})(-\d{1,4})$'
            m_extension = re.search(extension_pattern, phone)
            if m_extension:
                extension = m_extension.group(4).strip('-')
                phone = m_extension.group(1) + m_extension.group(2) + m_extension.group(3)

            if re.match(ur'^800-?\d{3}-?\d{4}-?(\d{1,4})?$', phone):
                type = '800'
                phone = phone.replace('-', '')

            elif re.match(ur'^400-?\d{3}-?\d{4}-?(\d{1,4})?$', phone):
                type = '400'
                phone = phone.replace('-', '')

            elif re.match(ur'^(0)?(10|2[012345789]|[3-9]\d{2})-?[2-8]\d{6,7}$', phone):
                type = 'fixed-areacode'
                m = re.match(ur'^(0)?(10|2[012345789]|[3-9]\d{2})-?([2-8]\d{6,7})$', phone)
                phone = '0' + m.group(2) + m.group(3)

            elif re.match(ur'^[2-8]\d{6,7}$', phone):
                type = 'fixed-no-areacode'

            elif re.match(ur'^95[01345789]\d{2}$|^95[26]\d{3}$|^96\d{3,4}$', phone):
                type = 'short'

            elif re.match(ur'^95[017]\d{3,5}$|^952\d{4,5}$|^96\d{5,6}$', phone):
                type = 'short-extended'

            elif re.match(ur'^(0)?(10|2[012345789]|[3-9]\d{2})-?(95[01345789]\d{2}$|^95[26]\d{3}$|96\d{3,4})$',
                          phone):
                type = 'short-areacode'
                m = re.match(ur'^(0)?(10|2[012345789]|[3-9]\d{2})-?(95[01345789]\d{2}$|^95[26]\d{3}$|96\d{3,4})$',
                             phone)
                phone = '0' + m.group(2) + m.group(3)

            elif re.match(ur'^1[01]\d{3}$', phone):
                type = 'short'

            elif len(phone) in [3, 4] and phone in common_number_list:
                type = 'short'

            else:
                type = 'wrong'
                phone = phone
                extension = ''

        new_list.append((type, phone, extension))
    return new_list


def libphonenumber_parse_number(phone, country='CN'):
    phone_list = pre_process_number(phone)
    if not phone_list:
        return [('wrong', '', '')]
    new_list = []
    for phone, extension in phone_list:
        type = ''
        try:
            phone_obj = phonenumbers.parse(phone, country)
        except phonenumbers.phonenumberutil.NumberParseException:
            type = 'wrong'

        if not phonenumbers.is_possible_number(phone_obj):  # 更宽泛
            type = 'not possible'

        if not phonenumbers.is_valid_number(phone_obj):
            type = 'not valid'

        if not type:
            type = 'right'

        f_number = phonenumbers.format_number(phone_obj, phonenumbers.PhoneNumberFormat.E164)
        new_list.append((type, f_number, extension))
    return new_list


if __name__ == '__main__':
    number = '15620600082'
    # number = '0319-2356789'
    # number = '319-2356789'
    # number = '03192356789'
    # number = '(0319)-2346998'
    # number = '0830-8892040;0830-8892777'
    # number = '1562945-2360'
    # number = '800-820-8820'
    # number = '86-0951-8447039'
    number = '008610-95555'
    # number = '10010'
    # number = '8008009000-9809'
    # number = '+8695218299'
    number = '+0085296906934'
    res = re_process_number(number)
    print res
