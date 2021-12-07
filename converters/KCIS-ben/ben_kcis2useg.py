#!/usr/bin/env python3

import re
import string
import sys
sys.path.append('../../src/')
from useg import SegLex
import unicodedata as ucd

import logging

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    fileHandler = logging.FileHandler(log_file, mode='w')
    l.setLevel(level)
    l.addHandler(fileHandler)

setup_logger('gen_issues', r'general.log')
setup_logger('seg_issues', r'segmentation.log')
setup_logger('pos_issues', r'pos.log')
gen_issues = logging.getLogger('gen_issues')
seg_issues = logging.getLogger('seg_issues')
pos_issues = logging.getLogger('pos_issues')


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" Bengali-SSF-file.csv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

def isascii(str):
    '''Returns True if English'''
    alphabet = list(string.ascii_lowercase)
    for l in alphabet:
        if l in str:
            return True
    return False


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

    features = {k:v for k,v in features.items() if v!=""}

    return features

def longest_common_prefix(s, t):
    '''Finds length of LCP'''
    lcp_len = 0
    while(lcp_len <= min(len(s),len(t)) and s[:lcp_len]==t[:lcp_len]):
        lcp_len += 1
    return lcp_len-1


annot_name = "kcis"
infile = open(sys.argv[1])


# allomorph_sets = {morph:morph_set for morph_set in allomorph_eq_sets for morph in morph_set}

for line in infile:
    entries = line.strip().split("\t")
    lexeme = entries[0].strip("'\"").strip()
    pos = entries[1].strip()
    fs = entries[2].strip()

    if isascii(lexeme):
        continue

    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")

    upos = assign_upos(pos)
    lemma = get_lemma(lexeme, pos, fs)
    features = get_lexeme_features(af, pos)

    lex_id = lexicon.add_lexeme(lexeme, lemma, upos, features=features)

    # if lexeme!= "হাতে":
    #     continue
    #

    if len(af)!=8:
        gen_issues.warning("Lexeme %s has af: %s without enough fields", lexeme, af)
        continue

    if af[7] not in ["", "0"]:

        suffix = af[7]
        root = af[0]

        s_len = longest_common_prefix(lexeme[::-1], suffix[::-1])

        # print(lexeme, suffix, af)
        # for c in lexeme:
        #     print(c, ucd.name(c))
        # print("\n\n")
        # for c in suffix:
        #     print(c, ucd.name(c))
        #
        # print("LCP ", s_len)

        if s_len != 0:
            start = len(lexeme) - s_len
            assert lexeme[-s_len:] == suffix[-s_len:]
            features = {"type":"suffix"}
            lexicon.add_contiguous_morpheme(lex_id, annot_name, start, len(lexeme), features)

            features = {"type":"root"}
            lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, start, features)
        else:
            seg_issues.warning("Suffix %s not at end of wordform %s, af: %s", suffix, lexeme, af)
            # if suffix in allomorph_sets:
            #     for allomorph in allomorph_sets[suffix]:
            #         if wordform[:end].endswith(allomorph):
            #             morph = allomorph

outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
