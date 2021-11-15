#!/usr/bin/env python3
#todo: fill in the report

from collections import defaultdict,Counter
import sys
sys.path.append('../../src/')
from useg import SegLex
import difftypes
import morpheme_guesser
import morpheme_classifier
indir="../../data/original/MorphoChallenge"
outdir="../../data/converted/MorphoChallenge"
if(len(sys.argv)!=4):
    print("Usage:")
    print("./convert_morphemes.py file_with_morphs_only file_with_both_morphs_and_morphemes output_file")
    exit(-1)

#todo: we removed hyy:n	hyy\::hyy n:+GEN, mtk:hon	mtk\::mtk hon:+ILL from finish dataset. ::.......
#todo: root changes
#todo: 52 word in turkish only match with lowercase!!!



def load_f07(fname):
    f=open(fname,"r",1024**2, encoding="latin1")
    data=[]
    for line in f:
        line=line.strip().replace("~","") #.lower()
        if(line==""):
            continue

        label,segs=line.split("\t")
        segs=segs.split(", ")
        segs2=[]
        for seg in segs:
            out=list(map(lambda x: x.split("_")[0], seg.split(" "))) #TODO: fix this!!!
            segs2.append(out)
        for seg in segs2:
            data.append([label,seg])
    f.close()
    return data

def load_f10(fname):
    f=open(fname,"r",1024**2, encoding="latin1")
    data=[]
    for line in f:
        line=line.strip().replace("~","") #.lower()
        if("::" in line):
            print("skipping because of '::':", line)
            continue
        if(line==""):
            continue
        label,segs=line.split("\t")
        segs=segs.split(", ")
        segs2=[]
        for seg in segs:
            tmp=[]
            for m in seg.split(" "):
                morph, morpheme=m.split(":")
                tmp.append([morph,morpheme.split("_")[0]])
            segs2.append(tmp)
        for seg in segs2:
            data.append([label,seg])
    f.close()
    return data

data_old=load_f07(sys.argv[1])
if(sys.argv[2]!=""):
    data_new=load_f10(sys.argv[2])
else:
    data_new=[] #this happens in case of german.
    print("Warning!!! We do not have data for unsupervised morpheme2morph mapping which creates problems in case of virtual morphemes.")

morpheme2morph,virtual_morpheme2morph=morpheme_guesser.create_morpheme2morph_mapping(data_new,data_old)

solved_words=[]
unsolved_words=[]
for word,morphemes in data_old:
        word, morphs,morphemes,uncertainty_level=morpheme_guesser.guess_morphs(word, morphemes, morpheme2morph, virtual_morpheme2morph)
        if(morphs is not None):
            solved_words.append([word,morphs, morphemes, uncertainty_level])
        else:
            unsolved_words.append([word,morphemes])




print("solved:",len(solved_words),"unsolved:",len(unsolved_words))
print("segmented to morphs by authors:",len(data_new), "(does not include the '05 morph-only data)")
#print(len(not_equal),"out of", len(data_old), "words do not equal")

print("unsolved words:")
for word,morphemes in unsolved_words:
    print(word,morphemes)

solved_in_2010=[]
for word, morphemes in data_new:
    out_morphs=[]
    out_morphemes=[]
    for morph, morpheme in morphemes:
        out_morphs.append(morph)
        out_morphemes.append(morpheme)
    solved_in_2010.append([word, out_morphs, out_morphemes, 0])



morpheme_cl=morpheme_classifier.MorphemeClassifier()
for word, morphs, morphemes, uncertainty_level in solved_words+solved_in_2010:
    morpheme_cl.Update(morphs)

lexicon = SegLex()
for word,morphs,morphemes,level in solved_words:
    lexeme=lexicon.add_lexeme(form=word, lemma=word, pos="none")
    morph_classes=morpheme_cl.Guess(morphs)
    idx=0
    for i in range(len(morphs)):
        morph=morphs[i]
        morpheme=morphemes[i]
        len_=len(morph)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme,
            annot_name="MorphoChallenge",
            start=idx,
            end=idx+len_,
            features={"morph": morph, "morpheme":morpheme, "type":morph_classes[i]},
        )
        idx+=len_

for word,morphs,morphemes,level in solved_in_2010:
    lexeme=lexicon.add_lexeme(form=word, lemma=word, pos="none")
    morph_classes=morpheme_cl.Guess(morphs)
    idx=0
    for i in range(len(morphs)):
        morph=morphs[i]
        morpheme=morphemes[i]
        len_=len(morph)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme,
            annot_name="MorphoChallenge2010",
            start=idx,
            end=idx+len_,
            features={"morph": morph, "morpheme":morpheme, "type":morph_classes[i]},
        )
        idx+=len_



fout=open(sys.argv[3], "w", encoding='utf-8')
lexicon.save(fout)
fout.close()