#!/usr/bin/env python3

import re
import string
import sys
sys.path.append('../../src/')
from useg import SegLex
import unicodedata as ucd
from collections import defaultdict

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

def get_char_equivalences():
    '''Equivalence classes for vowels'''
    letter_file = open("ben_characters.txt", "r")
    eq2letter = defaultdict(lambda: [])
    for line in letter_file:
        description, letter = line.split("\t")[1], line.split("\t")[2]
        eq2letter[description.split(" ")[-2]].append(letter)

    # print("FIRST \n", eq2letter, "\n\n\n")
    del eq2letter["MARK"]
    # del eq2letter["CANDRABINDU"]
    eq2letter = {v[0]:v for k,v in eq2letter.items() if len(v)>1}
    # print("ONLY DOUBLES \n", eq2letter, "\n\n\n")
    letter2eq = {eq_char:k for k,v in eq2letter.items() for eq_char in v}
    # print("letter2eq\n", letter2eq, "\n\n\n")

    return letter2eq


def get_vowel_classes():
    '''Return set of long and short vowels'''

    vowels = "aeiou"
    short_vowels = set()
    long_vowels = set()
    dipthongs = set()

    letter_file = open("ben_characters.txt", "r")
    for line in letter_file:
        description, letter = line.split("\t")[1], line.split("\t")[2]
        translit_letter = description.split(" ")[-2].lower()

        translit_letter_vow = [c for c in translit_letter if c in vowels]
        if len(translit_letter_vow) < len(translit_letter):
            continue

        if len(translit_letter)==1:
            short_vowels.add(letter)
        elif len(translit_letter)==2 and translit_letter[0]==translit_letter[1]:
            long_vowels.add(letter)
        else:
            dipthongs.add(letter)

    # print("SHORT: ", short_vowels)
    # print("LONG: ", long_vowels)
    # print("DIPTHONGS: ", dipthongs)

    return short_vowels, long_vowels, dipthongs


def normalize_chars(str):
    '''Replace character with representative of equivalence set'''
    str_original = str
    for ch, member in eq_sets.items():
        if ch in str:
            str = re.sub(ch, member, str)

    assert len(str)==len(str_original)

    return str

short_vowels, long_vowels, dipthongs = get_vowel_classes()
eq_sets = get_char_equivalences()
# print(eq_sets)

def find_morph_boundaries(lexeme, morph, req_start = -1):
    '''Finds morph boundaries'''

    # if req_start==0:
    #     return 0, longest_common_prefix(lexeme, morph)

    for i in range(len(morph)):
        # print(i)
        # print(morph[:len(morph)-i])
        # morph_start = lexeme.find(morph[:len(morph)-i])
        shortened_morph = morph[:len(morph)-i]
        # shortened_morph = morph[i:]

        best_start, best_end = -1, -1

        for match in re.finditer(shortened_morph, lexeme):
            current_start, current_end = -1, -1
            morph_start, morph_end = match.start(), match.end()

            allowed_interfix_len = len(lexeme)
            if morph_start <= req_start + allowed_interfix_len:
                current_start, current_end = morph_start, morph_end
                #If more than 1 matches for same length, choose the one closest to req_start
                if best_start == -1:
                    best_start, best_end = current_start, current_end

                if current_start != -1 and abs(current_start - req_start) < abs(best_start - req_start):
                    best_start, best_end = current_start, current_end

        if best_start != -1 and best_start != best_end:
            return best_start, best_end

    return -1,-1




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
    return "UNK"

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
allomorph_set = defaultdict(lambda: set())
allomorphs = {"মএ":{"এ"},
"এর":{"ইর"}}
allomorph_set.update(allomorphs)


for line in infile:

    entries = line.strip().split("\t")
    lexeme = entries[0].strip("'\"").strip()
    pos = entries[1].strip()
    fs = entries[2].strip()

    if re.match("\d",lexeme):
        continue
    if isascii(lexeme):
        continue
    if len(lexeme)<2:
        continue
    if "af" not in fs:
        continue

    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")
    print(lexeme)
    upos = assign_upos(pos)
    lemma = get_lemma(lexeme, pos, fs)
    features = get_lexeme_features(af, pos)


    # if lexeme != "উড়এ":
        # continue
    lex_id = lexicon.add_lexeme(lexeme, lemma, upos, features=features)

    if len(af)!=8:
        gen_issues.warning("Lexeme %s has af: %s without enough fields", lexeme, af)
        continue


    if af[7] not in ["", "0"]:

        suffix = af[7]
        root = af[0]

        lexeme = normalize_chars(lexeme)
        suffix = normalize_chars(suffix)

        # s_len = longest_common_prefix(lexeme[::-1], suffix[::-1])
        #
        # if s_len != 0:
        #     start = len(lexeme) - s_len
        #     assert lexeme[-s_len:] == suffix[-s_len:]
        #     features = {"type":"suffix"}
        #     lexicon.add_contiguous_morpheme(lex_id, annot_name, start, len(lexeme), features)
        #
        #     features = {"type":"root"}
        #     lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, start, features)
        # else:
        #     seg_issues.warning("Suffix %s not at end of wordform %s, af: %s", suffix, lexeme, af)
        morph_start, morph_end = find_morph_boundaries(lexeme, suffix, req_start = len(lexeme))
        if morph_start == -1:
            for allomorph in allomorph_set[suffix]:
                morph_start, morph_end = find_morph_boundaries(lexeme, normalize_chars(allomorph), req_start = len(lexeme))
                if morph_start != -1:
                    break

        if morph_start != -1 and morph_end == len(lexeme):
            # start = len(lexeme) - s_len
            # assert lexeme[-s_len:] == suffix[-s_len:]
            features = {"type":"suffix"}
            lexicon.add_contiguous_morpheme(lex_id, annot_name, morph_start, morph_end, features)

            features = {"type":"root"}
            lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, morph_start, features)
        else:
            seg_issues.warning("Suffix %s not at end of wordform %s, af: %s", suffix, lexeme, af)

        # if morph_start == -1:
        #     issues+=1
        #     print(lexeme, suffix)
        #     print(lexeme, suffix)
        #     for i, c in enumerate(lexeme):
        #         print(c, ucd.name(c, "unknown"), i)
        #     print("\n")
        #     for c in suffix:
        #         print(c, ucd.name(c, "unknown"))
        #     print("\n")
        #
        #     print(morph_start, morph_end)


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
