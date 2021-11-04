#!/usr/bin/env python3

import sys
sys.path.append('../../src/')
from useg import SegLex

import os

import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


unimorphpos2upos = {'N':'NOUN',
                     'V':'VERB',
                     'ADJ':'ADJ',
                     'ADV':'ADV'}

# TODO: there are many other POS values distinguished, see: ../../data/original/UniMorph/???/??? | cut -f3 | cut -f1 -d ';' | cut -f1 -d '.' | Sort
import os.path

#if len(sys.argv) != 2:
#    sys.stderr.write("Usage:\n  "+__file__+" langcode < input-unimorph-file > output-useg-file \n\n")

#logging.info(f"Converting {sys.argv[1]} from STDIN to STDOUT")

#langcode = sys.argv[1]

lexicon = SegLex()

prevlemma = None
prevpos = None
allforms = []

def process_cluster(lemma,pos,forms):
    longest_common_prefix = os.path.commonprefix(forms)
    for form in forms:
        print(f"lemma={lemma} form={form} prefix={longest_common_prefix}")
        if len(longest_common_prefix) > 0:
#            print("X"+str(len(longest_common_prefix)))
            suffix = form[len(longest_common_prefix):]
            
            lexeme = lexicon.add_lexeme(lemma, form, unimorphpos2upos[pos] )

            print(f"lemma={lemma}   form={form}   common={longest_common_prefix}   suffix={suffix}")
            
            lexicon.add_contiguous_morpheme(lexeme,'?TODO', 0, len(longest_common_prefix)-1, features={"type": "root"})
            print(len(longest_common_prefix), len(form)-1)
            lexicon.add_contiguous_morpheme(lexeme,'?TODO', len(longest_common_prefix), len(form)-1, features={ "type": "suffix"})


for line in sys.stdin:

        columns = line.rstrip().split("\t")

        if len(columns) == 3:

            [lemma, wordform, morphofeatures] = columns
            pos = morphofeatures.split(";")[0]

            if prevlemma == None or prevlemma == lemma:
                allforms.append(wordform)

            else:
                process_cluster(prevlemma,prevpos,allforms)
                allforms = [wordform]

            prevlemma = lemma
            prevpos = pos
        
        
process_cluster(prevlemma,prevpos,allforms)

            
#        pos = morphofeatures.split(";")[0]

#        if pos in unimorphpos2upos:
#            pos = unimorphpos2upos[pos]
        
#        lexeme = lexicon.add_lexeme(lemma, lemma, pos )
        


lexicon.save(sys.stdout)
