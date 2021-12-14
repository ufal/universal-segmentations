#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex
from collections import defaultdict

import logging
logging.basicConfig(filename="unsolved.log", filemode = "w", level=logging.WARNING)

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" French-demonette-file.csv converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

infile = open(sys.argv[1])

def assign_upos(grace_tag):
    '''Finds UPOS tag corresponding to GRACE tag based on first letter'''
    grace2upos = {"N":"NOUN", "V":"VERB", "A":"ADJ"}
    if grace_tag[:2]=="Np":
        return "PROPN"
    else:
        return grace2upos[grace_tag[0]]

def get_lexeme_features(root, grace_tag, morph_process, annot_name):
    '''Builds features JSON for lexeme'''
    features = {}
    features["root"] = root

    gender = {"f":"fem", "m":"masc", "-":"none"}
    number = {"s":"sg", "p":"pl", "-":"none"}

    verb_category = {"m":"main", "a":"aux"}
    mood = {"n":"none"}
    tense = {"-":"non-finite"}
    person = {"-":"none"}

    adj_category = {"f": "qualificative"}
    degree = {"p":"positive", "c":"comparative", "s":"superlative"}

    upos = assign_upos(grace_tag)

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

# Building allomorph set based on observation of allomorphy occurence from corpus
allomorph_set = defaultdict(lambda: set())
allomorph_known = {"aille" : {"ailles"},
"ment":{"ments"},
"aison":{"ison"},
"erie":{"irie"},
"if":{"ive"},
"ure":{"ûre"}
}
allomorph_set.update(allomorph_known)

def add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root, annot_name):
    '''Adds lexeme to lexicon object'''

    upos = assign_upos(grace_tag)
    features = get_lexeme_features(root, grace_tag, morph_process, annot_name)

    lex_id = lexicon.add_lexeme(lexeme, lexeme, upos, features=features)

    # ASSUMPTION: There is at most one root and suffix. This is true for the Demonette dataset.
    # In case there is some interfix, we will find its start and end boundary by shifting these two pointers
    # forwards and backwards depending on the found root and suffix.
    # We label anything between the root and suffix as an interfix.
    start_of_interfix = 0
    end_of_interfix = len(lexeme)

    # Handling hyphenated words. There are only 5 such words in Demonette; of the structure <prefix>-<root>...
    # We therefore label the first part as prefix.
    # Hyphens are annotated as hyphen morphs
    if "-" in lexeme:
        prefix = lexeme.split("-")[0]
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(prefix), features={"type":"prefix"})
        lexicon.add_contiguous_morpheme(lex_id, annot_name, len(prefix), len(prefix)+1, features={"type":"hyphen"})


    if root != "" and lexeme.startswith(root):
        assert suffix not in ["0", ""]
        lexicon.add_contiguous_morpheme(lex_id, annot_name, 0, len(root), features={"type":"root"})
        start_of_interfix = len(root)

    if suffix not in ["0", ""]:
        for allomorph in {suffix}.union(allomorph_set[suffix]):
            if lexeme.endswith(allomorph):
                suffix = allomorph
                break
        stem = lexeme[:-len(suffix)]
        if lexeme[-len(suffix):]!=suffix:
            logging.warning("Suffix %s not contained at the end of wordform %s", suffix, lexeme)
            lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"root"})
            return
        # if suffix not in lexeme:
        #     logging.warning("Suffix %s not contained in wordform %s", suffix, lexeme)
        #     lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"root"})
        #     return
        lexicon.add_contiguous_morpheme(lex_id, annot_name, len(stem), len(lexeme), features={"type":"suffix"})
        end_of_interfix = len(stem)

    if start_of_interfix != 0 and end_of_interfix != len(lexeme): #we've found some root and suffix
        if start_of_interfix != end_of_interfix:
            lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"interfix"})

    elif start_of_interfix==0: #elif end_of_interfix != len(lexeme) (if we want to avoid adding whole word as stem)
        assert start_of_interfix != end_of_interfix
        lexicon.add_contiguous_morpheme(lex_id, annot_name, start_of_interfix, end_of_interfix, features={"type":"root"})

for line in infile:
    if line=="\n" or line==" ":
        continue
    entries = line.split(',')
    lexeme = entries[0].strip('"')
    grace_tag = entries[4].strip('"')
    morph_process = entries[10].strip('"')
    suffix = entries[11].strip('"')
    root = entries[26].strip('"')
    annot_name = entries[12].strip('"') or entries[27].strip('"')
    if entries[12].strip('"') != "" and entries[27].strip('"') != "":
        assert entries[12].strip('"') == entries[27].strip('"')

    add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root, annot_name)

    lexeme = entries[2].strip('"')
    grace_tag = entries[6].strip('"')
    morph_process = entries[13].strip('"')
    suffix = entries[14].strip('"')
    root = entries[28].strip('"')
    annot_name = entries[15].strip('"') or entries[29].strip('"')
    if entries[15].strip('"') != "" and entries[29].strip('"') != "":
        assert entries[15].strip('"') == entries[29].strip('"')

    add_lexeme(lexicon, lexeme, grace_tag, morph_process, suffix, root, annot_name)

outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
