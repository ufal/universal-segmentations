#!/usr/bin/env python3
import sys
import morpheme_classifier
sys.path.append('../../src/')
from useg import SegLex


if(len(sys.argv)!=3):
    print("Usage:")
    print("./convert_morphs.py INPUT_FILE OUTPUT_FILE")
    exit(-1)

fname_in=sys.argv[1]
fname_out=sys.argv[2]


fin=open(fname_in, "r", encoding="utf-8")
id_=0
data=[]
for line in fin:
    line=line.strip()
    if(line==""):
        continue
    line=line.replace("/","")
    morphs=line.split(" ")
    word="".join(morphs)
    data.append([word,morphs])

fin.close()

morpheme_cl=morpheme_classifier.MorphemeClassifier()
for word,morphs in data:
    morpheme_cl.Update(morphs)


lexicon = SegLex()
for word,morphs in data:
    lexeme=lexicon.add_lexeme(form=word, lemma=word, pos="none")
    morph_classes=morpheme_cl.Guess(morphs)
    idx=0
    for i,morph in enumerate(morphs):
        len_=len(morph)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme,
            annot_name="Tikhonov",
            start=idx,
            end=idx+len_,
            features={"morph": morph, "morpheme":morph, "type":morph_classes[i]},
        )
        idx+=len_
fout=open(fname_out, "w", encoding='utf-8')
lexicon.save(fout)
fout.close()