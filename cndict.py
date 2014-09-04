#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import json
import os
import subprocess


class DictLookupError(Exception):
    pass


def is_english(word):
    for i in word:
        if ord(i) > 127:
            return False
    return True


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def system_lookup(word, exe='./dict'):
    # works for '朗道英汉/汉英词典5.0' only
    if os.path.isfile(exe) and os.access(exe, os.X_OK):
        dict_file = 'langdao-ec-gb.dictionary' if is_english(word) else 'langdao-ce-gb.dictionary'
        dict_path = os.path.expanduser('~/Library/Dictionaries/{}'.format(dict_file))
        proc = subprocess.Popen([exe, dict_path, word], stdout=subprocess.PIPE)
        definition = proc.stdout.read()
        if definition == '(null)\n':
            return []
    else:
        from DictionaryServices import DCSCopyTextDefinition
        unicode_word = word.decode('utf-8')
        word_range = (0, len(unicode_word))
        definition = DCSCopyTextDefinition(None, unicode_word, word_range)
        if definition is None:
            return []
        definition = definition.encode('utf-8')

    definition = definition.split('\n相关词组:\n')[0]
    result = definition.split('\n')
    if is_english(word):
        if result[1].startswith('*['):
            phonetic = result[1][2:-1]
            result[0:2] = ['{} {}'.format(word, '/{}/'.format(phonetic) if phonetic else '')]
    else:
        result[1:2] = result[1].split('; ')
    return result


def youdao_lookup(word):
    params = {
        'keyfrom': 'awf-Chinese-Dict',
        'key': '19965805',
        'version': '1.1',
        'type': 'data',
        'doctype': 'json',
        'q': word
    }
    url = '{}?{}'.format('http://fanyi.youdao.com/openapi.do', urllib.urlencode(params))
    try:
        data = urllib.urlopen(url).read()
        data = convert(json.loads(data))
    except:
        raise DictLookupError('error to fetch data.')
    err_code = data.get('errorCode', -1)
    if err_code != 0:
        err_msg = {
            20: 'word is too long.',
            30: 'unable to translate.',
            40: 'language is not supported.',
            50: 'key is invalid.'
        }
        raise DictLookupError(err_msg.get(err_code, 'unkown error.'))
    result = []
    basic = data.get('basic', {})
    if basic:
        if is_english(word):
            result.extend(basic.get('explains', []))
        else:
            for explain in basic.get('explains', []):
                pos = explain.rfind(']')
                result.append(explain[pos+1:] if pos >= 0 else explain)
        if result:
            phonetic = basic.get('phonetic', '')
            result.insert(0, '{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
    return result


def iciba_lookup(word):
    params = {
        'key': 'E93A321FB1995DF5EC118B51ABAF8DC7',
        'type': 'json',
        'w': word
    }
    url = '{}?{}'.format('http://dict-co.iciba.com/api/dictionary.php', urllib.urlencode(params))
    try:
        data = urllib.urlopen(url).read()
        data = convert(json.loads(data))
    except:
        raise DictLookupError('error to fetch data.')
    result = []
    symbol = data.get('symbols', [{}])[0]
    if is_english(word):
        for elem in symbol.get('parts', []):
            result.append('{} {}'.format(elem.get('part', ''), '；'.join(elem.get('means', []))))
        if result:
            phonetic = symbol.get('ph_am', '')
            result.insert(0, '{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
    else:
        elem = symbol.get('parts', [{}])[0]
        for mean in elem.get('means', []):
            word_mean = mean.get('word_mean', '')
            if word_mean:
                result.append(word_mean)
        if result:
            phonetic = symbol.get('word_symbol', '')
            result.insert(0, '{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
    return result


def baidu_lookup(word):
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


def lookup(dictionary, word):
    dict_map = {
        'sys': system_lookup,
        'system': system_lookup,
        'yd': youdao_lookup,
        'youdao': youdao_lookup,
        'cb': iciba_lookup,
        'iciba': iciba_lookup,
        'bd': baidu_lookup,
        'baidu': baidu_lookup
    }
    lookup_func = dict_map.get(dictionary, None)
    return lookup_func and lookup_func(word)


if __name__ == '__main__':
    import sys

    def print_result(dictionary, word):
        print '---------- {}: {} ----------'.format(dictionary, word)
        try:
            result = lookup(dictionary, word)
        except DictLookupError, e:
            print e
        print 'failed to lookup.' if result is None else '\n'.join(result)

    if len(sys.argv) == 1:
        for dictionary in ('system', 'youdao', 'iciba', 'baidu'):
            for word in ('translate', '翻译'):
                print_result(dictionary, word)
    elif len(sys.argv) >= 3:
        print_result(sys.argv[1], ' '.join(sys.argv[2:]))
    else:
        print 'Usage: {} dict word'.format(sys.argv[0])
        sys.exit(1)
