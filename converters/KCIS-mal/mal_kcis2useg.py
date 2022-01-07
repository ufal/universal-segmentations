#!/usr/bin/env python3

import re
import sys
sys.path.append('../../src/')
from useg import SegLex
from collections import defaultdict
import unicodedata as ucd
import string

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
    sys.stderr.write("Usage:\n  "+__file__+" Malayalam-SSF-file.csv converted-file.useg\n\n")

gen_issues.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

def isascii(str):
    '''Returns True if English'''
    alphabet = list(string.ascii_lowercase)
    for l in alphabet:
        if l in str:
            return True
    return False

def get_char_equivalences():
    '''Equivalence classes for vowels'''
    letter_file = open("mal_characters.txt", "r")
    eq2letter = defaultdict(lambda: [])
    for line in letter_file:
        description, letter = line.split("\t")[1], line.split("\t")[2]
        eq2letter[description.split(" ")[-2]].append(letter)

    # print("FIRST \n", eq2letter, "\n\n\n")
    del eq2letter["MARK"]
    # del eq2letter["VIRAMA"]
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
    viramas = set()


    letter_file = open("mal_characters.txt", "r")
    for line in letter_file:
        description, letter = line.split("\t")[1], line.split("\t")[2]
        translit_letter = description.split(" ")[-2].lower()

        if "BAR VIRAMA" in description:
            viramas.add(letter)
            continue

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

    return short_vowels, long_vowels, dipthongs, viramas


def normalize_chars(str):
    '''Replace character with representative of equivalence set'''
    str_original = str
    for ch, member in eq_sets.items():
        if ch in str:
            str = re.sub(ch, member, str)

    assert len(str)==len(str_original)

    return str

short_vowels, long_vowels, dipthongs, viramas = get_vowel_classes()
def find_allomorphs(morpheme):
    '''Make modifications from most to least conservative'''
    #No modification
    yield morpheme

    #Remove starting vowel
    def remove_start_vowel(morpheme):
        if len(morpheme)<1:
            return ""
        if morpheme[0] in short_vowels.union(long_vowels):
            return morpheme[1:]
        return morpheme

    #Remove viramas
    def remove_viramas(morpheme):
        return "".join([c for c in morpheme if c not in viramas])

    def switch_letters(morpheme, a, b):
    #Interchange a and b
        morpheme_s = morpheme
        for cidx, c in enumerate(morpheme):
            if c == a:
                morpheme_s = morpheme_s[:cidx] + b + morpheme_s[cidx+1:]
                # yield morpheme_t

            if c == b:
                morpheme_s = morpheme_s[:cidx] + a + morpheme_s[cidx+1:]
                # yield morpheme_t
        return morpheme_s


    #Different combinations of above transformations
    m_rsv = remove_start_vowel(morpheme)
    yield m_rsv


    m_rv = remove_viramas(morpheme)
    yield m_rv
    yield remove_start_vowel(m_rv)

    switch_pairs = {("ട", "റ"), ( "ര", "റ"), ("ത", "ട"), ("ര", "റ"), ("ക", "ങ")}
    #(TTA, RRA), (TA, RRA), (TA, TTA), (RA, RRA), (KA, NGA)

    for s_pair in switch_pairs:
        m_s = switch_letters(morpheme, s_pair[0], s_pair[1])
        yield m_s
        yield remove_start_vowel(m_s)
        yield remove_viramas(m_s)

    # m_twr = switch_letters(morpheme, "ട", "റ") #TTA, RRA
    # yield m_twr
    # yield remove_start_vowel(m_twr)
    # yield remove_viramas(m_twr)
    #
    # m_twr = switch_letters(morpheme, "ര", "റ") #TA, RRA
    # yield m_twr
    # yield remove_start_vowel(m_twr)
    # yield remove_viramas(m_twr)
    #
    # m_twt = switch_letters(morpheme, "ത", "ട") #TA, TTA
    # yield m_twt
    # yield remove_start_vowel(m_twt)
    # yield remove_viramas(m_twt)
    #
    # m_rwr = switch_letters(morpheme, "ര", "റ") #RA, RRA
    # yield m_rwr
    # yield remove_start_vowel(m_rwr)
    # yield remove_viramas(m_rwr)
    #
    #
    # m_kwn = switch_letters(morpheme, "ക", "ങ") #KA, NGA
    # yield m_kwn
    # yield remove_start_vowel(m_kwn)
    # yield remove_viramas(m_kwn)



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

# print(find_morph_boundaries("vacacation", "ca", 6))

def choose_allomorph_boundaries(lexeme, morpheme, req_start = -1):
    '''Finds boundaries of allomorph'''

    best_boundary = dict()

    for morph in find_allomorphs(morpheme):

        morph_start, morph_end = find_morph_boundaries(lexeme, morph, req_start)
        if morph_start != -1:
            best_boundary[morph] = (morph_start, morph_end)

    #Choose allomorph with best boundary
    if len(best_boundary) == 0:
        return -1,-1

    if len(best_boundary) == 1:
        for morph in best_boundary:
            return best_boundary[morph]

    allo_lengths = [[morph, best_boundary[morph][1]-best_boundary[morph][0]] for morph in best_boundary.keys()]
    allo_lengths = sorted(allo_lengths, key = lambda x: x[1], reverse=True)

    #Take all allomorphs with max len
    best_allo_lengths = filter(lambda x: x[1]==allo_lengths[0][1], allo_lengths)

    #If not, judge by closeness to req_start
    dist_from_req = [[morph, abs(req_start - best_boundary[morph][0])] for [morph, len] in best_allo_lengths]
    dist_from_req = sorted(dist_from_req, key = lambda x: x[1])

    return best_boundary[dist_from_req[0][0]]



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
        upos = "ADJ"
    if pos.startswith("RB"):
        upos = "ADV"
    if pos.startswith("PR"):
        upos = "ADP"

    if upos=="":
        pos_issues.warning("POS %s not assigned ", pos)

    return upos

def get_lemma(lexeme, pos, fs):
    '''Returns lemma'''
    return "UNK"

def get_lexeme_features(af, pos):
    '''Extracts and translates features from af'''
    features = dict()
    features["root"] = af[0]
    if len(af)!=8:
        return features
    features["lcat"] = af[1]
    features["gender"] = af[2]
    features["number"] = af[3]
    features["person"] = af[4]
    features["case"] = af[5]
    if assign_upos(pos).startswith("N"):
        features["case_marker"] = af[6]
    if assign_upos(pos).startswith("V"):
        features["tam_marker"] = af[6]

    features["AnnCorra_tag"] = pos

    features = {k:v for k,v in features.items() if v!=""}

    return features



annot_name = "kcis"
infile = open(sys.argv[1])

eq_sets = get_char_equivalences()

for line in infile:
    if line == "\n" or line == " ":
        continue
    entries = line.strip().split("\t")
    lexeme = entries[0].strip("'\"").strip()
    pos = entries[1].strip()
    fs = entries[2].strip()

    if re.match("\d",lexeme):
        continue
    if isascii(lexeme):
        continue
    if len(lexeme)==0:
        continue
    if "af" not in fs:
        continue

    af = fs.strip("<>").split(" ")[1].split("=")[1].strip("''").split(",")


    # if "അക്കാരണങ്ങളാല്" not in lexeme:
        # continue

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

    lexeme_eq = normalize_chars(lexeme)
    morpheme_seq_eq = [normalize_chars(suff) for suff in morpheme_seq]
    short_vowels, long_vowels, dipthongs, viramas = get_vowel_classes()

    start = 0
    for midx, morpheme in enumerate(morpheme_seq_eq):

        if morpheme=="":
            continue

        morph_start, morph_end = choose_allomorph_boundaries(lexeme_eq, morpheme, req_start = start)

        # print(lexeme, "\tnormalized: ", lexeme_eq, "\tmorpheme: ", morpheme,"\tmorph_start, end: ", morph_start, morph_end, "\t", af)
        # print(lexeme_eq[morph_start:morph_end], "\t",len(morpheme), len(lexeme_eq))
        # print(morpheme_seq_eq,"\t", midx)
        # # print(start_of_next_morpheme, end_of_next_morpheme)
        #
        # for i, c in enumerate(lexeme_eq):
        #     print(c, ucd.name(c, "unknown"), i)
        # print("\n")
        # for c in morpheme:
        #     print(c, ucd.name(c, "unknown"))
        # print("\n")
        #
        # print("\n\n\n")

        if morph_start != -1 and morph_end != -1:

            # if morph_start > start:
            #     lexicon.add_contiguous_morpheme(lex_id, annot_name, start, morph_start, features={"type":"interfix"})
            #     seg_issues.warning("Interfix added at position %s, %s, of wordform %s, af: %s", start, morph_start, lexeme, af)
            if midx == 0 and morph_start != 0:
                lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, morph_start, {"type":"prefix"})

            features = dict()
            features["type"] = "root" if midx == 0 else "suffix"
            features["morpheme"] = morpheme_seq[midx]

            lexicon.add_contiguous_morpheme(lex_id, annot_name, morph_start, morph_end, features)
        else:
            if start == 0:
                seg_issues.warning("Root %s not at position %s, of wordform %s, normalized %s", morpheme, start, lexeme, lexeme_eq)
            else:
                if len(morpheme)>1:
                    seg_issues.warning("Morpheme %s not at position %s, of wordform %s, normalized %s", morpheme, start, lexeme, lexeme_eq)
            continue

        if morph_end != -1:
            start = morph_end


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
