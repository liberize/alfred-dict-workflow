#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
from utils import *


def lookup(dictionary, word):
    dict_name_map = {
        'sys': 'system',
        'yd': 'youdao',
        'cb': 'iciba',
        'bd': 'baidu',
        'by': 'bing'
    }
    module_name = dict_name_map.get(dictionary, dictionary) + 'dict'
    try:
        cndict = importlib.import_module('.' + module_name, __name__)
    except ImportError:
        return None
    return cndict.lookup(word)
