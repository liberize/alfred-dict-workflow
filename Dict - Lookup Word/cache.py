# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals
import os
import json
import time
import shutil
import codecs
import hashlib

# { 'expire_time' : 0, name: '', data' : {} }

_DEFAULT_EXPIRE = 60 * 60 * 24


class Cache(object):
    def __init__(self, cache_dir):
        self.__cache_dir = cache_dir

    def __get_path(self, name):
        if not os.path.exists(self.__cache_dir):
            os.makedirs(self.__cache_dir)
        # convert to md5, more safe for file name
        md5_name = hashlib.md5(name).hexdigest()
        return os.path.join(self.__cache_dir, '{}.json'.format(md5_name))

    def __get_content(self, name):
        try:
            filepath = self.__get_path(name)
            with codecs.open(filepath, 'r', 'utf-8') as f:
                return json.load(f)
        except:
            pass

    def set(self, name, data, expire=_DEFAULT_EXPIRE):
        filepath = self.__get_path(name)
        try:
            cache = {
                'expire': time.time() + expire,
                'name': name,
                'data': data
            }
            with codecs.open(filepath, 'w', 'utf-8') as f:
                json.dump(cache, f, indent=4)
        except:
            pass

    def get(self, name, default=None):
        try:
            cache = self.__get_content(name)
            if cache['expire'] >= time.time():
                return cache['data']
        except:
            pass
        return default

    def delete(self, name):
        cache_file = self.__get_path(name)
        if os.path.exists(cache_file):
            os.remove(cache_file)

    def clean(self):
        if os.path.exists(self.__cache_dir):
            shutil.rmtree(self.__cache_dir)

    def clean_expired(self):
        if not os.path.exists(self.__cache_dir):
            return
        to_remove = []
        for f in os.listdir(self.__cache_dir):
            if not f.endswith('.json'):
                continue
            filepath = os.path.join(self.__cache_dir, f)
            try:
                with codecs.open(filepath, 'r', 'utf-8') as fp:
                    cache = json.load(fp)
                    if cache['expire'] < time.time():
                        to_remove.append(filepath)
            except:
                to_remove.append(filepath)
        for f in to_remove:
            os.remove(f)

    def timeout(self, name):
        try:
            cache = self.__get_content(name)
            if cache['expire'] >= time.time():
                return cache['expire'] - time.time()
        except:
            pass
        return -1
