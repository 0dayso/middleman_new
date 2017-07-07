#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import logging
import random
from time import sleep, clock
from chardet import detect
from re import search

LOG = logging.getLogger(__name__)
BASE_RETRY_INTERVAL = 1 # second(s)
REQUEST_TIMEOUT = 30 # second(s)

def random_agent():
    REAL_WORLD_AGENTS = (
        # Linux
        '5.0 (X11; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0',
        '5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
        # Mac
        '5.0 (Macintosh; Intel Mac OS X 10.9; rv:29.0) Gecko/20100101 Firefox/29.0',
        '5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
        'Mac / Safari 7: 5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
        # Windows
        '5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0',
        '5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36',
        '4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
        '4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        '4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0)',
        '5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
        '5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
        '5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        # Android
        '5.0 (Android; Mobile; rv:29.0) Gecko/29.0 Firefox/29.0',
        '5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36',
        # iOS
        '5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) CriOS/34.0.1847.18 Mobile/11B554a Safari/9537.53',
        '5.0 (iPad; CPU OS 7_0_4 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11B554a Safari/9537.53', )
    return 'Mozilla/' + random.choice(REAL_WORLD_AGENTS)

def req_args():
    '''
    Build request arguments as kwargs for requests.get
    '''
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': random_agent(),
        #connection
        #cache control
        #pragma
    }
    return {'timeout': REQUEST_TIMEOUT, 'headers': headers}

def guess_response_encoding(resp):
    '''
    Guess the content encoding of a requests response.

    Note: there's a performance issue due to chardet.
    '''
    # first try guessing the encoding using chardet
    # this should work in most cases
    start = clock()
    g = detect(resp.content)
    if g['confidence'] > 0.9:
        LOG.info('Detected encoding %s with cofidence of %g in %gs.' % (g['encoding'], g['confidence'], clock() - start))
        return g['encoding']
    # let's see if http response has the encoding info
    # if that doesn't work, sometimes the page tells us its encoding
    # but it's least accurate
    ct = ''
    if 'charset=' in resp.headers.get('content-type', ''):
        # assuming charset is the last element
        ct = resp.headers['content-type']
    else:
        m = search('<meta http-equiv="Content-Type".*?>', resp.content)
        if m:
            ct = m.group()
    if ct:
        m = search('charset=([^; "]*)', ct)
        if m and len(m.groups()) > 0: # is this implied?
            LOG.info('Detected encoding %s using HTTP headers or html-quiv.' % m.groups()[0])
            return m.groups()[0]
    LOG.warning('Encoding detection failed. Returning empty str.')
    return ''

def wait_b4_try(num_tried, factor = 1):
    '''
    Wait befor trying, ONLY if needed.

    Waiting time is determied by number of previous attempts -
    it DOUBLES with every attempt you've made.
    Of course we won't wait on the first try.
    '''
    if num_tried:
        t = 2 ** (num_tried - 1) * BASE_RETRY_INTERVAL
        LOG.info('Sleeping for %f seconds' % t)
        sleep(t * factor)

if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)
    wait_b4_try(1, 0.1)
    print random_agent()

    wait_b4_try(2, 0.1)
    print req_args()

    import requests
    wait_b4_try(3, 0.1)
    r = requests.get('http://cnbeta.com')
    print guess_response_encoding(r)
