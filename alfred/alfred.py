#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os


class Alfred(object):
    def __init__(self):
        match = re.search(r'/Alfred (\d)/', os.path.realpath(__file__))
        self.version = int(match.group(1)) if match else 2

    def get_cache_dir(self):
        return os.path.expanduser('~/Library/Caches/com.runningwithcrayons.Alfred-{}/Workflow Data/'.format(self.version))

    def run(self, text):
        os.system("""osascript -e 'tell application "Alfred {}" to search "{}"' &""".format(self.version, text.replace('"', '\\"')))
