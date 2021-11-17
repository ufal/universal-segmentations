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
    sys.stderr.write("Usage:\n  "+__file__+" Hindi-SSF-file.csv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

def assign_upos(pos):
    '''Maps POS to UPOS'''
    upos = ""
    if pos.startswith("N"):
        upos = "NOUN"
    if pos.startswith("NNP"):
        upos = "PROPN"
    if pos.startswith("NNP"):
        upos = "NOUN"
    if pos.startswith("V"):
        upos = "VERB"
    if "VAU" in pos or "VAU" in pos:
        upos = "AUX"
    if pos.startswith("X"):
        upos = "X"
    if pos.startswith("RP"):
        upos = "PART"
    if pos.startswith("J"):
        upos = "JJ"
    if pos.startswith("RB"):
        upos = "ADV"
    if pos.startswith("PR"):
        upos = "ADP"

    if upos=="":
        pos_issues.warning("POS %s not assigned ", pos)

    return upos

def get_lemma(wordform, pos, fs):
    '''Returns lemma'''
    return wordform

def get_lexeme_features(af, pos):
    '''Extracts and translates features from af'''
    features = dict()
    features["root"] = af[0]
    if len(features)!=8:
        return features
    features["lcat"] = af[1]
    features["gender"] = af[2]
    features["number"] = af[3]
    features["person"] = af[4]
    features["case"] = af[6]
    # features["person"] = af[7]
    features["AnnCorra_tag"] = pos
    return features


def longest_common_prefix(s, t):
    '''Finds length of LCP'''
    lcp_len = 0
    while(lcp_len <= min(len(s),len(t)) and s[:lcp_len]==t[:lcp_len]):
        lcp_len += 1
    return lcp_len-1



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
    features = get_lexeme_features(af, pos)

    lex_id = lexicon.add_lexeme(wordform, lemma, upos, features)

    if len(af)!=8:
        gen_issues.warning("Wordform %s has af: %s without enough fields", wordform, af)
        continue

    if af[6] not in ["","0"]:
        suffixes = af[6].split("_")

        # suffixes.reverse()
        # if wordform.endswith(suffixes[0]):
        #     start = len(wordform[:end]) - len(suffix)
        #
        if len(suffixes)==2:
            continue
        root = af[0]
        root_length = longest_common_prefix(wordform, root)
        if root_length==0:
            seg_issues.warning("Root %s not in wordform %s ", root, wordform)
            continue
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, root_length, features={"type":"root"})
        lexicon.add_contiguous_morpheme(lex_id, annot_name, root_length, len(wordform), features={"type":"suffix", "morpheme":suffixes[0]})


        # end = len(wordform)
        # # if len(suffixes)>1:
        #     # suffixes = suffixes[:-1]
        # for suffix in suffixes:
        #     features = {"info":""}
        #     start = len(wordform[:end]) - len(suffix)
        #     if not wordform[:end].endswith(suffix):
        #         seg_issues.warning("Suffix %s not at position %s, %s, of wordform %s, af: %s", suffix, start, end, wordform, af)
        #         # print(wordform, suffix, af)
        #         # print(start, end)
        #         continue
        #
        #     lexicon.add_contiguous_morpheme(lex_id, annot_name, start, end, features)
        #     end = start
        # lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, end, features={"type":"root"})


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
