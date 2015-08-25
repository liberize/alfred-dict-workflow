#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib
import subprocess
import platform
from distutils.version import StrictVersion
from utils import *

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


def lookup(word, external_cmd=True, parse_html=True, *args):
    if external_cmd:
        cmd = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), 'systemdict')
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            dict_name = '牛津英汉汉英词典'
            proc = subprocess.Popen([cmd, '-t', 'html' if parse_html else 'text', '-d', dict_name, word],
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            definition = proc.stdout.read()
            if definition.strip() == '':
                return []
            if not parse_html:
                definition = definition.decode('utf-8')
        else:
            raise DictLookupError('file {} not found or not executable.'.format(cmd))
    else:
        from DictionaryServices import DCSCopyTextDefinition
        unicode_word = word.decode('utf-8')
        word_range = (0, len(unicode_word))
        definition = DCSCopyTextDefinition(None, unicode_word, word_range)
        if definition is None:
            return []

    result = []
    is_eng = is_english(word)
    mac_ver = StrictVersion(platform.mac_ver()[0])

    part_map = {
        'noun': 'n.',
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
    } if is_eng else {
        u'名' if mac_ver >= StrictVersion('10.10') else u'名词': u'n.',
        u'动' if mac_ver >= StrictVersion('10.10') else u'动词': u'v.',
        u'形' if mac_ver >= StrictVersion('10.10') else u'形容词': u'adj.',
        u'副' if mac_ver >= StrictVersion('10.10') else u'副词': u'adv.',
        u'数' if mac_ver >= StrictVersion('10.10') else u'数词': u'num.',
        u'代' if mac_ver >= StrictVersion('10.10') else u'代词': u'pron.',
        u'介' if mac_ver >= StrictVersion('10.10') else u'介词': u'prep.',
        u'连' if mac_ver >= StrictVersion('10.10') else u'连词': u'conj.',
        u'叹' if mac_ver >= StrictVersion('10.10') else u'叹词': u'excl.'
    }

    if external_cmd and parse_html:
        # use ElementTree to parse html
        ns = '{http://www.apple.com/DTDs/DictionaryService-1.0.rng}'
        phonetic_spans = []
        for xml in definition.split('<?xml')[1:]:
            html = ET.fromstring('<?xml' + xml)
            entry = html.find('.//{}entry'.format(ns))

            word_span = entry.find("./span[@class='hwg']/span[@{}dhw]".format(ns))
            if word_span is None:
                continue
            if word_span.text.encode('utf-8').lower() == word.lower():
                root = entry
                phonetic_span = entry.find("./span[@class='hwg']/span[@class='pr']".format(ns))
                if phonetic_span is not None:
                    phonetic_spans.append(phonetic_span)
            else:
                if not is_eng:
                    continue
                phrase_span = entry.find("./span[@class='pvb']//span[@class='pvg'][span='{}']/..".format(word))
                if phrase_span is None:
                    continue
                root = phrase_span

            for span1 in root.findall("./span[@lexid]"):
                phonetic_span = span1.find("./span[@class='pr']")
                if phonetic_span is not None:
                    phonetic_spans.append(phonetic_span)

                part_span = span1.find("./span[@class='ps']")
                if part_span is None:
                    continue
                part = part_map.get(part_span.text, part_span.text + '.')
                for span2 in span1.findall("./span[@lexid]"):
                    item = ''
                    for span3 in span2.findall('./span[@class]'):
                        if span3.attrib['class'] == 'ind':
                            item += ''.join(span3.itertext())
                        elif span3.attrib['class'] == 'trg':
                            for span4 in span3.findall('./span[@class]'):
                                if span4.attrib['class'] != 'trans ty_pinyin':
                                    item += ''.join(span4.itertext())

                    item = re.sub(r' {2,}', ' ', item).strip()
                    if item:
                        item = u'{} {}'.format(part, item).encode('utf-8')
                        result.append(item)

        phonetics = []
        for phonetic_span in phonetic_spans:
            phonetic = ''.join(phonetic_span.itertext())
            phonetic = re.sub(r' {2,}', ' ', phonetic).encode('utf-8').strip(' |')
            phonetic = '/{}/'.format(phonetic)
            if phonetic not in phonetics:
                phonetics.append(phonetic)
        phonetics = ', '.join(phonetics)
        if phonetics or len(result) > 0:
            result.insert(0, '{} {}'.format(word, phonetics))

    else:
        # use regular expression to parse text
        number = u'①-⑳㉑-㉟㊱-㊿'
        chinese = ur'\u4e00-\u9fa5'
        pinyin = u'āáǎàēéěèōóǒòīíǐìūúǔùüǘǚǜńň'
        phrase = r"a-zA-Z,\. "
        sentence = ur"0-9a-zA-Z'‘’«»£\$/\?!,\.\[\]\(\) "
        pinyin_all = u"a-zA-Z{}'… ".format(pinyin)
        sentence_full = ur'([{1}][{0}]*[{1}]|\([{0}]*[{1}]|[{1}][{0}]*\)) ?[{2}]+'.format(
            sentence, sentence.replace(r'\(\) ', ''), chinese)

        ignore_list = [
            'Countable and uncountable', 'Uncountable and countable',
            'Countable', 'Uncountable', 'British', 'American',
            'colloquial', 'euphemistic', 'dated', 'Linguistics'
        ] if is_eng else [
            u'方言', u'客套话', u'委婉语', u'书面语', u'俗语', u'比喻义',
            u'口语', u'惯用语', u'旧词', u'敬辞'
        ]

        phrase_mode = False
        if is_eng:
            word_escaped = re.escape(word)
            if not re.match(word_escaped + '(?= )', definition, re.I):
                verb_escaped = re.escape(word.split(' ')[0])
                if not re.match(verb_escaped + '(?= )', definition, re.I):
                    return result
                phrase_mode = True
            pos = definition.find('PHRASAL VERB')
            if phrase_mode:
                if pos == -1:
                    return result
                definition = definition[pos:]
                match = re.search(r'(({0}:? )([A-Z]\. )?({1}).*?)(?=\b{2} [{3}]*?:? ([A-Z]\. )?({1}))'.format(
                    word_escaped, '|'.join(part_map.keys()), verb_escaped, phrase), definition)
                if match is None:
                    return result
                definition = match.group(1)
                start_pos = len(match.group(2))
            else:
                if pos != -1:
                    definition = definition[:pos]

        if phrase_mode:
            result.append(word)
        else:
            trimmed_len = 0
            single_phonetic = True
            if is_eng:
                phonetics = []
                for match in re.finditer(r'[A-Z]\. \|(.*?)\| ?', definition):
                    phonetic = match.group(1).encode('utf-8').strip()
                    phonetic = '/{}/'.format(phonetic)
                    if phonetic not in phonetics:
                        phonetics.append(phonetic)
                    start = match.start() + 3 - trimmed_len
                    end = match.end() - trimmed_len
                    definition = definition[:start] + definition[end:]
                    trimmed_len += end - start
                if len(phonetics) > 0:
                    phonetics = ', '.join(phonetics)
                    result.append('{} {}'.format(word, phonetics))
                    single_phonetic = False
            if single_phonetic:
                match = re.search(r'\|(.*?)\| ?'
                                  if is_eng else
                                  ur'([^ ]*[{}][^ ]*) ?'.format(pinyin),
                                  definition)
                if match is None:
                    return result
                phonetic = match.group(1).encode('utf-8').strip()
                result.append('{}{}'.format(word, ' /{}/'.format(phonetic) if phonetic else ''))
                start_pos = match.span()[1]

        part_list = []
        pattern = (r'({}) ?(\(.*?\))? ?'.format('|'.join(part_map.keys()))
                   if is_eng else
                   ur'({}) '.format('|'.join(part_map.keys())))

        if 'A. ' not in definition:
            match = re.match(pattern, definition[start_pos:])
            if match:
                part_list.append((start_pos, start_pos + match.span()[1], part_map[match.group(1)]))
        else:
            for match in re.finditer(ur'[A-Z]\. {}'.format(pattern), definition):
                part_list.append((match.start(), match.end(), part_map[match.group(1)]))

        last_start_pos = len(definition)
        pattern = (ur"([^{4}]*?([{0}][{1}]*? |[{2}]*?(\) |›)))(?=({3}|[{4}]|$))".format(pinyin, pinyin_all, phrase, sentence_full, number)
                   if is_eng else
                   ur"(?![a-z] )([^{2}]*?[{0}]* )(?=([→{1}{2}]|$))".format(phrase, chinese, number))

        for part in reversed(part_list):
            entry_list = []
            text = definition[part[1]:last_start_pos]
            if u'① ' not in text:
                match = re.match(pattern, text)
                if match:
                    entry_list.append(match.group(1))
            else:
                for match in re.finditer(ur'[{}] {}'.format(number, pattern), text):
                    entry_list.append(match.group(1))

            pos = 1
            for entry in entry_list:
                entry = re.sub(ur'[{0}]*[{1}][{0}]*'.format(pinyin_all, pinyin)
                               if is_eng else
                               r'\[used .*?\]',
                               '', entry)
                entry = re.sub(ur'({})'.format('|'.join(ignore_list)), '', entry)
                entry = re.sub(r'\([ /]*\)', '', entry)
                entry = re.sub(r' {2,}', ' ', entry).strip()
                if is_eng:
                    entry = entry.replace(u' ;', u';')
                entry = (u'{} {}'.format(part[2], entry)).encode('utf-8')
                result.insert(pos, entry)
                pos += 1

            last_start_pos = part[0]

    return result


def extract(word, item):
    if not is_english(word):
        match = re.match(r'[a-z]+\. (（.+）|［.+］)?(.+)', item)
        if match:
            return match.group(2)


def get_url(word):
    return 'dict://' + urllib.quote(word)
