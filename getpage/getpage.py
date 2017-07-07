#!/usr/bin/env python2
# -*- coding: utf-8 -*- 

import requests
import random
import logging

from time import time
from traceback import format_exc
from utils import *
from page import page_from_resp, Page
from proxy import get_proxies, report_proxy_status

LOG = logging.getLogger(__name__)


def _get_page(url, retry=3, proxies=None, fpfirst=False):
    '''
    Get the page directly or via given proxy.

    This is where getting page actually happens. All entries finally converge to his single point.
    Note: only http schema is currently supported.
    '''
    start_time = time()
    assert proxies is None or type(proxies) is dict
    if proxies:
        LOG.info('Trying to get page %s via proxy %s.' % (url, proxies['http']))
    else:
        LOG.info('Trying to get page %s via direct connection.' % url)

    schema = url.split(':')[0]
    if schema == url:
        LOG.warning('URL schema missing. Assuming HTTP.')
        url = 'http://' + url
    elif schema not in ('http',):  # 'https', 'ftp'):
        LOG.error('URL schema "%s" not supported. Returning nothing.' % schema)
        return None

    for i in range(retry):
        wait_b4_try(i, factor=3)
        try_start_time = time()
        resp = None
        try:
            session = requests.Session()
            rargs = req_args()
            rargs['proxies'] = proxies
            # some sites needs cookies from the frontpage
            if fpfirst:
                urlsplit = url.split('/')
                if len(urlsplit) > 3 and urlsplit[3] != '':
                    fpurl = urlsplit[0] + '//' + urlsplit[2]
                    resp = session.get(fpurl, **rargs)
                    # sleep some random time before requesting again
                    sleep(random.uniform(2, 4))
            resp = session.get(url, **rargs)
        except requests.exceptions.ProxyError, e:
            LOG.debug(format_exc())
            if proxies and proxies['http']:
                LOG.warning('Proxy error while getting page %s. Proxies: %s' % (url, str(proxies)))
                report_proxy_status(proxies['http'], False)
            continue
        except (requests.exceptions.Timeout, requests.exceptions.ConnectTimeout), e:
            LOG.debug(format_exc())
            if proxies and proxies['http']:
                LOG.warning('Proxies timed out: %s' % str(proxies))
                report_proxy_status(proxies['http'], False)
            else:
                LOG.warning('Direct connection timed out.')
            continue
        except requests.exceptions.ConnectionError, e:
            LOG.debug(format_exc())
            LOG.warning('Failed to get page. ConnectionError.')
            if proxies and proxies['http']:
                report_proxy_status(proxies['http'], is_valid=False)
            continue
        except Exception, e:
            LOG.debug(format_exc())
            continue

        try:
            if proxies and proxies['http']:
                report_proxy_status(proxies['http'], is_valid=True)
        except:
            LOG.debug(format_exc())
            LOG.warning('Failed to report proxy %s as valid.' % proxies['http'])

        if resp.status_code != 200:
            LOG.warning('Got response with status code %d while getting page %s.' % (resp.status_code, url))
            LOG.debug(resp.text)
            continue
        # requests automatically decompresses gzip-encoded responses
        # so we're good
        elapsed = time() - try_start_time
        LOG.info('Successfully got page %s. Tried %d time(s) in %gs.' % (url, i + 1, elapsed))
        p = page_from_resp(resp)
        p.elapsed = elapsed
        p.proxy = proxies and proxies['http'] or None
        return p
    LOG.warning('All %d attempt(s) to get page failed in %gs. Returning nothing.' % (retry, time() - start_time))
    return None


def _get_page_via_proxy(url, retry=3, proxies=None, fpfirst=False):
    '''
    Get the page via given proxy server.
    '''
    start_time = time()
    for i in range(retry):
        if proxies:
            wait_b4_try(i, factor=3)
            x = proxies
        else:
            x = get_proxies()
        if x:
            # each proxy server is tried once only
            # if anything goes wrong, we'll get another one
            # so it'd better grasp the only chance it'll have
            p = _get_page(url, retry=1, proxies=x, fpfirst=fpfirst)
            if p:
                return p
        else:
            LOG.warning('No valid proxy to get page. Continuing.')
    LOG.warning(
        'All %d attempt(s) to get page via proxy failed in %s. Returning nothing.' % (retry, time() - start_time))
    return None


def get(url, retry=3, fpfirst=False, use_proxy=True, render_js=False):
    """
    Download a web page via proxy and return as unicode string.

    A proxy server is automatically retrieved from server
    and used, unless use_proxy is set to False, where the page
    will be fetched directly. The proxy status is reported back
    to server after each successful or failed use.

    Note: JavaScript renderer is not currently supported.
    """
    print url
    if render_js:
        LOG.error('JavaScript renderding not supported yet asked for.')
    if use_proxy:
        return _get_page_via_proxy(url, retry=retry, fpfirst=fpfirst)
    else:
        return _get_page(url, retry=retry, fpfirst=fpfirst)


if __name__ == '__main__':
    # LOG.addHandler(logging.StreamHandler())
    # logging.basicConfig(level=logging.INFO)
    # p = get('http://cnbeta.com', use_proxy=False)
    # if p:
    #     print 'url', p.url
    #     print 'encoding', p.encoding
    #     print 'text', p.text[:1000]
    #     print 'elapsed', p.elapsed
    # else:
    #     print 'None'

    res = get(url = "http://www.cnlinfo.net/jixie/",use_proxy=False)
    f = open('a.html','wb')
    print res
    f.write(res.content)
