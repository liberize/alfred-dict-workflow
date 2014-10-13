#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import plistlib
import cndict
from cache import Cache
from feedback import Feedback


def query(dictionary, word, dict_cache):
    now = time.time()

    # dict_cache.set('last lookup time', now, float('inf'))
    # time.sleep(1)
    # if dict_cache.get('last lookup time') != now:
    #     return

    clean_time = dict_cache.get('last clean time')
    if clean_time is None or now - clean_time > 3600 * 24:
        dict_cache.set('last clean time', now, float('inf'))
        dict_cache.clean_expired()

    cache_name = '{}@{}'.format(word, dictionary)
    cache = dict_cache.get(cache_name)
    if cache:
        return cache

    result = cndict.lookup(dictionary, word)
    if result:
        result = [item.decode('utf-8') for item in result]
        dict_cache.set(cache_name, result, 3600 * 24)
        return result


feedback = Feedback()
sys.argv = [arg for arg in sys.argv if arg != '']
argc = len(sys.argv)
if argc == 1:
    feedback.add_item(title=u'Dict - Lookup Word',
                      subtitle=u'Format: "word @ dict". Available dicts are "sys", "yd", "cb", "bd", "by".',
                      valid=False)
elif argc == 2:
    arg = sys.argv[1]
    pos = arg.rfind('@')
    if pos == -1:
        word = arg.strip()
        dictionary = 'sys'
    else:
        word = arg[:pos].strip()
        dictionary = arg[pos+1:].strip()
        if dictionary == '':
            dictionary = 'sys'
    plist = plistlib.readPlist(os.path.abspath('./info.plist'))
    bundle_id = plist['bundleid'].strip()
    base_dir = os.path.expanduser('~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/')
    dict_cache = Cache(os.path.join(base_dir, bundle_id))
    try:
        result = query(dictionary, word, dict_cache)
        if result:
            arg = u'{} @ {}'.format(word.decode('utf-8'), dictionary.decode('utf-8'))
            feedback.add_item(title=result[0],
                              subtitle=u'Press "↩" to view full definition or "⌘/⌥/⌃/⇧/fn + ↩" to lookup word in other dicts.',
                              arg=arg,
                              valid=True)
            if cndict.is_english(word):
                for item in result[1:]:
                    feedback.add_item(title=item, valid=False)
            else:
                for item in result[1:]:
                    feedback.add_item(title=item, arg=u'{} | {}'.format(arg, item), valid=True)
        else:
            feedback.add_item(title=u'Dict - Lookup Word',
                              subtitle=u'Word "{}" doesn\'t exist in dict "{}".'.format(word.decode('utf-8'), dictionary.decode('utf-8')),
                              valid=False)
    except cndict.DictLookupError, e:
        feedback.add_item(title=word, subtitle='Error: {}'.format(e), valid=False)
else:
    sys.exit(1)
feedback.output()
