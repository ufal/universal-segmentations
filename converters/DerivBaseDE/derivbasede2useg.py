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

    # umlaut pattern deletion: (sfx "e" & try uml) vs. (pfx "ge" & opt (uml))
    # COMMENT: umlaut is not morph
    rule = rule.replace('& try uml', '').replace('& opt (uml)', '').replace('& opt uml', '').replace('& try (uml)', '')
    rule = re.sub(r' +', ' ', rule)
    rule = rule.replace(' )', ')')

    # umlaut pattern: (opt uml)
    result = re.search(r'\(opt uml\)$', rule)
    if result:
        return 'only_target', 'e*n$'

    # prefixation pattern: (pfx "rück")
    result = re.search(r'\(pfx \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return 'only_target', '^' + result.group(1)

    # sufixation pattern: (sfx "schaft")
    result = re.search(r'\(sfx \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return 'only_target', result.group(1) + '$'

    # re-sufixation pattern: (rsfx "ier" "end")
    result = re.search(r'\(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return 'base_target', result.group(1) + '$', result.group(2) + '$'

    # empty pattern: nul
    if rule == 'nul':
        # COMMENT: too difficult to parse
        return None

    # re-infixation pattern: (rifx "e" "u")
    result = re.search(r'\(rifx \"(\p{L}+)\" \"(\p{L}+)\"\s*\)$', rule)
    if result:
        # COMMENT: too difficult to parse, conceptual problem with definition of morph
        return None

    # sufixation and possible de-suffixation pattern: (sfx "ei" & try (dsfx "e"))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s* \& try \(dsfx \"(\p{L}+)\"\s*\)\s*\)$', rule)
    if result:
        return 'base_target', result.group(2) + '$', result.group(1) + '$'

    # prefixation and (possible) sufixation pattern: (pfx "ge" & sfx "e") vs. (pfx "an" & opt (sfx "er"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*sfx \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return 'only_target', '^' + result.group(1), result.group(2) + '$'

    # prefixation and (possible) sufixation pattern: (pfx "ge" & sfx "e") vs. (pfx "an" & opt (sfx "er"))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*sfx \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return 'only_target', result.group(2) + '*' + result.group(1) + '$'

    # prefixation and possible re-sufixation: (pfx "aus" & try (rsfx "ern" "er"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& try \(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)\s*\)$', rule)
    if result:
        return 'base_target', ('^' + result.group(1), result.group(2) + '$'), result.group(3) + '$'

    # prefixation and possible de-sufixation: (pfx "durch" & try (dsfx "e"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& t*r*y*o*p*t* \(dsfx \"(\p{L}+)\"\s*\)\s*\)$', rule)
    if result:
        return 'only_target', '^' + result.group(1), result.group(2) + '$'

    # two re-suffixation pattern: (rsfx "ier" "abel" & try (rsfx "izier" "ikier"))
    result = re.search(r'\(rsfx \"(\p{L}+)\"\s* \"(\p{L}+)\"\s* \& try \(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)\s*\)$', rule)
    if result:
        return 'base_target', (result.group(1) + 'e*n*$', result.group(3) + 'e*n*$'), (result.group(2) + '$', result.group(4) + '$')

    # sufixation and list of re-sufixation patern: (sfx "at" & try (asfx [("a",""), ("en",""), ("ium",""), ("um","")]))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s* \& try \(asfx \[\(\"', rule)
    if result:
        res = re.findall(r'\"(\p{L}*)\"', rule)
        suf, asf = res[0], res[1:]
        target = set()
        for _, asf2 in zip(asf[0::2], asf[1::2]):
            target.add(asf2 + suf + '$')
        return 'only_target', tuple(target)

    # prefixation and list of re-prefixation patern: (pfx "de" & try (apfx [("a","sa"), ("e","se"), ("i","si"), ("o","so"), ("u","su")]))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& try \(apfx \[\(\"', rule)
    if result:
        return 'only_target', '^' + result.group(1)

    # prefixation and re-infixation pattern: (pfx "ge" & rifx "i" "a")
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*rifx \"(\p{L}+)\"\s* \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return 'only_target', '^' + result.group(1)

    if '|' in rule:  # TODO: FIX complex rules
        return None

    # TODO: continue with more complicated rules
    print(rule)
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
# carfully about capitalised letters
def apply_rules(lemma, rule):
    return []


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
