#!/usr/bin/env python3

#TODO Add word 2
#TODO Add more features

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

def get_lexeme_features(grace_tag):
    '''Builds features JSON for lexeme'''

    gender = {"f":"fem", "m":"masc", "-":"none"}
    number = {"s":"sg", "p":"pl", "-":"none"}

    mood = {"n":"none"}
    tense = {"-":"non-finite"}
    person = {"-":"none"}

    degree = {"p":"positive", "c":"comparative", "s":"superlative"}

    upos = assign_upos(grace_tag)
    features = {}
    if upos=="NOUN" or upos=="PROPN":
        features["gender"] = gender[grace_tag[2]]
        features["number"] = number[grace_tag[3]]

    if assign_upos(grace_tag)=="VERB":
        features["tense"] = tense[grace_tag[3]]
        if features["tense"] != "non-finite":
            features["mood"] = mood[grace_tag[2]]
            features["person"] = person[grace_tag[4]]
            features["number"] = number[grace_tag[5]]
            features["gender"] = gender[grace_tag[6]]


    if assign_upos(grace_tag)=="ADJ":
        features["degree"] = degree[grace_tag[2]]
        features["gender"] = gender[grace_tag[3]]
        features["number"] = number[grace_tag[4]]

    return features


for line in infile:
    entries = line.split(',')
    lexeme = entries[0].strip('"')
    grace_tag = entries[4].strip('"')
    type = entries[10].strip('"')
    suffix = entries[11].strip('"')

    upos = assign_upos(grace_tag)
    features = get_lexeme_features(grace_tag)
    #radical = entries[26]
    if set(lexicon.iter_lexemes(form=lexeme, lemma=lexeme, pos=upos)):
        continue
    lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features=features)
    if suffix != "":
        stem = lexeme[:-len(suffix)]
        #add_contiguous_morpheme(self, lex_id, annot_name, start, end, features=None):
        assert len(stem)+len(suffix)==len(lexeme)
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(stem), features={"type":"stem"})
        lexicon.add_contiguous_morpheme(lex_id, annot_name, len(stem), len(lexeme), features={"type":"suffix"})
    else:
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(lexeme))


outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
