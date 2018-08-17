#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import urllib
import subprocess
import platform
from distutils.version import StrictVersion
from utils import *

_lxml_installed = True
try:
    sys.path.append('/usr/local/lib/python2.7/site-packages')
    from lxml import etree
except ImportError:
    _lxml_installed = False


def lookup(word, *args):
    mac_ver = StrictVersion(platform.mac_ver()[0])
    if mac_ver < StrictVersion('10.13'):
        raise DictLookupError('system oxford dict requires macOS version 10.13!')

    if not _lxml_installed:
        raise DictLookupError('lxml not installed!')

    cmd = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), 'systemdict')
    if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
        proc = subprocess.Popen([cmd, '-t', 'html', '-d', '牛津英汉汉英词典', word],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        definition = proc.stdout.read()
        if definition.strip() == '':
            return []
    else:
        raise DictLookupError('file {} not found or not executable.'.format(cmd))

    result = []
    is_eng = is_english(word)

    part_map = {
        'noun': 'n.',
        'verb': 'v.',
        'intransitive verb': 'vi.',
        'transitive verb': 'vt.',
        'reflexive verb': 'vr.',
        'adjective': 'adj.',
        'adverb': 'adv.',
        'determiner': 'det.',
        'pronoun': 'pron.',
        'preposition': 'prep.',
        'conjunction': 'conj.',
        'exclamation': 'excl.',
        'abbreviation': 'abbr.',
        'noun plural': 'pl.',
        'modifier': 'mod.'
    }

    # use ElementTree to parse html
    ns = {'d': 'http://www.apple.com/DTDs/DictionaryService-1.0.rng'}
    phonetic_spans = []
    for xml in definition.split('<?xml')[1:]:
        html = etree.fromstring('<?xml' + xml)
        # entry span
        entry = html.xpath('.//d:entry', namespaces=ns)
        if not entry:
            continue
        entry = entry[0]
        # word span
        word_span = entry.xpath("./span[contains(@class,'hwg')]/span[@d:dhw]", namespaces=ns)
        if not word_span:
            continue
        word_text = word_span[0].text.strip()
        if word_text.encode('utf-8').lower() == word.lower():
            # lookup a word, e.g. go
            root = entry
            phonetic_span = entry.xpath("./span[contains(@class,'hwg')]/span[@class='prx' and @dialect='AmE']/span[@class='ph']")
            if phonetic_span:
                phonetic_spans.extend(phonetic_span)
        else:
            # lookup a phrase, e.g. go for
            if not is_eng:
                continue
            phrase_span = entry.xpath("./span[contains(@class,'pvb')]//span[contains(@class,'pvg')]/span[@class='pv' and normalize-space(.)='{}']/../..".format(word))
            if not phrase_span:
                continue
            root = phrase_span[0]

        for span1 in root.xpath("./span[@lexid]"):
            # some words may have different phonetic for different part, e.g. record
            phonetic_span = span1.xpath("./span[1]/span[@class='prx' and @dialect='AmE']/span[@class='ph']")
            if phonetic_span:
                phonetic_spans.extend(phonetic_span)

            part_span = span1.xpath("./span[1]/span[@class='ps']")
            if not part_span:
                continue
            part_text = part_span[0].text.strip()
            part = part_map.get(part_text, part_text + '.')

            # for word, find span[@class='trgg x_xd2']; for phrase, find span[@class='x_xdh']
            # common way is to find parent of span[contains(@class,'trg')]
            # for ch to eng, the situation is more complicated
            for span2 in span1.xpath("./span[@lexid]//span[contains(@class,'trg') and not(ancestor::span[contains(@class,'exg')])]/.."):
                spans = span2.xpath("./span[contains(@class,'trg')]/span[@class='ind' or @class='trans']")
                item = ' '.join(''.join(s.itertext()).strip() for s in spans)
                item = re.sub(r' {2,}', ' ', item)
                item = item.replace(' ;', ';')
                if item:
                    item = u'{} {}'.format(part, item).encode('utf-8')
                    result.append(item)

    phonetics = []
    for phonetic_span in phonetic_spans:
        phonetic = ''.join(phonetic_span.itertext()).strip()
        phonetic = u'/{}/'.format(phonetic).encode('utf-8')
        if phonetic not in phonetics:
            phonetics.append(phonetic)
    phonetics = ', '.join(phonetics)
    if phonetics or len(result) > 0:
        result.insert(0, '{} {}'.format(word, phonetics))

    return result


def extract(word, item):
    if not is_english(word):
        match = re.match(r'[a-z]+\. (（.+）|［.+］)?(.+)', item)
        if match:
            return match.group(2)


def get_url(word):
    return 'dict://' + urllib.quote(word)
