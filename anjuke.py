#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/22 14:52
# @Author  : lichenxiao

import sys
import logging
from lxml import html

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

    dom_xpath = ur"//div[@class='jjr-itemmod']"
    name_xpath = ur".//div[@class='jjr-title']/h3/a/text()"
    number_xpath = ur".//div[@class='jjr-side']/text()"
    company_xpath = ur".//p[@class='jjr-desc mg-top']/a[1]/text()"

    dom_list = page_tree.xpath(dom_xpath)

    for dom_item in dom_list:
        name_list = dom_item.xpath(name_xpath)
        number_list = dom_item.xpath(number_xpath)
        company_list = dom_item.xpath(company_xpath)
        if name_list and number_list:
            name = ''.join(name_list[0].strip().split())
            number = ''.join(number_list[1].strip().split())
            if company_list:
                company = ''.join(company_list[0].strip().split())
            else:
                company = ''
            page_res_list.append((name, number, company))
    next_page_xpath = ur"//a[@class='aNxt']/@href"
    next_page_url = page_tree.xpath(next_page_xpath)
    return page_res_list, next_page_url


def crawl(middleman_type):
    origin_url = "http://www.anjuke.com/sy-city.html"
    city_xpath = ur"//div[@class='city_list']/a/@href"
    # 获取城市url列表
    page_obj = get(origin_url, use_proxy=False)
    if not page_obj:
        logging.warning('%s: Cannot get page. url: %s' % (middleman_type, origin_url))
        return
    city_url_list = get_xpath_content(origin_url, page_obj.text, city_xpath)
    if not city_url_list:
        logging.warning('%s: No city url!' % (middleman_type))
        return None
    # city_url_list = ["http://beijing.anjuke.com/tycoon/"]

    for city_url in city_url_list:
        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        city_url = city_url.rstrip("/")
        # 经纪人的url
        page_url = city_url + "/tycoon/"
        while page_url:
            logging.warning("%s: Get list page url, url: %s" % (middleman_type, page_url))
            page_obj = get(page_url, use_proxy=False)
            if not page_obj:
                logging.warning('%s: Cannot get page. url: %s' % (middleman_type, page_url))
                page_url = None
                continue
            page_res_list, next_page_url = parse_page(city_url, page_obj)
            if next_page_url:
                page_url = next_page_url[0]
            else:
                page_url = None
            res = record_res(page_res_list, middleman_type)
            if not res:
                logging.error("%s: Cannot record res, url: %s" % (middleman_type, page_url))
            # break


if __name__ == '__main__':
    middleman_type = 'anjuke'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
