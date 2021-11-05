#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex

import logging
logging.basicConfig(filename="unsolved.log", level=logging.WARNING)

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" Italian-DerIvaTario-file.csv converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

def assign_upos(lexeme):
    '''Finds lexeme in UDer and its POS'''
    return "NOUN"

def longest_common_prefix(s, t):
    '''Finds length of LCP'''
    lcp_len = 0
    while(lcp_len <= min(len(s),len(t)) and s[:lcp_len]==t[:lcp_len]):
        lcp_len += 1
    return lcp_len-1

def find_morph_boundaries(lexeme, morph):
    '''Finds boundaries of allomorph'''
    # if is_prefix:
    #     return 0, longest_common_prefix(lexeme, morph)
    morph_start = 0
    for i in range(len(morph)):
        # print(i)
        # print(morph[:len(morph)-i])
        morph_start = lexeme.find(morph[:len(morph)-i])
        # print(morph_start)
        if morph_start != -1:
            return morph_start, morph_start+len(morph)-i
    return -1,-1


# print(find_morph_boundaries("vacation", "cat", False))

lexicon = SegLex()

infile = open(sys.argv[1])

annot_name = "DerIvaTario"

prefixes = {"acons", "anti", "auto", "bi", "de", "dis", "in", "micro", "ri", "1s", "2s", "co", "neo", "1in", "2in"}
root_types = {"adj_th", "dnt_root", "ltn_pp", "presp", "pst_ptcp", "root", "suppl", "unrec", "vrb_th"}


for line in infile:
    entries = [s.lower() for s in line.strip().split(";")]
    entries = list(filter(lambda f: f!="", entries))
    lexeme = entries[1]
    root = entries[2].split(":")
    # if lexeme!="anti-riscaldamento":
    #     continue


    if len(root) < 2:
        logging.warning("Root %s does not have 2 fields", root)
        continue
    if len(entries) <= 2:
        logging.warning("Lexeme %s only has root", lexeme)

    upos = assign_upos(lexeme)
    features = {"upos": upos, "other_info":""}
    lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features=features)

    info_morphemes = entries[2:]
    # print("lexeme ", lexeme)
    # print("info_morpheme ", info_morphemes)
    #Arranging morphemes according to order in wordform
    morpheme_seq = []
    for info_morpheme in info_morphemes:
        # print(info_morpheme.split(":")[0])
        if info_morpheme.split(":")[0] in prefixes:
            morpheme_seq = [info_morpheme] + morpheme_seq
        else:
            morpheme_seq = morpheme_seq + [info_morpheme]

    start = 0

    root_not_found = False
    for info_morpheme in morpheme_seq:
        is_root = False
        if info_morpheme.split(":")[0] == "conversion":
            continue

        if len(info_morpheme.split(":")) < 2:
            # print("0")
            logging.warning("Empty morph %s of lexeme %s", info_morpheme, lexeme)
            continue

        if info_morpheme.split(":")[1] in root_types:
            is_root = True

        if info_morpheme.split(":")[0] == "baseless":
            root_not_found = True
            continue

        if is_root:
            allomorph = info_morpheme.split(":")[0]
        else:
            allomorph = info_morpheme.split(":")[1]
        morpheme = info_morpheme.split(":")[0]
        morph_start, morph_end = find_morph_boundaries(lexeme, allomorph)
        # print("New field: ")
        # print(info_morpheme)
        # print(morpheme, allomorph, morph_start, morph_end)
        if morph_start == -1:
            # print("1")
            logging.warning("Morph %s not found in lexeme %s with entry %s", morpheme, lexeme, line)
            continue
        if morph_start < start:
            # print("2")
            logging.warning("Morph %s overlaps with previous morpheme in lexeme %s with entry %s", morpheme, lexeme, line)
            # continue
        if morph_start == morph_end:
            # print("3")
            logging.warning("Empty morph %s in lexeme %s with entry %s", allomorph, lexeme, line)
            continue

        if morph_start > start:
            if root_not_found:
                lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"stem"})
                root_not_found = False
            else:
                lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"interfix"})

        lexicon.add_contiguous_morpheme(lex_id, annot_name, morph_start, morph_end, features={})
        # print(start)
        # print(len_lcp)
        # print(lexeme, start, end, allomorph)
        start = morph_end


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
