#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg.seg_lex import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" Persian-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

lexicon = SegLex()

infile = open(sys.argv[1])

for line in infile:
    columns = line.rstrip().split(" ")
    wordform = columns[0]
    lemma = columns[1]
    morphemes = columns[4:]

    lexeme = lexicon.add_lexeme(wordform, lemma, '?TODO')

    start = 0
    for morpheme in morphemes:
        lexicon.add_contiguous_morpheme(lexeme,'?TODO', start, start+len(morpheme)-1, features={"morpheme": morpheme, "type": "?TODO"})
        start = start+len(morpheme)
    

outfile = open(sys.argv[2], 'w')
lexicon.save(outfile)
