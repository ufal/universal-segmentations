#!/usr/bin/env python3

import csv

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" MorphoDictKE-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")


lexicon = SegLex()


parse_pos = {
    'A': 'ADJ', 'S': 'NOUN', 'V': 'VERB', 'ADV': 'ADV', 'PR': 'ADP', 'APRO': 'PRON', 'SPRO': 'PRON',
    'ANUM': 'NUM', 'NUM': 'NUM', 'ADVPRO': 'ADV', 'CONJ': 'CONJ', 'PART': 'PART', 'PARENTH': 'X',
    'INTJ': 'INTJ', 'PRAEDIC': 'X', 'NONLEX': 'X', 'COM': 'NOUN'
}

with open(sys.argv[1], mode='r', encoding='U8') as infile:
    for lemma, morphs, roots, pos, morphs_init, _ in csv.reader(infile):
        morphs = morphs if type(morphs) is list else eval(morphs)
        roots = roots if type(roots) is list else eval(roots)
        morphs_init = morphs_init if type(morphs_init) is list else eval(morphs_init)

        lexeme = lexicon.add_lexeme(form=lemma, lemma=lemma, pos=parse_pos.get(pos, '?TODO?'))

        for morph, init_index in zip(morphs, morphs_init):
            if morph in roots:
                lexicon.add_contiguous_morpheme(
                    lex_id=lexeme,
                    annot_name='?TODO?',
                    start=init_index,
                    end=init_index + len(morph),
                    features={'morph': morph, 'morpheme': '?TODO?', 'type': 'root'}
                )
            else:
                lexicon.add_contiguous_morpheme(
                    lex_id=lexeme,
                    annot_name='?TODO?',
                    start=init_index,
                    end=init_index + len(morph),
                    features={'morph': morph, 'morpheme': '?TODO?', 'type': '?TODO?'}
                )
    

with open(sys.argv[2], mode='w', encoding='U8') as outfile:
    lexicon.save(outfile)
