#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import cndict

if len(sys.argv) != 2:
    sys.exit(1)


def restore(arg):
    os.system("""osascript -e 'tell application "Alfred 2" to search "{}"'""".format(arg.replace('"', '\\"')))

match = re.match(r'^(.*?) @ (.*?) (\| (.*) )?([@|>]) (.*?)$', sys.argv[1])
if match:
    word, dictionary, _, item, operator, command = match.groups()
    if item:
        cndict.copy(dictionary, item)
        print 'Definition copied to clipboard.'
    else:
        if operator == '@':
            restore('dict {} @ {}'.format(word, command))
        elif operator == '>':
            if command == 'say':
                cndict.say(dictionary, word)
            elif command == 'open':
                cndict.open(dictionary, word)
