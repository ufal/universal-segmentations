#!/usr/bin/env python3

import csv
from email.mime import base
from email.policy import default
import regex as re
from collections import defaultdict

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
                    segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'PTFX'))
                    break

        elif operation == 'INTERFIX':
            # COMMENT: No information about segmentation.
            continue

        else:
            print('Missing code for the given operation:', operation)
        
        # according to part-of-speech category
        if deri_pos == 'verb' and (deriv_lemma.endswith('ть') or deriv_lemma.endswith('ться')):
            found = re.search(r'ть(ся)*$', deriv_lemma)
            if 'ся' in found.group():
                span_start = found.span(0)[0]
                span_end = found.span(0)[1] - 2
                morph = 'ть'
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((morph, (span_start, span_end), 'END-inf'))
            else:
                segmented_lemmas['_'.join([deriv_lemma, deri_pos])].add((found.group(), found.span(0), 'END-inf'))


# TODO: go through segmented lemmas and resolve overlaping morphs
print(segmented_lemmas)


# TODO: upload to the resulting format
# lexicon = SegLex()

# with open(sys.argv[2], mode='w', encoding='U8') as outfile:
#     lexicon.save(outfile)

# lexicon.add_contiguous_morpheme(
#     lex_id=lexeme,
#     annot_name='?TODO?',
#     start=init_index,
#     end=init_index + len(morph),
#     features={'morph': morph, 'morpheme': '?TODO?', 'type': '?TODO?'}
# )
