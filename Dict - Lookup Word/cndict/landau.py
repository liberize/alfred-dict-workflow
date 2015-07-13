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
        dict_file = 'langdao-ec-gb.dictionary' if is_english(word) else 'langdao-ce-gb.dictionary'
        dict_path = os.path.expanduser('~/Library/Dictionaries/{}'.format(dict_file))
        proc = subprocess.Popen([cmd, dict_path, word], stdout=subprocess.PIPE)
        definition = proc.stdout.read()
        if definition == '(null)\n':
            return []
        definition = definition.decode('utf-8')
    else:
        raise DictLookupError('file {} not found or not executable.'.format(cmd))

    result = []
    definition = definition.encode('utf-8').split('\n相关词组:\n')[0]
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
