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
#    print("-- cluster")
    for form in forms:
        if len(longest_common_prefix) > 0:
            suffix = form[len(longest_common_prefix):]

            if pos in unimorphpos2upos:
                pos = unimorphpos2upos[pos]
            
            lexeme = lexicon.add_lexeme(form, lemma, pos  )

#            print(f"lemma={lemma}   form={form}   common={longest_common_prefix}   suffix={suffix}")
            
            lexicon.add_contiguous_morpheme(lexeme,'?TODO', 0, len(longest_common_prefix), features={"type": "root"})
#            print(len(longest_common_prefix), len(form)-1)
            lexicon.add_contiguous_morpheme(lexeme,'?TODO', len(longest_common_prefix), len(form), features={ "type": "suffix"})


lines = sys.stdin.readlines()
lines.sort()  # because e.g. in Spanish accented and non-accented lemmas are interleaved
            
for line in lines:

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
