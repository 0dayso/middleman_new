#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from time import time
from chardet import detect
from utils import guess_response_encoding as guess_enc

def page_from_resp(resp, encoding = None):
    '''
    Convert :class:`requests.Responce` to a :class:`Page` object.
    '''
    enc = encoding or guess_enc(resp)
    return Page(resp.request.url, resp.content, enc, resp.elapsed)

class Page(object):
    '''
    The :class:`Page <Page>` object, which contains the
    contents of a requested page.
    '''
    def __init__(
        self,
        url,
        content,
        encoding = None,
        proxy = '',
        elapsed = 0,
        timestamp = 0,
        pageid = 0):

        super(Page, self).__init__()
        self.url = url
        self.content = content
        self.encoding = encoding
        self.elapsed = elapsed
        self.timestamp = timestamp or time()

    @property
    def text(self):
        if not self.content:
            return u''
        enc = self.encoding or detect(self.content)['encoding']
        try:
            text = self.content.decode(enc, errors='replace')
        except (LookupError, TypeError):
            text = self.content.decode('latin1', errors='replace')
        return text

if __name__ == '__main__':
    import requests
    r = requests.get('http://cnbeta.com')
    print page_from_resp(r)
