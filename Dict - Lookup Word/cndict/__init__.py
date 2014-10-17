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
        return None


def lookup(dictionary, word):
    dictionary = _load_module(dictionary)
    if dictionary:
        return dictionary.lookup(word)
    else:
        return None


def copy(dictionary, word, item):
    dictionary = _load_module(dictionary)
    if dictionary:
        dictionary.copy(word, item)


def open(dictionary, word):
    dictionary = _load_module(dictionary)
    if dictionary:
        dictionary.open(word)


def say(dictionary, word):
    dictionary = _load_module(dictionary)
    if dictionary:
        dictionary.say(word)
