#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import subprocess


class Alfred(object):
    def __init__(self):
        self.version = self.__get_version()

    def __get_version(self):
        match = re.search(r'/Alfred (\d)/', os.path.realpath(__file__))
        if match:
            return int(match.group(1))
        proc = subprocess.Popen("ps ax -o command | grep '[A]lfred'", shell=True, stdout=subprocess.PIPE)
        match = re.search(r'/Alfred (\d)\.app/', proc.stdout.read())
        if match:
            return int(match.group(1))
        return 2

    def get_cache_dir(self):
        return os.path.expanduser('~/Library/Caches/com.runningwithcrayons.Alfred-{}/Workflow Data/'.format(self.version))

    def run(self, text):
        os.system("""osascript -e 'tell application "Alfred {}" to search "{}"' &""".format(self.version, text.replace('"', '\\"')))
