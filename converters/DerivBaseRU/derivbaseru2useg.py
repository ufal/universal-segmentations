#!/usr/bin/env python3

import csv
import regex as re
from collections import defaultdict
from itertools import combinations

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" DerivBaseRU-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")


# load data and found segmentation
segmented_lemmas = defaultdict(set)
with open(sys.argv[1], mode='r', encoding='U8') as infile:
    reader = csv.reader(infile, delimiter='\t')
    header = next(reader)
    for base_lemma, base_pos, deriv_lemma, deri_pos, rule, operation in reader:
        # add (so far) unsegmented lemmas
        if not segmented_lemmas.get('_'.join([deriv_lemma, deri_pos]), False):
            segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add(None)
        if not segmented_lemmas.get('_'.join([base_lemma, base_pos]), False):
            segmented_lemmas['_'.join([base_lemma, base_pos])].add(None)

        # clean string of the rule
        rule = rule.replace(' + ', '+')
        rule = re.search(r'\(.*\)', rule).group(0)[1:-1]
        if '->' in rule:
            rule = re.search(r'.* ->', rule).group(0)[:-3]

        # individual morphological operations in the data
        if operation == 'SFX':
            morphs = re.search(r'\+(.*)$', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search(morph + '$', deriv_lemma)
                if found:
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'SFX'))
                    break

        elif operation == '0SFX':
            # COMMENT: No information about segmentation.
            continue

        elif operation == 'PFX':
            morphs = re.search(r'^(.*)\+', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search('^' + morph, deriv_lemma)
                if found:
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PFX'))
                    break

        elif operation == 'PFX,SFX':
            morphs = re.search(r'^(.*?)\+', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search('^' + morph, deriv_lemma)
                if found:
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PFX'))
                    break

            morphs = re.search(r'\+(.*)$', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search(morph + '$', deriv_lemma)
                if found:
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'SFX'))
                    break

        elif operation == 'SFX,PTFX':
            # COMMENT: sfx part is not clear because of segmentation of infinitive forms;
            # this part proposes to segment 'спесив-ить-ся' instead of 'спесив-и-ть-ся'
            # (it can be done additionally for all verbs)
            if deriv_lemma.endswith('ся'):
                found = re.search(r'ся$', deriv_lemma)
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PTFX'))

        elif operation == 'PFX,SFX,PTFX':
            # COMMENT: sfx part is not clear because of segmentation of infinitive forms (as above);
            morphs = re.search(r'^(.*?)\+', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search('^' + morph, deriv_lemma)
                if found:
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PFX'))
                    break
            
            if deriv_lemma.endswith('ся'):
                found = re.search(r'ся$', deriv_lemma)
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PTFX'))

        elif operation == 'CONV':
            # COMMENT: No information about segmentation.
            continue

        elif operation == 'PTFX':
            if deriv_lemma.endswith('ся'):
                found = re.search(r'ся$', deriv_lemma)
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PTFX'))

        elif operation == 'PFX,PTFX':
            morphs = re.search(r'^(.*?)\+', rule).group(1).split('/')
            morphs = sorted(morphs, key=len, reverse=True)
            for morph in morphs:
                morph = morph.replace('(', '[').replace(')', ']*')
                found = re.search('^' + morph, deriv_lemma)
                if found and deriv_lemma.endswith('ся'):
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PFX'))
                    found_sja = re.search(r'ся$', deriv_lemma)
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found_sja.group(), found_sja.span(0), 'PTFX'))
                    break

        elif operation == 'INTERFIX':
            # COMMENT: No information about segmentation.
            continue

        else:
            logging.warning('Missing code for the given operation: {}'.format(operation))

        # according to part-of-speech category
        if deri_pos == 'verb' and (deriv_lemma.endswith('ть') or deriv_lemma.endswith('ться')):
            found = re.search(r'ть(ся)*$', deriv_lemma)
            if 'ся' in found.group():
                span_start = found.span(0)[0]
                span_end = found.span(0)[1] - 2
                morph = 'ть'
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((morph, (span_start, span_end), 'END-inf'))
                span_start = found.span(0)[0] + 2
                span_end = found.span(0)[1]
                morph = 'ся'
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PTFX'))
            else:
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'END-inf'))


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
for item, segments in segmented_lemmas.items():
    lemma, pos = item.split('_')
    
    # 1. non-segmented lexemes
    if segments == {None}:  # segment basically
        new_segmented_lemmas[item] = [[lemma], ['STEM']]
        continue

    # 2. segmented lexemes
    segments.remove(None)
    if len(segments) == 1:  # segment basically
        morph, indices, operation = list(segments)[0]
        segmentation = [[], []]
        
        morph_before = lemma[:indices[0]]
        if morph_before:
            segmentation[0].append(morph_before)
            segmentation[1].append('STEM')
        
        morph_marked = lemma[indices[0]:indices[1]]
        segmentation[0].append(morph_marked)
        segmentation[1].append(operation)
        
        morph_after = lemma[indices[1]:]
        if morph_after:
            segmentation[0].append(morph_after)
            segmentation[1].append('STEM')

        new_segmented_lemmas[item] = segmentation

    else:  # resolve overlapping morphs and segment lexeme
        segments = sorted(list(segments), key=lambda x:len(x[0]))
        ranges = [list(range(segment[1][0], segment[1][1])) for segment in segments]
        operations = [segment[2] for segment in segments]

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


# store in the resulting format
lexicon = SegLex()

for entry, segmentation in new_segmented_lemmas.items():
    morphs, labels = segmentation
    lemma, pos = entry.split('_')

    lexeme = lexicon.add_lexeme(lemma, lemma, '?TODO?')

    start = 0
    for morph, label in zip(morphs, labels):
        print(morph, label, start, start + len(morph) - 1)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme,
            annot_name='?TODO?',
            start=start,
            end=start + len(morph) - 1,
            features={'morpheme': '?TODO?', 'type': 'UNSEG' if label == 'STEM' else label}
        )
        start = start+len(morph)

with open(sys.argv[2], mode='w', encoding='U8') as outfile:
    lexicon.save(outfile)
