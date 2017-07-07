#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/22 14:51
# @Author  : lichenxiao

import sys
import logging
from lxml import html
import time
import re

from conf.settings import get_log_path
from utils import get_xpath_content, record_res
from getpage import get

reload(sys)
sys.setdefaultencoding('utf-8')


def parse_page(origin_url, page_obj, first_page_url):
    """
    获取经纪人的电话
    :param origin_url:
    :param page_obj:
    :return:
    """
    page_res_list = []

    page_tree = html.document_fromstring(page_obj.text)
    page_tree.make_links_absolute(origin_url)

    dom_xpath = ur"//div[@class='hoverBg clearfix']"
    name_xpath = ur".//div[@class='fl h_info']/h3/a/text()"
    number_xpath = ur".//div[@class='fr tel']/text()"
    company_xpath = ur".//div[@class='clearfix mag_r']//span[@class='com']/text()"

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

    next_xpath = ur"//div[@class='page']/div[@id='page_d']/a[contains(text(),'下一页')]/@href"
    next_page_url = page_tree.xpath(next_xpath)
    next_page_url_list = []
    if next_page_url:
        m = re.search(ur"^javascript:show_broker\('(\d+)'\);$", next_page_url[0])
        if m:
            next_page_number = m.group(1)
            next_page_url = '.'.join(first_page_url.split('.')[0:-1])
            next_page_url += "/p" + next_page_number + '.html'
        else:
            next_page_url = []
    if type(next_page_url) != list:
        next_page_url_list.append(next_page_url)
        return page_res_list, next_page_url_list
    else:
        return page_res_list, next_page_url

def crawl(middleman_type):
    origin_url = "http://shijiazhuang.tuitui99.com/"
    city_xpath = ur"//div[@class='city_more']//a/@href"
    # 获取城市url列表
    page_obj = get(origin_url, use_proxy=False)
    city_url_list = get_xpath_content(origin_url, page_obj.text, city_xpath)
    if not city_url_list:
        logging.warning('%s: No city url!' % (middleman_type))
        return None
    # city_url_list = ["http://beijing.anjuke.com/tycoon/"]

    for city_url in city_url_list:
        logging.warning("%s: City page url, url: %s" % (middleman_type, city_url))
        city_url = city_url.rstrip("/")
        city_broker_url = city_url + "/broker"

        logging.warning("%s: Get city page url, url: %s" % (middleman_type, city_broker_url))
        time.sleep(2)
        city_broker_page_obj = get(city_broker_url, use_proxy=False)

        area_xpath = ur"//dl[@class='clearfix']/dd/a[position()>1]/@href"
        detail_xpath = ur"//dd[@class='sub_area']/a[position()>1]/@href"

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
                # print 'detail_url', detail_address_url
                first_detail_address_url = detail_address_url
                while detail_address_url:
                    logging.warning("%s: Get list page url, url: %s" % (middleman_type, detail_address_url))
                    time.sleep(2)
                    detail_page_obj = get(detail_address_url, use_proxy=False)
                    page_res_list, next_page_url = parse_page(city_url, detail_page_obj, first_detail_address_url)
                    if next_page_url:
                        detail_address_url = next_page_url[0]
                    else:
                        detail_address_url = None
                    # print 'next', detail_address_url
                    res = record_res(page_res_list, middleman_type)
                    if not res:
                        logging.error("%s: Cannot record res, url: %s" % (middleman_type, detail_address_url))
                        # break


if __name__ == '__main__':
    middleman_type = 'tuitui99'
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=get_log_path(middleman_type),
                        filemode='w')
    crawl(middleman_type)
