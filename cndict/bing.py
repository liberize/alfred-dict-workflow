#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import gzip
import re
import StringIO
from utils import *


def lookup(word, *args):
    params = {'q': word, 'mkt': 'zh-cn'}
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

    result = []
    is_eng = is_english(word)

    # no need to use BeautifulSoup, just extract definition from meta tag
    match = re.search(r'<meta name="description" content="(.*?)" />', data)
    if match is None:
        raise DictLookupError('failed to find meta tag.')
    description = match.group(1)

    match = re.match(r'^必应词典为您提供.*?的释义{}，(.*?)； 网络释义：.*$'.format(
                     r'(，美\[(.*?)\])?(，英\[(.*?)\])?'
                     if is_eng else
                     r'，拼音\[(.*)\]'), description)
    if match:
        phonetic = (match.group(2) or match.group(4)) if is_eng else match.group(1)
        result.append('{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
        items = match.group(5 if is_eng else 2).split('； ')
        if is_eng:
            for item in items:
                if item != '':
                    result.append(item)
        else:
            for item in items:
                match = re.match(r'([a-z]+\.) (.+)', item)
                if match:
                    part = match.group(1)
                    for new_item in match.group(2).split('; '):
                        result.append('{} {}'.format(part, new_item))
    return result


def extract(word, item):
    if not is_english(word):
        match = re.match(r'[a-z]+\. (.+)', item)
        if match:
            return match.group(1)


def get_url(word):
    params = {'q': word}
    return '{}?{}'.format('http://www.bing.com/dict/search', urllib.urlencode(params))
