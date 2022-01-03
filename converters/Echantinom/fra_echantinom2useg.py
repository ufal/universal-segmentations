#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex
from collections import defaultdict

import logging
logging.basicConfig(filename="unsolved.log", filemode = "w", level=logging.WARNING)

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" French-Échantinom-file.csv converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

infile = open(sys.argv[1])

annot_name = "echantinom"

gender_map = {"f":"fem", "m":"masc"}

pos2upos = {"A":"ADJ", "ADV":"ADV",
            "N":"NOUN", "NP":"PROPN", "PRO":"PRON",
            "V":"VERB", "V0":"VERB", "V12":"VERB", "V13":"VERB", "VINF":"VERB",
            "NUM":"NUM"}

allomorphs = defaultdict(lambda: set())
allomorphs_known = {"en":{"em"},
"re": {"r"},
"in": {"im", "il"},
"vice":{"vic"},
"iste":{"yste"},
"erie":{"irie"},
"sous": {"sou"},
"ière":{"ère"},
"entre":{"entr"},
"ette":{"ettes"}
}
allomorphs.update(allomorphs_known)


start_line = True
for line in infile:
    if start_line:
        start_line = False
        continue
    entries = line.split(',')
    lexeme = entries[0]
    gender = entries[1]
    morph_process_broad = entries[6]
    morph_process = entries[7]
    prefix = entries[8]
    compound_type = entries[9]
    conversion_type = entries[10]
    suffix = entries[11]
    suffix_morpheme = entries[12]
    base = entries[13]
    base_pos = entries[14]
    suffix_allomorph = entries[17]


    upos = "NOUN"

    features = {"gender":gender_map[gender], "last_process_broad":morph_process_broad, "last_morph_process":morph_process}

    if compound_type!="0" and "-" not in compound_type:
        features["compound_type"] = compound_type

    if conversion_type!="0":
        features["conversion_from"] = pos2upos[conversion_type]

    if base!="NA":
        features["base"] = base

    if base_pos!="NA":
        features["base_pos"] = pos2upos[base_pos]

    lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features)

    start_of_stem = 0
    end_of_stem = len(lexeme)
    if prefix!="0":

        prefix_set = {prefix}.union(allomorphs[prefix])

        for pref in prefix_set:
            if lexeme.startswith(pref):
                lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(pref), features={"type":"prefix", "morpheme":prefix})
                start_of_stem = len(pref)

        if start_of_stem == 0:
            logging.warning("Prefix %s not contained at the beginning of wordform %s", prefix, lexeme)
            # lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_stem, end_of_stem, features={"type":"stem"})
            # continue


    if suffix!="0":
        # print(lexeme)
        suff_features={"type":"suffix", "morpheme":suffix_morpheme}
        if suffix[-1]=="M" or suffix[-1]=="F":
            # print(suffix)
            suff_features["morpheme_gender"] = suffix[-1]
            suffix = suffix[:-1]
            # print(suffix)
        if suffix[-1]=="2":
            suffix = suffix[:-1]

        if suffix_allomorph!="NA":
            suff_features["allomorph"] = suffix_allomorph


        suffix_set = {suffix}.union(allomorphs[suffix])

        for suff in suffix_set:
            if lexeme.endswith(suff):
                lexicon.add_contiguous_morpheme(lex_id, annot_name, len(lexeme)-len(suff), len(lexeme), features=suff_features)
                end_of_stem = len(lexeme)-len(suff)


        if end_of_stem == len(lexeme):
            logging.warning("Suffix %s not contained at the end of wordform %s", suffix, lexeme)


    #Add processes for compounds
    if morph_process=="native_compound":
        if "-" in lexeme:
            features1 = {"type":"root1"}
            features2 = {"type":"root2"}
            if "-" in compound_type:
                stems_tags = compound_type.split("-")
                features1["upos"] = stems_tags[0]
                features2["upos"] = stems_tags[1]
            lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_stem, lexeme.index("-"), features=features1)
            lexicon.add_contiguous_morpheme(lex_id, annot_name, lexeme.index("-"), lexeme.index("-")+1, features={"type":"hyphen"} )
            lexicon.add_contiguous_morpheme(lex_id, annot_name, lexeme.index("-")+1, end_of_stem, features=features2)
    else:
        lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_stem, end_of_stem, features={"type":"root", "morpheme":base})

outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
