#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex

import os

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


morphynetpos2upos = {'N':'NOUN',
                     'V':'VERB',
                     'J':'ADJ',
                     'R':'ADV',
                     'U':'X'}


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" mophynet-dir output-dir\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")

indir = sys.argv[1]
outdir_common = sys.argv[2]


lexicon = SegLex()

for language_code in [dirname for dirname in os.listdir(indir) if len(dirname)==3]:

    infile_name = indir+language_code+"/"+language_code + ".derivational.v1.tsv"
    
    logging.info(f"Loading {infile_name}")
    
    infile = open(infile_name)

    outdir = outdir_common + "/" + language_code+"-MorphyNet"
    try:
        os.mkdir(outdir)
    except:
        pass
    

    for line in infile:
        columns = line.rstrip().split("\t")

        [parentlemma, lemma, parentpos, pos, affix, affixtype] = columns

        lexeme = lexicon.add_lexeme(lemma, lemma, morphynetpos2upos[pos] )
        
        if affixtype == "prefix":

            if affix.lower() == lemma[:len(affix)].lower():
                lexicon.add_contiguous_morpheme(lexeme,'?TODO', 0, len(affix)-1, features={ "type": "prefix"})
                lexicon.add_contiguous_morpheme(lexeme,'?TODO', len(affix), len(lemma), features={"type": "root"})
            else:
                logging.warning(f"Prefix does not match lemma:  '{affix.lower()}' not equal to '{lemma[:len(affix)].lower()}' in '{lemma}'")

        elif affixtype == "suffix":
            if affix.lower() == lemma[len(lemma)-len(affix):].lower():
                lexicon.add_contiguous_morpheme(lexeme,'?TODO', 0, len(lemma)-len(affix), features={"type": "root"})
                lexicon.add_contiguous_morpheme(lexeme,'?TODO', len(lemma)-len(affix), len(lemma), features={ "type": "suffix"})
            else:
                logging.warning(f"Suffix does not match lemma:  '{affix.lower()}' not equal to '{lemma[len(lemma)-len(affix):].lower()}' in '{lemma}'")                

        else:
            logging.warning(f"Unrecognized affix type:  {affixtype}")

    outfile_name = outdir+"/derivational.useg"    
    outfile = open(outfile_name, 'w')
    logging.info(f"Storing {outfile_name}")    
    lexicon.save(outfile)


            
#for line in infile:
#    columns = line.rstrip().split(" ")
#    wordform = columns[0]
#    lemma = columns[1]
#    morphemes = columns[4:]

#    lexeme = lexicon.add_lexeme(wordform, lemma, '?TODO')

#    start = 0
#    for morpheme in morphemes:
#        lexicon.add_contiguous_morpheme(lexeme,'?TODO', start, start+len(morpheme)-1, features={"morpheme": morpheme, "type": "?TODO"})
#        start = start+len(morpheme)
    

