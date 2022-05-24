#!/usr/bin/env python
# -*- coding: utf-8 -*-

from six import u as unicode

def is_english(word):
    for i in word:
        if ord(i) > 127:
            return False
    return True


def convert(input):
    if isinstance(input, dict):
        return {convert(key): convert(value) for key, value in input.items()}
    elif isinstance(input, list):
        return [convert(element) for element in input]
    # elif isinstance(input, unicode):
    #     return str(input, 'utf-8')
    else:
        return input


class DictLookupError(Exception):
    pass
