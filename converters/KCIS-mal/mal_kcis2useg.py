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
    sys.stderr.write("Usage:\n  "+__file__+" Kannada-SSF-file.csv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

def longest_common_prefix(s, t):
    '''Finds length of LCP'''
    lcp_len = 0
    while(lcp_len <= min(len(s),len(t)) and s[:lcp_len]==t[:lcp_len]):
        lcp_len += 1
    return lcp_len-1

def find_morph_boundaries(lexeme, morph, req_start = -1):
    '''Finds morph boundaries'''

    # if req_start==0:
    #     return 0, longest_common_prefix(lexeme, morph)

    for i in range(len(morph)):
        # print(i)
        # print(morph[:len(morph)-i])
        # morph_start = lexeme.find(morph[:len(morph)-i])
        shortened_morph = morph[:len(morph)-i]

        best_start, best_end = -1, -1

        for match in re.finditer(shortened_morph, lexeme):
            current_start, current_end = -1, -1
            morph_start, morph_end = match.start(), match.end()

            allowed_interfix_len = len(lexeme)
            if morph_start <= req_start + allowed_interfix_len and morph_start >= req_start:
                current_start, current_end = morph_start, morph_end
                #If more than 1 matches for same length, choose the one closest to req_start
                if best_start == -1:
                    best_start, best_end = current_start, current_end

                if current_start != -1 and abs(current_start - req_start) < abs(best_start - req_start):
                    best_start, best_end = current_start, current_end

        if best_start != -1 and best_start != best_end:
            return best_start, best_end

    return -1,-1



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

def get_lemma(lexeme, pos, fs):
    '''Returns lemma'''
    return lexeme

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
    features["person"] = af[7]
    features["AnnCorra_tag"] = pos
    return features


annot_name = "kcis"
infile = open(sys.argv[1])

for line in infile:
    if line == "\n" or line == " ":
        continue
    entries = line.strip().split("\t")
    lexeme = entries[0].strip("'\"").strip()
    pos = entries[1].strip()
    fs = entries[2].strip()

    if len(lexeme)==0:
        continue
    if "af" not in fs:
        continue
    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")

    if lexeme != "അംബാനിയുടെയും":
        continue

    upos = assign_upos(pos)
    lemma = get_lemma(lexeme, pos, fs)
    features = get_lexeme_features(af, pos)

    lex_id = lexicon.add_lexeme(lexeme, lemma, upos, features)

    if len(af)!=8:
        gen_issues.warning("Lexeme %s has af: %s without enough fields", lexeme, af)
        continue



    morpheme_seq = [af[0]]
    if af[6] in ["","0"]:
        continue
    else:
        morpheme_seq += af[6].split("+")


    start = 0
    for midx, morpheme in enumerate(morpheme_seq):

        morph_start, morph_end = find_morph_boundaries(lexeme, morpheme, req_start = start)

        if morph_start != -1 and morph_end != -1:
            start_of_next_morpheme = len(lexeme)
            if midx < len(morpheme_seq)-1:
                start_of_next_morpheme, end_of_next_morpheme = find_morph_boundaries(lexeme, morpheme_seq[midx+1], req_start = morph_end)
                if start_of_next_morpheme != -1:
                    morph_end = start_of_next_morpheme

            # if morph_start > start:
            #     lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"interfix"})
            #     seg_issues.warning("Interfix added at position %s, %s, of wordform %s, af: %s", start, morph_start, lexeme, af)
            if midx == 0 and morph_start != 0:
                lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, morph_start, {"type":"prefix"})

            features = dict()
            features["type"] = "root" if midx == 0 else "suffix"

            lexicon.add_contiguous_morpheme(lex_id, annot_name, morph_start, morph_end, features)
        else:
            if start == 0:
                seg_issues.warning("Root %s not at position %s, of wordform %s, af: %s", morpheme, start, lexeme, af)
            else:
                seg_issues.warning("Morpheme %s not at position %s, of wordform %s, af: %s", morpheme, start, lexeme, af)
            continue

        print(lexeme, "\t", morpheme,"\t", morph_start, morph_end, "\t", af)
        print(lexeme[morph_start:morph_end], "\t",len(morpheme), len(lexeme))
        print(morpheme_seq,"\t", midx)
        print(start_of_next_morpheme, end_of_next_morpheme)
        print("\n\n\n")

        if start_of_next_morpheme != -1:
            start = start_of_next_morpheme


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
