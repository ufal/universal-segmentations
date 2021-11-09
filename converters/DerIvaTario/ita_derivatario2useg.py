#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex

import logging
# logging.basicConfig(filename="unsolved.log", level=logging.WARNING)

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    # formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    # fileHandler.setFormatter(formatter)
    # streamHandler = logging.StreamHandler()
    # streamHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)
    # l.addHandler(streamHandler)

setup_logger('gen_issues', r'general.log')
setup_logger('seg_issues', r'segmentation.log')
setup_logger('boundary_overlap_issues', r'boundary_overlaps.log')
setup_logger('pos_issues', r'pos.log')
gen_issues = logging.getLogger('gen_issues')
seg_issues = logging.getLogger('seg_issues')
pos_issues = logging.getLogger('pos_issues')
boundary_overlap_issues = logging.getLogger('boundary_overlap_issues')

if len(sys.argv) != 4:
    sys.stderr.write("Usage:\n  "+__file__+" Italian-DerIvaTario-file.csv UDer-Italian-file.tsv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[3]}")

def initialize_all_upos():
    '''Reads UDer file and converts to dictionary'''
    uder = open(sys.argv[2])
    upos_assignment = dict()
    for line in uder:
        if line == "\n" or line == " ":
            continue
        word, upos = line.split("\t")[1].strip().split("#")
        if word in upos_assignment and upos_assignment[word] != upos:
            # logging.warning("Word %s has more than 1 POS: %s, %s ", word, upos_assignment[word], upos)
            upos_assignment[word] = upos_assignment[word] + " , " + upos
        else:
            upos_assignment[word] = upos

    return upos_assignment


def assign_upos(lexeme, upos_assignment):
    '''Finds lexeme in UDer and its POS'''
    try:
        return upos_assignment[lexeme]
    except KeyError:
        pos_issues.warning("Lexeme %s not in UDer, POS not found", lexeme)
        return "UNK"

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

prefixes = {"acons", "anti", "auto", "bi", "de", "dis", "in", "micro", "mini", "ri", "1s", "2s", "co", "neo", "1in", "2in", "a"}
root_types = {"adj_th", "dnt_root", "ltn_pp", "presp", "pst_ptcp", "root", "suppl", "unrec", "vrb_th"}

upos_assignment = initialize_all_upos()

for line in infile:
    entries = [s.lower() for s in line.strip().split(";")]
    entries = list(filter(lambda f: f!="", entries))
    lexeme = entries[1]
    root = entries[2].split(":")
    # if lexeme!="anti-riscaldamento":
    #     continue

    if len(root) < 2:
        gen_issues.warning("Root %s does not have 2 fields", root)
        continue
    if len(entries) <= 2:
        gen_issues.warning("Lexeme %s only has root", lexeme)

    upos = assign_upos(lexeme, upos_assignment)
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
            seg_issues.warning("Empty morph %s of lexeme %s", info_morpheme, lexeme)
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
            seg_issues.warning("Morph %s not found in lexeme %s with entry %s", allomorph, lexeme, line)
            continue
        if morph_start < start:
            if allomorph.startswith(lexeme[morph_start:start]):
                boundary_overlap_issues.warning("Morph %s overlaps with previous morpheme in lexeme %s with entry %s", allomorph, lexeme, line)
            else:
                seg_issues.warning("Morph %s overlaps with previous morpheme in lexeme %s with entry %s", allomorph, lexeme, line)
        if morph_start == morph_end:
            seg_issues.warning("Empty morph %s in lexeme %s with entry %s", allomorph, lexeme, line)
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


outfile = open(sys.argv[3], 'w')
lexicon.save(outfile)
