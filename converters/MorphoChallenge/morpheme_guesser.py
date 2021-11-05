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




def guess_morphs(word, morphemes, morpheme2morph, virtual_morpheme2morph):
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