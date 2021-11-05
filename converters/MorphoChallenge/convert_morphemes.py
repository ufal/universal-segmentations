#!/usr/bin/env python3
#Proof of concept.

from collections import defaultdict,Counter
import sys
sys.path.append('../../src/')
from useg import SegLex
import difftypes
import morpheme_guesser

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
        line=line.strip().replace("~","").lower()
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
        line=line.strip().replace("~","").lower()
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


morpheme2morph=defaultdict(Counter)
morpheme2morph_diffs=Counter()
virtual_morpheme2morph=defaultdict(Counter)

for word, morphemes in data_new:
    for morph, morpheme in morphemes:
        morpheme=morpheme.replace("~","")
        if(len(morpheme)!=0 and morpheme[0]=="+"):
            virtual_morpheme2morph[morpheme].update([morph])
        elif(morph!=morpheme):
            morpheme2morph[morpheme].update([morph])
            diff=difftypes.difftype3(morpheme,morph)
            morpheme2morph_diffs.update([diff])


solved_words=[]
unsolved_words=[]
diffs=Counter()


for word,morphemes in data_old:
        word, morphs,morphemes,uncertainty_level=morpheme_guesser.guess_morphs(word, morphemes, morpheme2morph, virtual_morpheme2morph)
        if(morphs is not None):
            solved_words.append([word,morphs, morphemes, uncertainty_level])
            #if(uncertainty_level>=4):
            #    print([word,morphs,morphemes, uncertainty_level])
        else:
            unsolved_words.append([word,morphemes])
            diffs.update([difftypes.difftype3(word,"".join(morphemes))])

print("solved:",len(solved_words),"unsolved:",len(unsolved_words))
print("segmented to morphs by authors:",len(data_new), "(does not include the '05 morph-only data)")
#print(len(not_equal),"out of", len(data_old), "words do not equal")

print("unsolved words:")
for w,m in unsolved_words:
    print(w,m)

solved_in_2010=[]
for word, morphemes in data_new:
    out_morphs=[]
    out_morphemes=[]
    for morph, morpheme in morphemes:
        out_morphs.append(morph)
        out_morphemes.append(morpheme)
    solved_in_2010.append([word, out_morphs, out_morphemes, 0])

lexicon = SegLex()
for word,morphs,morphemes,level in solved_words+solved_in_2010:
    lexeme=lexicon.add_lexeme(form=word, lemma=word, pos="none")
    idx=0
    for i in range(len(morphs)):
        morph=morphs[i]
        morpheme=morphemes[i]
        len_=len(morph)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme, 
            annot_name="none",
            start=idx,
            end=idx+len_,
            features={"morph": morph, "morpheme":morpheme, "type":"none"},
        )
        idx+=len_

fout=open(sys.argv[3], "w", encoding='utf-8')
lexicon.save(fout)
fout.close()


"""
Experiments with unsupervised morpheme handling.
>>> difftypes.difftype3("yllätystappion","|||".join(['yllättää', '+DV-US', 'tappio', '+GEN']))
'_-ys+tää|||+DV-US|||_-n+|||+GEN'

def uppercase(s):
    if(len(s)>0):
        if(s[0]=="+"):
            s=s.upper()
    return s

unsolved_diffs2=Counter()
for word, morphemes in unsolved_words:
    morphemes=list(map(uppercase, morphemes))
    diff=difftypes.difftype3(word,"|||".join([""]+morphemes+[""])).split("_")
    unsolved_diffs2.update(diff)
    print(diff)

"""