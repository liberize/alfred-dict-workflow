#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
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

    internal_cmds = {
        'clean': 'Clean cache',
        'sysdict <o|l>': 'Set system dictionary to "oxford" or "landau"',
        'defact <v|p>': 'Set default action to "view full definition" or "pronounce word"',
    }

    if word.startswith(':'):
        cmd = word.lstrip(':').split(' ')
        if cmd[0] == '':
            feedback.add_item(title='Internal commands', valid=False)
            for cmdl, desc in internal_cmds.iteritems():
                feedback.add_item(title=cmdl, subtitle=desc,
                                  arg=':{} '.format(cmdl.split(' ')[0]), valid=True)
        else:
            success = False
            if cmd[0] == u'clean':
                dict_cache.clean()
                success = True
            elif cmd[0] == u'sysdict':
                if len(cmd) == 2:
                    system_dict = {'o': 'oxford', 'l': 'landau'}.get(cmd[1], None)
                    if system_dict:
                        content = open('cndict/systemdict.py').read()
                        content = re.sub(r'(?<=DEFAULT_DICT_NAME = ).*', "'{}'".format(system_dict), content)
                        open('cndict/systemdict.py', 'w').write(content)
                        success = True
            elif cmd[0] == u'defact':
                if len(cmd) == 2:
                    default_action = {'v': 'open', 'p': 'say'}.get(cmd[1], None)
                    if default_action:
                        content = open('./info.plist').read()
                        content = re.sub(r'\b(open|say)\b', default_action, content)
                        open('./info.plist', 'w').write(content)
                        success = True
            if success:
                feedback.add_item(title='Command executed successfully',
                                  subtitle=u'Press "↩" to return.',
                                  arg=':', valid=True)
            else:
                feedback.add_item(title='Invalid command',
                                  subtitle=u'Press "↩" to view available internal commands.',
                                  arg=':', valid=True)
    else:
        try:
            result = query(dictionary, word, dict_cache)
            arg = u'{} @ {}'.format(word.decode('utf-8'), dictionary.decode('utf-8'))
            if result:
                feedback.add_item(title=result[0],
                                  subtitle=u'Press "↩" to view full definition or "⌘/⌥/⌃/⇧/fn + ↩" to lookup word in other dicts.',
                                  arg=arg, valid=True)
                for item in result[1:]:
                    feedback.add_item(title=item, arg=u'{} | {}'.format(arg, item), valid=True)
            else:
                feedback.add_item(title='Dict - Lookup Word',
                                  subtitle=u'Word "{}" doesn\'t exist in dict "{}".'.format(word.decode('utf-8'), dictionary.decode('utf-8')),
                                  arg=arg, valid=True)
        except cndict.DictLookupError, e:
            feedback.add_item(title=word, subtitle='Error: {}'.format(e), valid=False)
else:
    sys.exit(1)
feedback.output()
