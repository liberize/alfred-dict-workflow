#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os


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


def shell_exec(cmd, arg, escape=False):
    if escape:
        arg = arg.replace("%", "%%").replace("\\", "\\\\")
    os.environ['LANG'] = 'en_US.UTF-8'
    os.system(cmd.format("'{}'".format(arg.replace("'", "\\'"))))


class DictLookupError(Exception):
    pass
