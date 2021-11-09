#!/usr/bin/env python3

import regex as re
from collections import defaultdict

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" DerivBaseDE-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")


# load data and extract relations and their rules
relations_from_derivbase = defaultdict()
with open(sys.argv[1], mode='r', encoding='U8') as file:
    for line in file:
        rule_paths = line.strip().split(' ')[3:]
        rule_paths = zip(rule_paths[0::3], rule_paths[1::3], rule_paths[2::3])
        for first, rule, second in rule_paths:
            relations_from_derivbase[(first, second)] = rule[:-1]


# load rules and convert them into regular expressions
def convert_string_rule_to_regular_expression(string_rule):
    first_pos = string_rule.split(' ')[-2]
    second_pos = string_rule.split(' ')[-1]
    rule = ' '.join(string_rule.split(' ')[:-2])

    # prefixation pattern: (pfx "rück") verbs verbs
    result = re.search(r'\(pfx \"(\p{L}+)\"\)$', rule)
    if result:
        return '^' + result.group(1)

    # sufixation pattern: (sfx "schaft")
    result = re.search(r'\(sfx \"(\p{L}+)\"\)$', rule)
    if result:
        return result.group(1) + '$'

    # resufixation pattern: (rsfx "ier" "end")
    result = re.search(r'\(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)$', rule)
    if result:
        return result.group(1) + '$', result.group(2) + '$'
    
    # TODO: continue with more complicated rules
    # print(rule)
    return None


rules_from_derivbase = defaultdict()
with open(sys.argv[2], mode='r', encoding='U8') as file:
    for line in file:
        line = line.strip()
        if line.startswith('d'):
            label = re.search(r'd[A-Z0-9]+', line).group()
            rule = convert_string_rule_to_regular_expression(next(file).strip())
            if rule:
                rules_from_derivbase[label] = rule


# TODO: apply rules to the extracted data to obtain segmentation
def apply_rules(lemma, rule):
    return None


segmentation_from_derivbase = defaultdict(set)
for lemmas, rule in relations_from_derivbase.items():
    # resolve reversivelly applied rules
    if '*' in rule:
        second, first = lemmas
        rule = rule.replace('*', '')
    else:
        first, second = lemmas

    # proces known rules
    if rules_from_derivbase.get(rule, False):
        for morph in apply_rules(first, rules_from_derivbase[rule]):
            segmentation_from_derivbase[first].add(morph)
        for morph in apply_rules(second, rules_from_derivbase[rule]):
            segmentation_from_derivbase[second].add(morph)
    else:
        segmentation_from_derivbase[first].add(None)
        segmentation_from_derivbase[second].add(None)


# merge all segmented data, resolve overlapping morphs (TODO: as in DerivBaseRU)
# store data in the resulting USeg format (TODO: as in DerivBaseRU)
