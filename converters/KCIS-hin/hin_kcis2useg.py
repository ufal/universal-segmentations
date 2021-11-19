#!/usr/bin/env python3

import re
import string
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
    if pos.startswith("D"):
        upos = "DET"
    if pos.startswith("N"):
        upos = "NOUN"
    if pos.startswith("NNP"):
        upos = "PROPN"
    if pos.startswith("PR"):
        upos = "PRON"
    if pos.startswith("PSP"):
        upos = "ADP"
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
    if pos.startswith("Q"):
        upos = "NUM"
    if pos.startswith("CC"):
        upos = "SCONJ|CCONJ"
    if pos.startswith("INTF"):
        upos = "ADV"


    if upos=="":
        pos_issues.warning("POS %s not assigned ", pos)
        return "UNK"

    return upos


def isascii(str):
    '''Returns True if English'''
    alphabet = list(string.ascii_lowercase)
    for l in alphabet:
        if l in str:
            return True
    return False

def get_lemma(wordform, pos, fs):
    '''Returns lemma'''
    return wordform

def get_lexeme_features(af, pos):
    '''Extracts and translates features from af'''
    features = dict()
    features["root"] = af[0]

    if isascii(af[0]):
        del features["root"]

    if len(af)!=8:
        return features

    lcats = {"n", "adj", "avy", "adv", "num", "psp", "v", "any"}
    genders = {"f", "m", "n", "any"}
    numbers = {"sg", "pl", "any"}
    persons = {"1", "2", "3", "1h", "2h", "3h" "any"}
    cases = {"d", "o", "any"}


    features["lcat"] = af[1] if af[1] in lcats else ""
    features["gender"] = af[2] if af[2] in genders else ""
    features["number"] = af[3] if af[3] in numbers else ""
    features["person"] = af[4] if af[4] in persons else ""
    features["case"] = af[5] if af[5] in cases else ""

    if assign_upos(pos).startswith("N"):
        features["case_marker"] = af[6]
    if assign_upos(pos).startswith("V"):
        features["tam_marker"] = af[6]

    features["AnnCorra_tag"] = pos

    features = {k:v for k,v in features.items() if v not in ["", "0"]}

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

    if af[6] not in ["","0"] and isascii(af[6])==False:
        suffixes = af[6].split("_")

        # suffixes.reverse()
        # if wordform.endswith(suffixes[0]):
        #     start = len(wordform[:end]) - len(suffix)
        #
        if len(suffixes)==2:
            suffixes.reverse()
            lexicon.add_contiguous_morpheme(lex_id, annot_name, len(wordform)-len(suffixes[0]), len(wordform), features={"type":"suffix", "morpheme":suffixes[0]})
            lexicon.add_contiguous_morpheme(lex_id, annot_name, len(wordform)-len(suffixes[0])-len(suffixes[1]), len(wordform)-len(suffixes[0]), features={"type":"suffix", "morpheme":suffixes[1]})
            lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(wordform)-len(suffixes[0])-len(suffixes[1]), features={"type":"root"})
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
