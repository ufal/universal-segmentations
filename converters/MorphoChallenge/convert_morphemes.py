#!/usr/bin/env python3
#Proof of concept.

import sys
sys.path.append('../../src/')
from useg import SegLex
import difftypes

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
data_new=load_f10(sys.argv[2])

from collections import defaultdict,Counter
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

def starts_with(txt, substr):
    lent=len(txt)
    lens=len(substr)
    if(lens==0):
        return 0
    elif(lent<lens):
        return None
    elif(txt[:lens]==substr):
        return lens
    else:
        return None

# If we want to segment a word to morphs but only know morphemes, 
# then we may collect all the possible morph realizations of each morpheme
# and then try to find out if there is a combination of the morphs that produces the word.
# this method is the bruteforce part of this approach
#
# this methods gets a word and a list of candidate morphs and returns the decomposition or None.
#
# Example:
# find_combination(subword="arrived", candidates=[["arrive"], ["ed", "d"]])
# output: ["arrive", "d"]
def find_combination(subword, candidates):
    if(len(candidates)==0):
        if(len(subword)==0):
            return []
        else:
            return None
    elif(len(subword)!=0 and subword[0]=="-" and "-" not in candidates):
        guess=find_combination(subword[1:],candidates)
        if(guess is not None):
            if(guess==[]):
                return ["-"]
            else:
                return ["-"]+guess
    for candidate in candidates[0]:
        idx=starts_with(subword, candidate)
        if(idx!=None):
            guess=find_combination(subword[idx:],candidates[1:])
            if(guess is not None):
                if(guess==[]):
                    return [candidate]
                else:
                    return [candidate]+guess
    return None

def generate_candidates(word, morphemes, morpheme2morph={},virtual_morpheme2morph={}):
    candidates=[]
    for x in morphemes:
        candidates.append([])
        candidates[-1].append((x,1))
        if(len(x)!=0):
            candidates[-1].append((x+x[-1], 3)) #doubling of letters
            if(x[-1]=="y"):
                candidates[-1].append((x[:-1]+"i", 3)) #change of y to i

        for i in range(0,len(x)): #shortening of subword
            if(len(x)<=3):
                level=5
            else:
                level=4
            candidates[-1].append((x[:i], level))
            candidates[-1].append((x[i:], level))
            if(i>=3):
                candidates[-1].append((x[:i]+x[i-1], 6)) #doubling the last letter
                candidates[-1].append((x[:i-1]+x[i-2]+x[i-1], 7)) #doubling the second but last letter
                #undoubling last letter is already done :)
                if(x[i-2]==x[i-3]):#undoubling second-but-last letter is already done :)
                    candidates[-1].append((x[:i-2]+x[i-1],7))

        for c in virtual_morpheme2morph.get(x,[]):
            candidates[-1].append((c, 1)) #+PL => s, es
        for c,cnt in morpheme2morph.get(x,{}).items():
            if(cnt>=2):
                candidates[-1].append((c, 2)) #changes of individual morphemes with at least 2 occurances
            elif(cnt==1):
                candidates[-1].append((c, 4)) #changes of individual morphemes with 1 occurance
    return candidates

def get_filtered_candidates(candidates, uncertainty_level):
    candidates2=[]
    for grp in candidates:
        grp2=[]
        for candidate, uncertainty in grp:
            if(uncertainty<=uncertainty_level):
                grp2.append(candidate)
        candidates2.append(grp2)
    return candidates2

for word,morphemes in data_old:
        concat="".join(morphemes)
        #if(word==concat):
        #    solved_words.append([word,morphemes,morphemes,0])
        #else:
        candidates=generate_candidates(word, morphemes, morpheme2morph, virtual_morpheme2morph)

        morphs=None
        for uncertainty_level in range(1,7+1):
            candidates2=get_filtered_candidates(candidates, uncertainty_level)
            morphs=find_combination(word, candidates2)
            if(morphs is not None):
                break
        if(morphs is not None):
             #sometimes, "-" morph is not in the list of morphemes, so we need to add it.
            if(len(morphs)!=len(morphemes)):
                #print(word,morphs,morphemes)
                idx1=0
                idx2=0
                morphemes2=[]
                while idx1<len(morphs):
                    if(morphs[idx1]=="-"):
                        morphemes2.append("-")
                    else:
                        morphemes2.append(morphemes[idx2])
                        idx2+=1
                    idx1+=1
                morphemes=morphemes2
             
            solved_words.append([word,morphs,morphemes, uncertainty_level])
            #if(uncertainty_level>=4):
            #    print([word,morphs,morphemes, uncertainty_level])
        else:
            unsolved_words.append([word,morphemes])
            diffs.update([difftypes.difftype3(word,concat)])

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