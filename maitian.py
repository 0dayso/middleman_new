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

    dom_xpath = ur"//li[@class='clearfix']"
    name_xpath = ur".//div[@class='fl sale_points_author']/h6/a/text()"
    number_xpath = ur".//label[@id='clickMobileTJ']/@onclick"
    #company_xpath = ur".//p[@class='jjr-desc mg-top']/a[1]/text()"
    company = '麦田'
    dom_list = page_tree.xpath(dom_xpath)

    for dom_item in dom_list:
        name_list = dom_item.xpath(name_xpath)
        number_list = dom_item.xpath(number_xpath)
        #company_list = dom_item.xpath(company_xpath)
        if name_list and number_list:
            name = ''.join(name_list[0].strip().split())
            number = ''.join(number_list[0].split("'")[1].strip())
            page_res_list.append((name, number, company))

    next_page_xpath = ur"//div[@id='paging']/a[contains(text(),'下一页')]/@href"
    next_page_url = page_tree.xpath(next_page_xpath)
    return page_res_list, next_page_url


def crawl(middleman_type):
    city_url_list = ["http://bj.maitian.cn/bkesf",
                     "http://fz.maitian.cn/bkesf",
                     "http://xm.maitian.cn/bkesf"]
    # city_url_list = ["http://beijing.anjuke.com/tycoon/"]

    for city_url in city_url_list:
        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        page_url = city_url
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
    middleman_type = 'maitian'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
