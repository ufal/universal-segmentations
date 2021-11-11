#!/usr/bin/env python3

import regex as re
from collections import defaultdict
from itertools import combinations

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
    rule = ' '.join(string_rule.split(' ')[:-2])

    # umlaut pattern deletion: (sfx "e" & try uml) vs. (pfx "ge" & opt (uml))
    # COMMENT: umlaut is not morph
    rule = rule.replace('& try uml', '').replace('& opt (uml)', '').replace('& opt uml', '').replace('& try (uml)', '')
    rule = re.sub(r' +', ' ', rule)
    rule = rule.replace(' )', ')')

    # umlaut pattern: (opt uml)
    result = re.search(r'\(opt uml\)$', rule)
    if result:
        return ('e*n$', )

    # prefixation pattern: (pfx "rück")
    result = re.search(r'\(pfx \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return ('^' + result.group(1), )

    # sufixation pattern: (sfx "schaft")
    result = re.search(r'\(sfx \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return (result.group(1) + '$', )

    # re-sufixation pattern: (rsfx "ier" "end")
    result = re.search(r'\(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\s*\)$', rule)
    if result:
        return result.group(1) + '$', result.group(2) + '$'

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
        return result.group(2) + '$', result.group(1) + '$'

    # prefixation and (possible) sufixation pattern: (pfx "ge" & sfx "e") vs. (pfx "an" & opt (sfx "er"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*sfx \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return '^' + result.group(1), result.group(2) + '$'

    # prefixation and (possible) sufixation pattern: (pfx "ge" & sfx "e") vs. (pfx "an" & opt (sfx "er"))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*sfx \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return (result.group(2) + '*' + result.group(1) + '$', )

    # prefixation and possible re-sufixation: (pfx "aus" & try (rsfx "ern" "er"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& try \(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)\s*\)$', rule)
    if result:
        return '^' + result.group(1), result.group(2) + '$', result.group(3) + '$'

    # prefixation and possible de-sufixation: (pfx "durch" & try (dsfx "e"))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& t*r*y*o*p*t* \(dsfx \"(\p{L}+)\"\s*\)\s*\)$', rule)
    if result:
        return '^' + result.group(1), result.group(2) + '$'

    # two re-suffixation pattern: (rsfx "ier" "abel" & try (rsfx "izier" "ikier"))
    result = re.search(r'\(rsfx \"(\p{L}+)\"\s* \"(\p{L}+)\"\s* \& try \(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)\s*\)$', rule)
    if result:
        return result.group(1) + 'e*n*$', result.group(3) + 'e*n*$', result.group(2) + '$', result.group(4) + '$'

    # sufixation and list of re-sufixation patern: (sfx "at" & try (asfx [("a",""), ("en",""), ("ium",""), ("um","")]))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s* \& try \(asfx \[\(\"', rule)
    if result:
        res = re.findall(r'\"(\p{L}*)\"', rule)
        suf, asf = res[0], res[1:]
        target = set()
        for _, asf2 in zip(asf[0::2], asf[1::2]):
            target.add(asf2 + suf + '$')
        return tuple(target)

    # prefixation and list of re-prefixation patern: (pfx "de" & try (apfx [("a","sa"), ("e","se"), ("i","si"), ("o","so"), ("u","su")]))
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& try \(apfx \[\(\"', rule)
    if result:
        return ('^' + result.group(1), )

    # prefixation and re-infixation pattern: (pfx "ge" & rifx "i" "a")
    result = re.search(r'\(pfx \"(\p{L}+)\"\s* \& o*p*t*\s*\(*rifx \"(\p{L}+)\"\s* \"(\p{L}+)\"\s*\)*\s*\)$', rule)
    if result:
        return ('^' + result.group(1), )

    # sufixation and (possible) re-sufixation pattern: (sfx "er" & try (rsfx "el" "l"))
    result = re.search(r'\(sfx \"(\p{L}+)\"\s*\& t*r*y*o*p*t*\s*\(rsfx \"(\p{L}+)\" \"(\p{L}+)\"\)*$', rule)
    if result:
        return (result.group(1) + '$', )

    # complex rules regarding vocal/consonant changes, not morphs
    if '|' in rule:
        # sufixation
        result = re.search(r'\(sfx \"(\p{L}+)\"\s* \&', rule)
        if result:
            return result.group(1) + 'e*n*$', 'e*n$'
        
        # prefixation
        result = re.search(r'\(pfx \"(\p{L}+)\"\s* \&', rule)
        if result:
            return '^' + result.group(1), 'e*n$'

    # COMMENT: There are still some non-processed derivational rules because of their complexity.
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


# apply rules to the extracted data to obtain segmentation
# carfully about capitalised letters
def apply_rules(lemma, rules):
    lemma = lemma.split('_')[0].lower()

    morphs = list()
    for r in rules:
        result = re.search(r, lemma)
        if result:
            morphs.append((result.group(), result.span()))

    return morphs


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


# merge all segmented data, resolve overlapping morphs
# function for finding overlap between intervals
def find_overlap(a, b):
    for item in a:
        if item in b:
            return True
    return False


# function for constructing segmentation from non-overlapping morphs
def create_segmentation(lemma, ranges, operations):
    whole_interval = list(range(len(lemma)))
    for interval in ranges:
        for item in interval:
            whole_interval.remove(item)
    
    ranges.append(whole_interval)
    operations.append('STEM')

    ranges, operations = zip(*sorted(zip(ranges, operations)))

    morphs = ['' for _ in range(len(ranges))]
    for idx_interval in range(len(ranges)):
        for number in ranges[idx_interval]:
            morphs[idx_interval] += lemma[number]

    return [morphs, operations]


# function for searching for segmentation from overlapping morphs
def search_for_segmentation(lemma, ranges, operations):
    # check types of overlaps of the morph boundaries
    sorted_ranges = sorted(ranges, key=len)
    for idx_interval in range(len(sorted_ranges)-1):
        for idx_next_interval in range(idx_interval, len(sorted_ranges)):
            if any(index in sorted_ranges[idx_next_interval] for index in sorted_ranges[idx_interval]):  # check whether there is any overlapping index
                if not set(sorted_ranges[idx_interval]).issubset(sorted_ranges[idx_next_interval]):  # check whether there is an overlap across morph boundaries
                    logging.warning(
                        'There is a trouble with overlapping morph boundaries: {}, {}, {}'
                        .format(lemma, ranges, operations)
                    )
                    return [[lemma], ['STEM']]

    # non-problematic cases of overlapping morph boundaries
    new_ranges, new_operations = zip(*sorted(zip(ranges, operations), key=lambda x: len(x[0])))
    for idx_interval in range(len(new_ranges)-1):
        for idx_next_interval in range(idx_interval+1, len(new_ranges)):
            for item in new_ranges[idx_interval]:
                if item in new_ranges[idx_next_interval]:  # check whether there is any overlapping index
                    new_ranges[idx_next_interval].remove(item)

    new_ranges, new_operations = list(new_ranges), list(new_operations)
    to_delete = list()
    for index, interval in enumerate(new_ranges):
        if len(interval) == 0:
            to_delete.append(index)
    for index in sorted(to_delete, reverse=True):
        del new_ranges[index]
        del new_operations[index]

    return create_segmentation(lemma, new_ranges, new_operations)


# go through segmented lemmas and resolve overlapping morphs
new_segmented_lemmas = defaultdict()
for item, segments in segmentation_from_derivbase.items():
    if '_' not in item:
        continue

    lemma, pos = item.split('_')
    
    # 1. non-segmented lexemes
    if segments == {None}:  # segment basically
        new_segmented_lemmas[item] = [[lemma], ['STEM']]
        continue

    # 2. segmented lexemes
    if None in segments:
        segments.remove(None)

    if len(segments) == 1:  # segment basically
        morph, indices = list(segments)[0]
        segmentation = [[], []]
        
        morph_before = lemma[:indices[0]]
        if morph_before:
            segmentation[0].append(morph_before)
            segmentation[1].append('STEM')
        
        morph_marked = lemma[indices[0]:indices[1]]
        segmentation[0].append(morph_marked)
        segmentation[1].append('')
        
        morph_after = lemma[indices[1]:]
        if morph_after:
            segmentation[0].append(morph_after)
            segmentation[1].append('STEM')

        new_segmented_lemmas[item] = segmentation

    else:  # resolve overlapping morphs and segment lexeme
        segments = sorted(list(segments), key=lambda x:len(x[0]))
        ranges = [list(range(segment[1][0], segment[1][1])) for segment in segments]
        operations = [''*len(segments)]

        # find out whether there is an overlap between morphs
        there_is_overlap = False
        for first, second in combinations(ranges, 2):
            if find_overlap(first, second):
                there_is_overlap = True
                break

        # segment lexeme
        if there_is_overlap:
            segmentation = search_for_segmentation(lemma, ranges, operations)
            pass
        else:
            segmentation = create_segmentation(lemma, ranges, operations)

        new_segmented_lemmas[item] = segmentation


# function for flatening the given list (max 1 list inside)
def flatten(t):
    result = list()
    for item in t:
        if type(item) is list:
            for subitem in item:
                result.append(subitem)
        else:
            result.append(item)
    return result


# find segmentation of STEMs in the resource
lemmaset = {key.split('_')[0]: key.split('_')[1] for key in new_segmented_lemmas.keys()}
any_change = False
while any_change is False:
    any_change = False
    for entry, segmentation in new_segmented_lemmas.items():
        lemma, pos = entry.split('_')
        morphs, labels = segmentation

        # find stems and try to segment them
        stems = list()
        for i in range(len(labels)):
            if labels[i] == 'STEM':
                if morphs[i] in lemmaset:
                    stem_segmentation = new_segmented_lemmas['_'.join((morphs[i], lemmaset[morphs[i]]))]
                    if len(stem_segmentation[0]) > 1:
                        stems.append((morphs[i], i, stem_segmentation))
                        any_change = True
        if len(stems) == 0:
            continue

        # change the unsegmented stems to segmented ones
        morphs, labels = list(morphs), list(labels)
        for stem, idx, segm in stems:
            morphs[idx] = segm[0]
            labels[idx] = segm[1]
        
        # flaten the list of morphs and labels
        morphs = flatten(morphs)
        labels = flatten(labels)

        # save into the data
        new_segmented_lemmas[entry] = [morphs, labels]


# store data in the resulting USeg format
lexicon = SegLex()

parse_pos = {'N': 'NOUN', 'V': 'VERB', 'A': 'ADJ'}  # gender is deleted
for entry, segmentation in new_segmented_lemmas.items():
    morphs, labels = segmentation
    lemma, pos = entry.split('_')

    lexeme = lexicon.add_lexeme(lemma, lemma, parse_pos.get(pos[0], 'X'))

    start, seen_stem = 0, False
    for morph, label in zip(morphs, labels):
        if label != '':
            seen_stem = True
            lexicon.add_contiguous_morpheme(
                lex_id=lexeme,
                annot_name='?TODO?',
                start=start,
                end=start + len(morph),
                features={'type': 'unsegmented' if label == 'STEM' else label}
            )
        elif not seen_stem:
            lexicon.add_contiguous_morpheme(
                lex_id=lexeme,
                annot_name='?TODO?',
                start=start,
                end=start + len(morph),
                features={'type': 'prefix'}
            )
        else:
            lexicon.add_contiguous_morpheme(
                lex_id=lexeme,
                annot_name='?TODO?',
                start=start,
                end=start + len(morph),
                features={'type': 'suffix'}
            )
        start = start+len(morph)

with open(sys.argv[3], mode='w', encoding='U8') as outfile:
    lexicon.save(outfile)
