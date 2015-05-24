#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import cndict
import plistlib

if len(sys.argv) != 2:
    sys.exit(1)


def get_keyword():
    plist = plistlib.readPlist(os.path.abspath('./info.plist'))
    for item in plist['objects']:
        if 'keyword' in item['config']:
            return item['config']['keyword']


def restore(arg):
    os.system("""osascript -e 'tell application "Alfred 2" to search "{}"' &""".format(arg.replace('"', '\\"')))


def shell_exec(cmd, arg, escape=False):
    if escape:
        arg = arg.replace("%", "%%").replace("\\", "\\\\")
    os.environ['LANG'] = 'en_US.UTF-8'
    os.system(cmd.format("'{}'".format(arg.replace("'", "\\'"))))


match = re.match(r'^(:.*?) ([@|>]) (.*?)$', sys.argv[1])
if match:
    keyword = get_keyword()
    if keyword:
        restore('{} {}'.format(keyword, match.group(1)))
else:
    match = re.match(r'^(.*?) @ (.*?) (\| (.*) )?([@|>]) (.*?)$', sys.argv[1])
    if match:
        word, dictionary, _, item, operator, command = match.groups()
        if operator == '@':
            keyword = get_keyword()
            if keyword:
                if item:
                    new_word = cndict.extract(dictionary, word, item)
                    if new_word:
                        word = new_word
                        dictionary = command
                else:
                    dictionary = command
                restore('{} {} @ {}'.format(keyword, word, dictionary))
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
