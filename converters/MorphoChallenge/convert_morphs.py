#!/usr/bin/env python3
import sys
sys.path.append('../../src/')
from useg import SegLex

if(len(sys.argv)!=3):
    print("Usage:")
    print("./convert_morphs.py INPUT_FILE OUTPUT_FILE")
    exit(-1)

fname_in=sys.argv[1]
fname_out=sys.argv[2]

lexicon = SegLex()
fin=open(fname_in, "r", encoding="utf-8")
id_=0
for line in fin:
    line=line.strip()
    if(line==""):
        continue
    line=line.split("\t")
    word=line[0]
    segmentations=line[1].split(", ")
    for seg in segmentations:
        lexeme=lexicon.add_lexeme(form=word, lemma=word, pos="none")
        morphs=seg.split(" ")
        idx=0
        for morph in morphs:
            len_=len(morph)
            lexicon.add_contiguous_morpheme(
                lex_id=lexeme, 
                annot_name="none",
                start=idx,
                end=idx+len_,
                features={"morph": morph, "morpheme":morph, "type":"none"},
            )
            idx+=len_
fin.close()
fout=open(fname_out, "w", encoding='utf-8')
lexicon.save(fout)
fout.close()