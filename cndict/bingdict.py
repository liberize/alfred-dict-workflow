#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import gzip
import re
import StringIO
from utils import *


def lookup(word):
    params = {
        'q': word
    }
    url = '{}?{}'.format('http://www.bing.com/dict/search', urllib.urlencode(params))
    try:
        request = urllib2.Request(url)
        request.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(request)
        data = response.read()
    except:
        raise DictLookupError('error to fetch data.')

    if response.info().get('Content-Encoding') == 'gzip':
        gzip_file = gzip.GzipFile(fileobj=StringIO.StringIO(data))
        data = gzip_file.read()

    # no need to use BeautifulSoup, just extract definition from meta tag
    matches = re.search(r'<meta name="description" content="([^<>]*)"/>', data)
    if matches is None:
        raise DictLookupError('failed to find meta tag.')
    description = matches.group(1)

    result = []
    matches = re.match(r'^必应词典为您提供.*的释义，美\[([^\[\]]*)\](，英\[[^\[\]]*\])?，(.*)； 网络释义： .*； $', description)
    if matches:
        phonetic = matches.group(1)
        result.append('{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
        items = matches.group(3)
        for item in items.split('； '):
            if item != '':
                result.append(item)
    return result
