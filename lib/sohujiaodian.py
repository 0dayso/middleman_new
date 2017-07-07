#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/22 14:52
# @Author  : lichenxiao

import sys
import logging
from lxml import html

from conf.settings import get_log_path
from utils import get_xpath_content, record_res
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
    # open('a.html', 'wb').write(page_obj.text)
    if not page_obj.text:
        return [], None
    page_tree = html.document_fromstring(page_obj.text)
    page_tree.make_links_absolute(origin_url)

    dom_xpath = ur"//li[@class='items']"
    name_xpath = ur".//h2/a[@class='link']/text()"
    number_xpath = ur"./span[@class='items_r']/em/text()"
    company_xpath = ur"./div[@class='items_m']/p[1]/text()"

    dom_list = page_tree.xpath(dom_xpath)

    for dom_item in dom_list:
        name_list = dom_item.xpath(name_xpath)
        number_list = dom_item.xpath(number_xpath)
        company_list = dom_item.xpath(company_xpath)
        if name_list and number_list:
            name = ''.join(name_list[0].strip().split())
            number = ''.join(number_list[0].strip().split())
            if company_list:
                company = ''.join(company_list[0].lstrip('所属公司：').strip().split())
            else:
                company = ''
            page_res_list.append((name, number, company))
    next_page_xpath = ur"//div[@class='pages clearfix']//li[@class='next']/a/@href"
    next_page_url = page_tree.xpath(next_page_xpath)
    return page_res_list, next_page_url


def crawl(middleman_type):
    origin_url = "http://house.focus.cn/"
    city_xpath = ur"//div[@id='cityArea']/div[@class='bot']//div[@class='cityAreaBoxCen']//a/@href"
    # 获取城市url列表
    page_obj = get(origin_url, use_proxy=False)
    city_url_list = get_xpath_content(origin_url, page_obj.text, city_xpath)
    if not city_url_list:
        logging.warning('%s: No city url!' % (middleman_type))
        return None
    # city_url_list = ["http://beijing.anjuke.com/tycoon/"]

    for city_url in city_url_list:
        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        # 经纪人的url
        url_list = city_url.split('.')
        start_page_url = url_list[0] + ".esf.focus.cn/agent"
        page_url = url_list[0] + ".esf.focus.cn/agent"

        while page_url:
            logging.warning("%s: Get list page url, url: %s" % (middleman_type, page_url))
            page_obj = get(page_url, use_proxy=False)
            if not page_obj:
                break
            page_res_list, next_page_url = parse_page(start_page_url, page_obj)
            print 'next', next_page_url
            if next_page_url:
                page_url = next_page_url[0]
            else:
                page_url = None
            res = record_res(page_res_list, middleman_type)
            if not res:
                logging.error("%s: Cannot record res, url: %s" % (middleman_type, page_url))
                # break


if __name__ == '__main__':
    middleman_type = 'sohujiaodian'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
