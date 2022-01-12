#!/usr/bin/env python3

import logging
import sys
import string
import re

sys.path.append('../../src/')
from useg import SegLex

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
        upos = "ADJ"
    if pos.startswith("RB"):
        upos = "ADV"
    if pos.startswith("Q"):
        upos = "NUM"
    if pos.startswith("CC"):
        upos = "SCONJ|CCONJ"
    if pos.startswith("INTF"):
        upos = "ADV"

    if upos == "":
        pos_issues.warning("POS %s not assigned ", pos)

    return upos


def get_lemma(wordform, pos, fs):
    '''Returns lemma'''
    return ""


def get_lexeme_features(af, pos):
    '''Extracts and translates features from af'''
    features = dict()
    features["root"] = af[0]

    if isascii(af[0]):
        del features["root"]

    if len(af) != 8:
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

    features = {k: v for k, v in features.items() if v != ""}

    return features


annot_name = "kcis"
infile = open(sys.argv[1])


allomorph_eq_sets = [{"चा", "ची", "चे", "चं", "च", "च्या"},
                     {"ला", "ली", "ले", "लं", "ल", "ल्या"},
                     {"ता", "तो", "ती", "ते", "तं", "त्या", "तात"}]

allomorph_sets = {morph: morph_set for morph_set in allomorph_eq_sets for morph in morph_set}

for line in infile:
    entries = line.strip().split("\t")
    wordform = entries[0].strip("'\"").strip()
    if re.match("\d", wordform):
        continue
    if isascii(wordform):
        continue
    if len(wordform) == 0:
        continue
    pos = entries[1].strip()
    fs = entries[2].strip()

    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")

    upos = assign_upos(pos)
    lemma = get_lemma(wordform, pos, fs)
    features = get_lexeme_features(af, pos)

    lex_id = lexicon.add_lexeme(wordform, lemma, upos, features=features)

    # if wordform!= "अमेरीकेला":
    #     continue

    if len(af) != 8:
        gen_issues.warning("Wordform %s has af: %s without enough fields", wordform, af)
        continue

    if af[7] == "3":  # Odd annotating anomaly
        continue

    if af[7] != "" and isascii(af[7]) == False:
        suffixes = af[7].split("_")
        suffixes.reverse()
        end = len(wordform)
        # print(line)
        # print(suffixes)

        for suffix in suffixes:
            if suffix in ["", " "]:
                continue

            morph = ""

            if wordform[:end].endswith(suffix):
                morph = suffix
            else:
                if suffix in allomorph_sets:
                    for allomorph in allomorph_sets[suffix]:
                        if wordform[:end].endswith(allomorph):
                            morph = allomorph

            if morph == "":
                for suff in {suffix}.union(allomorph_sets.get(suffix, set())):
                    match = re.search(suff, wordform)
                    if match:
                        start, end = match.start(), match.end()
                        morph = suff
                        break
                if morph == "":
                    seg_issues.warning(
                        "Suffix %s not at end position %s, of wordform %s, af: %s", suffix, end, wordform, af)
                    continue

            start = len(wordform[:end]) - len(morph)

            features = {"type": "suffix"}

            if morph in ["ा", "ां"] and end != len(wordform):
                features["type"] = "interfix"

            lexicon.add_contiguous_morpheme(lex_id, annot_name, start, end, features)

            end = start
            # print(morph, start, end)
            # print("new end, ", end, wordform[:end])

        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, end, features={"type": "root"})


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
