#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

if len(sys.argv) != 2:
    sys.exit(1)

if '@' in sys.argv[1]:
    secs = sys.argv[1].split('@')
    if len(secs) == 2:
        word, dictionary = (sec.strip() for sec in secs)
        if '>' in word:
            word = word.split('>')[0].strip()
        os.system("""osascript -e 'tell application "Alfred 2" to search "dict {} @ {}"'""".format(word.replace('"', '\\"'), dictionary))
elif '>' in sys.argv[1]:
    secs = sys.argv[1].split('>')
    if len(secs) == 2:
        word, command = (sec.strip() for sec in secs)
        if command == 'say':
            os.system("say '{}'".format(word.replace("'", "\\'")))
        elif command == 'copy':
            os.system("printf '{}' | pbcopy".format(word.replace("'", "\\'")))
            print 'Definition "{}" copied to clipboard.'.format(word)
