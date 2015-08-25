#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib
import subprocess
from utils import *


def lookup(word, *args):
    cmd = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), 'systemdict')
    if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
        dict_name = '朗道英汉字典5.0' if is_english(word) else '朗道汉英字典5.0'
        proc = subprocess.Popen([cmd, '-t', 'text', '-d', dict_name, word],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        definition = proc.stdout.read()
        if definition.strip() == '':
            return []
    else:
        raise DictLookupError('file {} not found or not executable.'.format(cmd))

    result = []
    definition = definition.split('\n相关词组:\n')[0]
    result = definition.split('\n')
    if is_english(word):
        if result[1].startswith('*['):
            phonetic = result[1][2:-1]
            result[0:2] = ['{} {}'.format(word, '/{}/'.format(phonetic) if phonetic else '')]
    else:
        result[1:2] = result[1].split('; ')
    return result


def extract(word, item):
    if not is_english(word):
        match = re.match(r'(【.+】 )?(.+)', item)
        if match:
            return match.group(2)


def get_url(word):
    return 'dict://' + urllib.quote(word)
