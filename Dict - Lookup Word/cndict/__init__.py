#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib
from utils import *


def _load_module(dictionary):
    dict_name_map = {
        'sys': 'system',
        'yd': 'youdao',
        'cb': 'iciba',
        'bd': 'baidu',
        'by': 'bing'
    }
    module_name = dict_name_map.get(dictionary, dictionary) + 'dict'
    try:
        return importlib.import_module('.' + module_name, __name__)
    except ImportError:
        pass


def lookup(dictionary, *args, **kwargs):
    dictionary = _load_module(dictionary)
    if dictionary:
        return dictionary.lookup(*args, **kwargs)


def extract(dictionary, *args, **kwargs):
    dictionary = _load_module(dictionary)
    if dictionary:
        return dictionary.extract(*args, **kwargs)


def get_url(dictionary, *args, **kwargs):
    dictionary = _load_module(dictionary)
    if dictionary:
        return dictionary.get_url(*args, **kwargs)
