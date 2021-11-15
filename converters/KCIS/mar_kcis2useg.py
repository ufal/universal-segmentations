#!/usr/bin/env python3

import re
import sys
sys.path.append('../../src/')
from useg import SegLex


import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    fileHandler = logging.FileHandler(log_file, mode='w')
    l.setLevel(level)
    l.addHandler(fileHandler)

setup_logger('gen_issues', r'general.log')
setup_logger('seg_issues', r'segmentation.log')
setup_logger('boundary_overlap_issues', r'boundary_overlaps.log')
setup_logger('pos_issues', r'pos.log')
gen_issues = logging.getLogger('gen_issues')
seg_issues = logging.getLogger('seg_issues')
pos_issues = logging.getLogger('pos_issues')
boundary_overlap_issues = logging.getLogger('boundary_overlap_issues')

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" Marathi-SSF-file.csv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

def assign_upos(pos):
    '''Maps POS to UPOS'''
    return pos

def get_lemma(wordform, pos, fs):
    '''Returns lemma'''
    return wordform

def get_lexeme_features(af):
    '''Extracts and translates features from af'''
    features = dict()
    features["root"] = af[0]
    #features["gender"] ...
    return features


annot_name = "kcis"
infile = open(sys.argv[1])

for line in infile:
    entries = line.strip().split("\t")
    wordform = entries[0].strip("'\"").strip()
    pos = entries[1].strip()
    fs = entries[2].strip()

    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")

    upos = assign_upos(pos)
    lemma = get_lemma(wordform, pos, fs)
    features = get_lexeme_features(af)

    lex_id = lexicon.add_lexeme(wordform, lemma, upos, features)

    if len(af)!=8:
        print(af)
        continue

    if af[7] != "":
        suffixes = af[7].split("_")
        suffixes.reverse()
        end = len(wordform)
        for suffix in suffixes[:-1]:
            features = {"info":""}
            start = len(wordform[:end]) - len(suffix)
            if not wordform[:end].endswith(suffix):
                print(wordform, suffix, af)
                print(start, end)
                continue

            lexicon.add_contiguous_morpheme(lex_id, annot_name, start, end, features)
            end = start


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
