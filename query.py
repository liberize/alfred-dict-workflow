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
argc = len(sys.argv)
if argc == 1 or (argc == 2 and sys.argv[1] == ''):
    feedback.add_item(title=u'Dict - Lookup Word',
                      subtitle=u'Format: "word @ dict". Available dicts are "sys", "yd", "cb", "bd".',
                      valid=False)
elif argc == 2:
    secs = sys.argv[1].split('@')
    secc = len(secs)
    if secc == 1 or (secc == 2 and secs[1] == ''):
        word = secs[0]
        dictionary = 'sys'
    elif secc == 2:
        word, dictionary = (sec.strip() for sec in secs)
    else:
        sys.exit(1)
    plist = plistlib.readPlist(os.path.abspath('./info.plist'))
    bundle_id = plist['bundleid'].strip()
    base_dir = os.path.expanduser('~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data/')
    dict_cache = Cache(os.path.join(base_dir, bundle_id))
    try:
        result = query(dictionary, word, dict_cache)
        if result:
            feedback.add_item(title=result[0],
                              subtitle=u'Press "↩" to pronounce word or "⌘/⌥/⌃/⇧ + ↩" to lookup word in other dicts.',
                              arg=u'{} > say'.format(word.decode('utf-8')),
                              valid=True)
            for item in result[1:]:
                if not cndict.is_english(word) and cndict.is_english(item.encode('utf-8')):
                    feedback.add_item(title=item, arg=u'{} > copy'.format(item), valid=True)
                else:
                    feedback.add_item(title=item, valid=False)
        else:
            feedback.add_item(title=u'Dict - Lookup Word',
                              subtitle=u'Word "{}" doesn\'t exist in dict "{}".'.format(word.decode('utf-8'), dictionary.decode('utf-8')),
                              valid=False)
    except cndict.DictLookupError, e:
        feedback.add_item(title=word, subtitle='Error: {}'.format(e), valid=False)
else:
    sys.exit(1)
feedback.output()
