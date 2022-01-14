#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex
from morpheme_classifier import MorphemeClassifier

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

if len(sys.argv) < 3:
    sys.stderr.write("Usage:\n  "+__file__+" Persian-lex-file1.txt [Persian-lex-file2.txt] [Persian-lex-file3.txt] [...] converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1:-1]} to {sys.argv[-1]}")

lexicon = SegLex()

morpheme_cl=MorphemeClassifier()
data=[]
for file_name in sys.argv[1:-1]:
    infile = open(file_name, "r", encoding="utf-8")
    datafile_name=file_name.split("/")[-1].split(".")[0]
    annot_name="PersianLexicon-"+datafile_name
    for line in infile:
        columns = line.rstrip().split(" ")
        wordform = columns[0]
        lemma = columns[1]
        morphemes = columns[4:]
        data.append([wordform, lemma, annot_name, morphemes])
        morpheme_cl.Update(morphemes)
    infile.close()


for j,(wordform, lemma, annot_name, morphemes) in enumerate(data):
    lexeme = lexicon.add_lexeme(wordform, lemma, pos="X")
    morph_classes=morpheme_cl.Guess(morphemes) #workaround because of the right-to-left writing
    start = 0
    for i,morpheme in enumerate(morphemes):
        lexicon.add_contiguous_morpheme(lexeme, annot_name, 0, 0, features={"morpheme": morpheme, "type": morph_classes[i]})

outfile = open(sys.argv[-1], 'w', encoding="utf-8")
lexicon.save(outfile)
outfile.close()