#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/22 14:52
# @Author  : lichenxiao

import sys
import logging
from lxml import html
import time
import re

from conf.settings import get_log_path
from lib.utils import get_xpath_content, record_res
from getpage import get

reload(sys)
sys.setdefaultencoding('utf-8')


def parse_page(origin_url, page_obj, ):
    """
    获取经纪人的电话
    :param origin_url:
    :param page_obj:
    :return:
    """
    page_res_list = []

    page_tree = html.document_fromstring(page_obj.text)
    page_tree.make_links_absolute(origin_url)

    dom_xpath = ur"//dl[@class='agentinfo clearfix']"

    name_xpath = ur".//p[@class='font18 bold mt10']/a/text()"
    number_xpath = ur".//div[@class='tel-num']/text()"
    company_xpath = ur".//p[@class='mt10']/text()"

    dom_list = page_tree.xpath(dom_xpath)

    for dom_item in dom_list:
        name_list = dom_item.xpath(name_xpath)
        number_list = dom_item.xpath(number_xpath)
        company_list = dom_item.xpath(company_xpath)
        if name_list and number_list:
            name = ''.join(name_list[0].strip().split())
            number = ''.join(number_list[0].strip().split())
            company = ''.join(company_list[0].strip().split())
            page_res_list.append((name, number, company))
            print name, number, company

    next_page_xpath = ur"//a[@id='hlk_next']/@href"
    next_page_url = page_tree.xpath(next_page_xpath)
    return page_res_list, next_page_url


def crawl(middleman_type):
    origin_url = "http://fang.com/SoufunFamily.htm"
    city_xpath = "//div[@class='letterSelt']/div[@id='c01']//a/@href"
    # 获取城市url列表
    time.sleep(2)
    origin_page_obj = get(origin_url, use_proxy=False)
    if not origin_page_obj:
        logging.warning('%s: Cannot get page. url: %s' % (middleman_type, origin_url))
        return
    city_url_list = get_xpath_content(origin_url, origin_page_obj.text, city_xpath)
    if not city_url_list:
        logging.warning('%s: No city url.' % (middleman_type))
        return None

    # city_url_list = ["http://bj.fang.com/"]
    area_xpath = ur"//div[@class='qxName']/a[position()>1]/@href"
    detail_xpath = ur"//p[@id='shangQuancontain']/a[position()>1]/@href"

    for city_url in city_url_list:
        # print 'city',city_url
        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        if city_url == "http://bj.fang.com/":
            city_broker_url = "http://esf.fang.com"
        else:
            re_pattern = ur"^http://(\w+)\.fang\.com/$"
            m = re.search(re_pattern, city_url)
            if m:
                city_abbr = m.group(1)
                city_broker_url = "http://esf." + city_abbr + ".fang.com"

            else:
                continue
        city_broker_url_first = city_broker_url + '/agenthome/'
        logging.warning("%s: Get city page url, url: %s" % (middleman_type, city_broker_url_first))
        time.sleep(2)
        city_broker_page_obj = get(city_broker_url_first, use_proxy=False)
        if not city_broker_page_obj:
            logging.warning('%s: Cannot get page. url: %s' % (middleman_type, city_broker_url_first))
            continue
        area_url_list = get_xpath_content(city_broker_url, city_broker_page_obj.text, area_xpath)
        if not area_url_list:
            logging.warning('%s: No area broker url, info: %s' % (middleman_type, city_broker_url_first))
            continue

        # 获取具体地点的url列表
        # area_url_list = ["http://esf.fang.com/agenthome-a03/-i31-j310/"]
        for area_url in area_url_list:
            # print 'area_url', area_url
            logging.warning("%s: Get area page url, url: %s" % (middleman_type, area_url))
            time.sleep(2)
            area_page_obj = get(area_url, use_proxy=False)
            if not area_page_obj:
                logging.warning('%s: Cannot get page. url: %s' % (middleman_type, area_url))
                continue
            detail_address_broker_list = get_xpath_content(city_broker_url, area_page_obj.text, detail_xpath)
            if not detail_address_broker_list:
                logging.warning('%s: No detail address broker url, info: %s' % (middleman_type, area_url))
                continue

            # # 记录
            # detail_address_broker_list = ['http://esf.fang.com/agenthome-a03-b012384/-i31-j310/']
            for detail_address_url in detail_address_broker_list:
                # print 'detail_url', detail_address_url
                while detail_address_url:
                    logging.warning("%s: Get list page url, url: %s" % (middleman_type, detail_address_url))
                    time.sleep(2)
                    detail_page_obj = get(detail_address_url, use_proxy=False)
                    if not detail_page_obj:
                        logging.warning('%s: Cannot get page. url: %s' % (middleman_type, detail_address_url))
                        detail_address_url = None
                        continue
                    page_res_list, next_page_url = parse_page(city_broker_url, detail_page_obj)
                    if next_page_url:
                        detail_address_url = next_page_url[0]
                    else:
                        detail_address_url = None
                    # print 'next', detail_address_url
                    res = record_res(page_res_list, middleman_type)
                    if not res:
                        logging.error("%s: Cannot record res, url: %s" % (middleman_type, detail_address_url))
                        # exit()


if __name__ == '__main__':
    middleman_type = 'fangtianxia'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
