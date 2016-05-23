#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import importlib
from utils import *


def get_full_name(dictionary):
    dict_name_map = {
        'nj': 'oxford',
        'ld': 'landau',
        'yd': 'youdao',
        'cb': 'iciba',
        'by': 'bing',
        'hc': 'dictcn'
    }
    return dict_name_map.get(dictionary, dictionary)


def _load_module(dictionary):
    module_name = get_full_name(dictionary)
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
