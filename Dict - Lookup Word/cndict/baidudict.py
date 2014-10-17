#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
from utils import *


def lookup(word):
    params = {
        'client_id': 'Gh4UZOrtK9cUba2MW4SuTS3T',
        'q': word
    }
    if is_english(word):
        params['from'] = 'en'
        params['to'] = 'zh'
    else:
        params['from'] = 'zh'
        params['to'] = 'en'
    url = '{}?{}'.format('http://openapi.baidu.com/public/2.0/translate/dict/simple', urllib.urlencode(params))
    try:
        data = urllib.urlopen(url).read()
        data = convert(json.loads(data))
    except:
        raise DictLookupError('error to fetch data.')
    err_code = data.get('errno', -1)
    if err_code != 0:
        err_msg = data.get('errmsg', '')
        err_msg = err_msg.lower().replace('_', ' ') + '.' if err_msg != '' else 'unknown error.'
        raise DictLookupError(err_msg)
    result = []
    data = data.get('data', {})
    if data:
        symbol = data.get('symbols', [{}])[0]
        if is_english(word):
            for elem in symbol.get('parts', []):
                result.append('{} {}'.format(elem.get('part', ''), '；'.join(elem.get('means', []))))
            if result:
                phonetic = symbol.get('ph_am', '')
                result.insert(0, '{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
        else:
            elem = symbol.get('parts', [{}])[0]
            result.extend(elem.get('means', []))
            if result:
                phonetic = symbol.get('ph_zh', '')
                result.insert(0, '{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
    return result


def copy(word, item):
    shell_exec('printf {} | pbcopy', item, True)


def open(word):
    params = {
        'wd': word
    }
    url = '{}?{}'.format('http://dict.baidu.com/s', urllib.urlencode(params))
    shell_exec('open {}', url)


def say(word):
    shell_exec('say {}', word)
