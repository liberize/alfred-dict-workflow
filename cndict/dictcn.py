#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import gzip
import re
import StringIO
from utils import *


def lookup(word, wap_page=False, *args):
    if wap_page:
        params = {'q': word}
        url = '{}?{}'.format('http://3g.dict.cn/s.php', urllib.urlencode(params))
    else:
        url = 'http://dict.cn/{}'.format(urllib.quote(word))
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

    if wap_page:
        match = re.search(r'<h1>.*?</h1>\s*<div class="phonetic">{}</div>{}'.format(
                          r'\s*<span>英 <bdo>\[.*?\]</bdo>.*?</span>\s*<span>美 <bdo>\[(.*?)\]</bdo>.*?</span>\s*'
                          if is_eng else
                          r'\[(.*?)\]',
                          r'\s*<div class="exp">(.*?)</div>'
                          if is_eng else
                          r''), data, re.S)
        if match:
            phonetic = match.group(1)
            result.append('{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
            if is_eng:
                definition = match.group(2)
                for match in re.finditer(r'<span>(.*?)</span>(.*?)<br/>', definition):
                    result.append('{} {}'.format(match.group(1), match.group(2)))
    else:
        match = re.search(r'<div class="phonetic">{}</div>'.format(
                          r'\s*<span>\s*英.*?\[.*?\].*?</span>\s*<span>\s*美.*?\[(.*?)\].*?</span>\s*'
                          if is_eng else
                          r'\s*<span>\s*\[(.*?)\]\s*</span>\s*'), data, re.S)
        phonetic = match.group(1) if match else ''
        result.append('{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))

        match = re.search(r'<div class="layout {}">(.*?)</div>'.format(
                          r'detail' if is_eng else r'cn'), data, re.S)
        if match is None:
            if is_eng:
                # no detailed definition, try basic
                match = re.search(r'<ul class="dict-basic-ul">(.*?)</ul>', data, re.S)
                if match:
                    for item in re.finditer(r'<li>\s*<span>(.*?)</span>\s*<strong>(.*?)</strong>\s*</li>', match.group(1), re.S):
                        result.append('{} {}'.format(item.group(1), item.group(2)))
        else:
            definition = match.group(1)
            if is_eng:
                for match in re.finditer(r'<span>(.*?)<bdo>.*?</bdo>\s*</span>\s*<ol .*?>(.*?)</ol>', definition, re.S):
                    part = match.group(1).strip()
                    for item in re.finditer(r'<li>(.*?)</li>', match.group(2)):
                        result.append('{} {}'.format(part, item.group(1)))
            else:
                match = re.search(r'<ul .*?>(.*?)</ul>', definition, re.S)
                if match:
                    for item in re.finditer(r'<li>\s*<a .*?>(.*?)</a>\s*</li>', match.group(1), re.S):
                        result.append(item.group(1).strip())

        # no definition and no phonetic, return empty list
        if not phonetic and len(result) == 1:
            result = []
    return result


def extract(word, item):
    if not is_english(word):
        match = re.match(r'[a-z]+\. (.+)', item)
        if match:
            return match.group(1)


def get_url(word):
    return 'http://dict.cn/{}'.format(urllib.quote(word))
