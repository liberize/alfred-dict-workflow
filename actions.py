#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import cndict
import json

from alfred.alfred import Alfred
from alfred.cache import Cache
from alfred.plist import Plist


if len(sys.argv) != 2:
    sys.exit(1)


def shell_exec(cmd, arg, escape=False):
    if escape:
        arg = arg.replace("%", "%%").replace("\\", "\\\\")
    os.environ['LANG'] = 'en_US.UTF-8'
    os.system(cmd.format("'{}'".format(arg.replace("'", "\\'"))))


alfred = Alfred()
plist = Plist()
plist.read(os.path.abspath('./info.plist'))

match = re.match(r'^:(.*?) ([@|>]) (.*?)$', sys.argv[1])
if match:
    command = match.group(1).strip()
    if command == 'clean':
        dict_cache = Cache(os.path.join(alfred.get_cache_dir(), plist.get_bundleid()))
        dict_cache.clean()
        print 'Cache has been cleaned.'
    elif command == 'config':
        shell_exec('open {}', os.path.abspath('./config.json'))
        print 'Please edit config file in your editor.'
    elif command == 'update':
        config_data = open(os.path.abspath('./config.json')).read()
        config = json.loads(re.sub(r'//.*', '', config_data))
        plist.set_keyword(config['keyword'])
        plist.set_keymap(config['keymap'])
        plist.write(os.path.abspath('./info.plist'))
        print 'Config has been successfully updated.'
else:
    match = re.match(r'^(.*?) @ (.*?) (\| (.*) )?([@|>]) (.*?)$', sys.argv[1])
    if match:
        word, dictionary, _, item, operator, command = match.groups()
        if operator == '@':
            keyword = plist.get_keyword()
            if keyword:
                if item:
                    new_word = cndict.extract(dictionary, word, item)
                    if new_word:
                        word = new_word
                        dictionary = command
                else:
                    dictionary = command
                alfred.run('{} {} @ {}'.format(keyword, word, dictionary))
        elif operator == '>':
            if item:
                definition = cndict.extract(dictionary, word, item) or item
                shell_exec('printf {} | pbcopy', definition, True)
                print 'Definition copied to clipboard.'
            elif command == 'say':
                shell_exec('say {}', word)
            elif command == 'open':
                url = cndict.get_url(dictionary, word)
                shell_exec('open {}', url)
