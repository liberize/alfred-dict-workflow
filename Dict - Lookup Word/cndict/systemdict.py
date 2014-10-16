#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib
import subprocess
from utils import *

DEFAULT_CMD = '{}/{}'.format(os.path.dirname(os.path.realpath(__file__)), 'systemdict')
DEFAULT_DICT_NAME = 'landau'  # or 'oxford'


def lookup(word, external_cmd=True, cmd=DEFAULT_CMD, dict_name=DEFAULT_DICT_NAME):
    if external_cmd:
        if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
            if dict_name == 'oxford':
                dict_path = '/Library/Dictionaries/Simplified Chinese - English.dictionary'
            elif dict_name == 'landau':
                dict_file = 'langdao-ec-gb.dictionary' if is_english(word) else 'langdao-ce-gb.dictionary'
                dict_path = os.path.expanduser('~/Library/Dictionaries/{}'.format(dict_file))
            else:
                raise DictLookupError('dict name not valid.')
            proc = subprocess.Popen([cmd, dict_path, word], stdout=subprocess.PIPE)
            definition = proc.stdout.read()
            if definition == '(null)\n':
                return []
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
    if dict_name == 'oxford':
        is_eng = is_english(word)

        number = u'①-⑳㉑-㉟㊱-㊿'
        chinese = ur'\u4e00-\u9fa5'
        pinyin = u'āáǎàēéěèōóǒòīíǐìūúǔùüǘǚǜńň'
        phrase = r"a-zA-Z,\. "
        sentence = ur"0-9a-zA-Z'‘’«»£\$/\?!,\.\[\]\(\) "
        pinyin_all = u"a-z{}'… ".format(pinyin)
        sentence_full = ur'([{1}][{0}]*[{1}]|\([{0}]*[{1}]|[{1}][{0}]*\)) ?[{2}]+'.format(
            sentence, sentence.replace(r'\(\) ', ''), chinese)

        part_map = {
            'noun': 'n.',
            'intransitive verb': 'vi.',
            'transitive verb': 'vt.',
            'adjective': 'adj.',
            'adverb': 'adv.',
            'determiner': 'det.',
            'pronoun': 'pron.',
            'preposition': 'prep.',
            'conjunction': 'conj.',
            'exclamation': 'excl.',
            'abbreviation': 'abbr.',
            'plural noun': 'pl.',
            'modifier': 'mod.'
        } if is_eng else {
            u'名词': u'n.',
            u'动词': u'v.',
            u'形容词': u'adj.',
            u'副词': u'adv.',
            u'数词': u'num.',
            u'代词': u'pron.',
            u'介词': u'prep.',
            u'连词': u'conj.',
            u'叹词': u'excl.'
        }

        ignore_list = [
            'Uncountable and countable', 'Countable', 'Uncountable', 'British', 'American',
            'colloquial', 'euphemistic', 'dated', 'Linguistics'
        ] if is_eng else [
            u'方言', u'客套话', u'委婉语', u'书面语', u'俗语', u'比喻义', u'口语', u'惯用语'
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

    elif dict_name == 'landau':
        definition = definition.encode('utf-8').split('\n相关词组:\n')[0]
        result = definition.split('\n')
        if is_english(word):
            if result[1].startswith('*['):
                phonetic = result[1][2:-1]
                result[0:2] = ['{} {}'.format(word, '/{}/'.format(phonetic) if phonetic else '')]
        else:
            result[1:2] = result[1].split('; ')
    else:
        raise DictLookupError('dict name not valid.')

    return result


def copy(word, item, dict_name=DEFAULT_DICT_NAME):
    if not is_english(word):
        if dict_name == 'oxford':
            match = re.match(r'[a-z]+\. (（.+）|［.+］)?(.+)', item)
            if match:
                item = match.group(2)
        elif dict_name == 'landau':
            match = re.match(r'【.+】 (.+)', item)
            if match:
                item = match.group(1)
    os.system("printf '{}' | LANG=en_US.UTF-8 pbcopy".format(escape(item)))


def open(word):
    url = 'dict://' + urllib.quote(word)
    os.system('open {}'.format(url))


def say(word):
    os.system("say '{}'".format(word.replace("'", "\\'")))
