#!/usr/bin/env python
# coding: utf-8

import requests
from lxml import etree
import time
import urlparse
import sys, traceback
from requests.exceptions import ConnectTimeout, ConnectionError, ReadTimeout

Headers = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
}

SESSION = requests.session()


def retry(trytimes):
    def deco(func):
        def wrapper(*args, **kwargs):
            att = 0
            while att < trytimes:
                try:
                    return func(*args, **kwargs)
                except (ConnectTimeout, ConnectionError, ReadTimeout):
                    time.sleep(15)
                    att += 1
                except:
                    att += 1
                    print >> sys.stderr, traceback.format_exc(), args

        return wrapper

    return deco


@retry(3)
def request(method, url, **kwargs):
    kwargs.setdefault('timeout', 10)
    kwargs.setdefault('headers', Headers)
    r = SESSION.request(method, url, **kwargs)
    if urlparse.urlparse(url).netloc in ['']:
        r.encoding = 'utf-8'
    r.xpath = etree.HTML(r.text).xpath
    return r
