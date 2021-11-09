#does the string start with the given substring?
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

# this generates morph candidates for the approach described above, except for the fact
# that the candidate list contains uncertainty levels
# [[(morph1, uncertainty), (morph2, uncertainty),..],..]
# uncertainty is basically the level of aggressiveness of the approach. the higher the number, 
# the higher chance of match, but the higher the chance of making a mistake
# the candidates need to be filtered first with get_filtered_candidates before calling the find_combination()
# word is word. morphemes is a list of morpheme strings. the other two are candidate mappings between morphemes and morphs with occurance numbers. 
# (it only matters if it was seen ones or more times. All the candidates are used but have different priorities)
# virtual morphemes should start with + and will not be subject to shortening, etc.
def generate_candidates(word, morphemes, morpheme2morph={},virtual_morpheme2morph={}):
    candidates=[]
    for x in morphemes:
        candidates.append([])
        candidates[-1].append((x,1))
        for c in virtual_morpheme2morph.get(x,[]):
            candidates[-1].append((c, 1)) #+PL => s, es
        for c,cnt in morpheme2morph.get(x,{}).items():
            if(cnt>=2):
                candidates[-1].append((c, 2)) #changes of individual morphemes with at least 2 occurances
            elif(cnt==1):
                candidates[-1].append((c, 3)) #changes of individual morphemes with 1 occurance

        if(len(x)!=0 and x[0]=="+"): #virtual morpheme
            continue

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

    return candidates

#generate guessing candidates of certain uncertainty_level and lower (level 3 collects uncertainty 1,2,3).
#uncertainty level is in range {1,2...,7}. candidates is the output of generate_candidates
def get_filtered_candidates(candidates, uncertainty_level):
    candidates2=[]
    for grp in candidates:
        grp2=[]
        for candidate, uncertainty in grp:
            if(uncertainty<=uncertainty_level):
                grp2.append(candidate)
        candidates2.append(grp2)
    return candidates2



#guesses the morphs when we have a morpheme segmentation of word.
#example:
#   guess_morphs("slowed", ["slow", "+PAST"], {"s":{"es":12} }, {"+PAST":{"d":124, "ed":14}, "+PL":{"s":13},...}}
#output: ["slowed", ["slow","ed"], ["slow", "+PAST"], 1]
#        ie [word, morphs, morphemes, uncertainty level - the higher the worse]
#please note that morphemes may differ from the input ones. e.g. in case that there is "-" in the input 
#word and there was no morpheme representing it.
#
#the dictionaries are {morpheme:Counter({morph1:num_occurances,morph2:num2...  }), morpheme2:  }
#the difference between these dictionaries is that virtual_morpheme2morph is used sooner.
#the occurance number currently only means that candidates with only 1 occurance are tried later.
#
#also: morphemes may be normal or virtual (start with +). We will not try to e.g. shorten the virtual morphemes.
def guess_morphs(word, morphemes, morpheme2morph={}, virtual_morpheme2morph={}):
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
    return word, morphs,morphemes, uncertainty_level




def create_morpheme2morph_mapping(data_new,data_old):
  morpheme2morph=defaultdict(Counter)
  virtual_morpheme2morph=defaultdict(Counter)

  for word, morphemes in data_new:
    for morph, morpheme in morphemes:
        morpheme=morpheme.replace("~","")
        if(len(morpheme)!=0 and morpheme[0]=="+"):
            virtual_morpheme2morph[morpheme].update([morph])
        elif(morph!=morpheme):
            morpheme2morph[morpheme].update([morph])


  virtual_morpheme2morph["+PAST"].update(["t","et"])

  for word,morphemes in data_old:
    morphemes2=[]
    for m in morphemes:
        if(len(m)>1 and m[0]=="+"):
            morphemes2.append(m.upper()) #todo: causes trouble with turkish where punctuation is represented by upper/lower-case
        else:
            morphemes2.append(m.lower())
    if("@@" in word or "##" in word or "+" in word):
        continue
    diff=difftypes.difftype3(word,"".join(map(lambda x: x.replace("+","@@").replace("-","##"),morphemes2)))
    if(len(diff)>=3): #e.g.: _-en+@@INF
        if(diff[:2]=="_-" and "_" not in diff[2:] and "-" not in diff[2:]):
            diff=diff[2:]
            if("+" in diff):
                diff=diff.split("+")
                if(len(diff)==2):
                    from_, to_ =diff
                    to_=to_.replace("@@","+").replace("##","-")
                    for i,x in enumerate(morphemes2):
                        if(x==to_):
                            to_=morphemes[i] #unuppercase
                    tmp=to_.split("+")
                    if(len(tmp)==2 and tmp[0]==""):
                        if(len(to_)>=1 and to_[0]=="+"):
                            virtual_morpheme2morph[to_].update([from_])
                        else:
                            morpheme2morph[to_].update([from_])
  return morpheme2morph,virtual_morpheme2morph