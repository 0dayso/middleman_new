#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/22 14:52
# @Author  : lichenxiao

import sys
import logging
from lxml import html
import time

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
    company = '我爱我家'

    if 'tj.5i5j' in origin_url:
        dom_xpath = ur"//ul[@class='agentlist']"
        name_xpath = ur".//ul/li[@class='agentname']/em/a/text()"
        number_xpath = ur"./li[@class='phoneno']/p/text()"
    else:
        dom_xpath = ur"//div[@class='zhiye_content']"
        name_xpath = ur".//div[@class='conts_left']/span/text()"
        number_xpath = ur".//div[@class='conts_left']/b/text()"

    dom_list = page_tree.xpath(dom_xpath)

    for dom_item in dom_list:
        name_list = dom_item.xpath(name_xpath)
        number_list = dom_item.xpath(number_xpath)

        if name_list and number_list:
            name = ''.join(name_list[0].strip().split())
            number = ''.join(number_list[0].strip().split())
            page_res_list.append((name, number, company))

    next_page_url = page_tree.xpath(ur"//div[@class='rent-page']/a[contains(text(),'下一页')]/@href")
    return page_res_list, next_page_url


def crawl(middleman_type):

    origin_url = "http://bj.5i5j.com/"
    city_xpath = "//div[@class='new_city_more']//a/@href"
    # 获取城市url列表
    time.sleep(2)
    origin_page_obj = get(origin_url, use_proxy=False)
    city_url_list = get_xpath_content(origin_url, origin_page_obj.text, city_xpath)
    if not city_url_list:
        logging.warning('%s: No city url.' % (middleman_type))
        return None

    # city_url_list = ["http://bj.5i5j.com/"]

    for city_url in city_url_list:

        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        city_url = city_url.rstrip("/")
        city_broker_url = city_url + "/broker"

        logging.warning("%s: Get city page url, url: %s" % (middleman_type, city_broker_url))
        time.sleep(2)
        city_broker_page_obj = get(city_broker_url, use_proxy=False)

        if "tj.5i5j" in city_url:
            area_xpath = ur"//ul[@class='search-quyu']/li[1]/a[position()>1]/@href"
            detail_xpath = ur"//li[@class='addressli']/div[@class='shquan quanm']/span/a/@href"
        else:
            area_xpath = ur"//li[@class='quyu_gao']//a[position()>1]/@href"
            detail_xpath = ur"//div[@class='keywords01']/a/@href"

        area_url_list = get_xpath_content(city_url, city_broker_page_obj.text, area_xpath)
        if not area_url_list:
            logging.warning('%s: No area broker url, info: %s' % (middleman_type, city_broker_url))
            continue

        # 获取具体地点的url列表
        # area_url_list = ["http://bj.5i5j.com/broker/haidian/"]
        for area_url in area_url_list:
            logging.warning("%s: Get area page url, url: %s" % (middleman_type, area_url))
            time.sleep(2)
            area_page_obj = get(area_url, use_proxy=False)
            detail_address_broker_list = get_xpath_content(city_url, area_page_obj.text, detail_xpath)
            if not detail_address_broker_list:
                logging.warning('%s: No detail address broker url, info: %s' % (middleman_type, area_url))
                continue

            # # 记录
            for detail_address_url in detail_address_broker_list:
                #print 'detail_url', detail_address_url
                while detail_address_url:
                    logging.warning("%s: Get list page url, url: %s" % (middleman_type, detail_address_url))
                    time.sleep(2)
                    detail_page_obj = get(detail_address_url, use_proxy=False)
                    page_res_list, next_page_url = parse_page(city_url, detail_page_obj)
                    if next_page_url:
                        detail_address_url = next_page_url[0]
                    else:
                        detail_address_url = None
                    #print 'next', detail_address_url
                    res = record_res(page_res_list, middleman_type)
                    if not res:
                        logging.error("%s: Cannot record res, url: %s" % (middleman_type, detail_address_url))


if __name__ == '__main__':
    middleman_type = 'woaiwojia'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
