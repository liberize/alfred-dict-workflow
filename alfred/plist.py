#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import plistlib
import cndict


class Plist(object):
    def __init__(self):
        self.__modifier_map = {
            0: 'none',
            524288: 'alt',
            262144: 'ctrl',
            131072: 'shift',
            1048576: 'cmd',
            8388608: 'fn'
        }
        self.__plist = None
        self.__base = None
        self.__branches = {}

    def read(self, path):
        self.__plist = plistlib.readPlist(path)
        for obj in self.__plist['objects']:
            if 'keyword' in obj['config']:
                self.__base = obj
                uid = self.__base['uid']
                for conn in self.__plist['connections'][uid]:
                    self.__branches[conn['destinationuid']] = [conn, None]
                break
        for uid, pair in self.__branches.iteritems():
            for obj in self.__plist['objects']:
                if uid == obj['uid']:
                    pair[1] = obj
                    break

    def write(self, path):
        if self.__plist:
            plistlib.writePlist(self.__plist, path)

    def get_keyword(self):
        if self.__base:
            return self.__base['config']['keyword']
        return ''

    def set_keyword(self, value):
        if self.__base:
            self.__base['config']['keyword'] = value

    def get_keymap(self):
        keymap = {}
        for conn, child in self.__branches.values():
            modifier = self.__modifier_map[conn['modifiers']]
            match = re.search(r'[@|>] (\w+)"', child['config']['script'])
            if match:
                keymap[modifier] = match.group(1)
        return keymap

    def set_keymap(self, value):
        keymap = value
        for conn, child in self.__branches.values():
            modifier = self.__modifier_map[conn['modifiers']]
            if modifier in keymap:
                child['config']['script'] = re.sub(r'(?<=[@|>] )\w+(?=")', keymap[modifier],
                                                   child['config']['script'])
                if modifier != 'none':
                    dict_name = cndict.get_full_name(keymap[modifier])
                    conn['modifiersubtext'] = re.sub(r'(?<=in )\w+(?= dict)', dict_name,
                                                     conn['modifiersubtext'])

    def get_bundleid(self):
        if self.__plist:
            return self.__plist['bundleid']
        return ''
