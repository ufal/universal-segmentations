#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" French-demonette-file.csv converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

infile = open(sys.argv[1])

annot_name = "test_1"

def assign_upos(grace_tag):
    '''Finds UPOS tag corresponding to GRACE tag'''
    grace2upos = {"N":"NOUN", "V":"VERB", "A":"ADJ"}
    if grace_tag[:2]=="Np":
        return "PROPN"
    else:
        return grace2upos[grace_tag[0]]

def get_lexeme_features(grace_tag, morph_process):
    '''Builds features JSON for lexeme'''

    gender = {"f":"fem", "m":"masc", "-":"none"}
    number = {"s":"sg", "p":"pl", "-":"none"}

    verb_category = {"m":"main", "a":"aux"}
    mood = {"n":"none"}
    tense = {"-":"non-finite"}
    person = {"-":"none"}

    adj_category = {"f": "qualificative"}
    degree = {"p":"positive", "c":"comparative", "s":"superlative"}

    upos = assign_upos(grace_tag)
    features = {}
    if upos=="NOUN" or upos=="PROPN":
        features["gender"] = gender[grace_tag[2]]
        features["number"] = number[grace_tag[3]]

    if upos=="VERB":
        features["category"] = verb_category[grace_tag[1]]
        features["tense"] = tense[grace_tag[3]]
        if features["tense"] != "non-finite":
            features["mood"] = mood[grace_tag[2]]
            features["person"] = person[grace_tag[4]]
            features["number"] = number[grace_tag[5]]
            features["gender"] = gender[grace_tag[6]]


    if upos=="ADJ":
        features["category"] = adj_category[grace_tag[1]]
        features["degree"] = degree[grace_tag[2]]
        features["gender"] = gender[grace_tag[3]]
        features["number"] = number[grace_tag[4]]

    if morph_process=="conv":
        features["morph_process"] = "conversion"

    return features



def add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root):
    '''Adds lexeme to lexicon object'''
    upos = assign_upos(grace_tag)
    features = get_lexeme_features(grace_tag, morph_process)

    # for prev_lex_id in lexicon.iter_lexemes(form=lexeme, lemma=lexeme, pos=upos):
    #     return
    lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features=features)

    start_of_interfix = 0
    end_of_interfix = len(lexeme)

    if root != "":
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(root), features={"type":"stem"})
        start_of_interfix = len(root)

    if suffix != "":
        stem = lexeme[:-len(suffix)]
        assert len(stem)+len(suffix)==len(lexeme)
        lexicon.add_contiguous_morpheme(lex_id, annot_name, len(stem), len(lexeme), features={"type":"suffix"})
        end_of_interfix = len(stem)

    if start_of_interfix != 0 and end_of_interfix != len(lexeme):
        if start_of_interfix != end_of_interfix:
            lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"interfix"})
    elif end_of_interfix != len(lexeme):
        lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"stem"})

for line in infile:
    if line=="\n" or line==" ":
        continue
    entries = line.split(',')
    lexeme = entries[0].strip('"')
    grace_tag = entries[4].strip('"')
    morph_process = entries[10].strip('"')
    suffix = entries[11].strip('"')
    root = entries[26].strip('"')

    add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root)

    lexeme = entries[2].strip('"')
    grace_tag = entries[6].strip('"')
    morph_process = entries[13].strip('"')
    suffix = entries[14].strip('"')
    root = entries[28].strip('"')

    add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root)

outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
