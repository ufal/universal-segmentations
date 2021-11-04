"""
Diff types
Difftypes are descriptions of the change from one word to another.

They all stem from the original representation of difference:
    jel   --> dojel     ["+do","_jel"]
    lodka --> lodicka   ["_lod", "+ic", "_ka"]
    vyrazit --> porazit ["-po", "+vy", "razit"]

difftype1:
    jel   --> dojel         +_          //Why?  +do,_jel
    lodka --> lodicka       _+_         //Why?  _lod,+ic,_ka
    vyrazit --> porazit     -+_         //Why?  -po,+vy,_razit

difftype2:
    jel   --> dojel         +2_3       //Why? Two charracters added, and the following 3 remained the same
    lodka --> lodicka       _3+2_2     //Why? The first tree charracters remained the same, then two 2 charracters were added, and the following 2 remained the same.

difftype3:
    jel   --> dojel         +do_       //Why? "do" was added, the rest remained the same
    lodka --> lodicka       _+ic_      //Why?  ic was inserted in the middle of word.

difftype3_with_diacritics
    loďka --> lodička       _-ď+dič_
    vylez --> výlez         _-y+ý_

difftype4:
    jel   --> dojel         +2_
    lodka --> lodicka       _+2_



Usage:
    difftype1("jel","dojel")   --->   +_

use of preprocess("word") is highly recommended, although not necessary (strip(),lower_case(), remove_accents())
    pdifftype1("jel","dojel")   --->   +_

does that for you

"""

#from DerinetTreeBuilder import Node,DerinetTreeBuilder
import difflib


def strip_diacritics(w):
    for x,y in ["áa","ée","ěe","íi","ýy","óo","úu","ůu","čc","ďd","ňn","řr","šs","ťt","žz"]: #hubit->zhouba, sníh->sněžný require a more advanced approach
        w=w.replace(x,y)
    return w

def preprocess(w):
    w=w.lower().strip()
    w=strip_diacritics(w)
    return w

def preprocess2(w):
    w=w.lower().strip()
    return w



def diff(a,b): #"ammianus","ammianův"
    differ=difflib.Differ();
    dif=list(differ.compare(a,b)) #['  a', '  m', '  m', '  i', '  a', '  n', '- u', '- s', '+ ů', '+ v']  #TODO: UNCOMMENT THIS

    #let's clean it up a little.
    dif2=[dif[0]]
    for x in dif[1:]:
        if(x[0]==dif2[-1][0]):
            dif2[-1]+=x[1:]
        else:
            dif2.append(x)
    dif3=[]
    for x in dif2:
        dif3.append(x[0]+x[1:].replace(" ",""))
    i=0
    maxi=len(dif3)-1
    while(i<maxi):
        if(dif3[i][0]=="+" and dif3[i+1][0]=="-"): #swap them
            dif3[i],dif3[i+1]=dif3[i+1],dif3[i]
            i+=1
        i+=1
    return dif3

def diff_showdiac(a,b): #"ammianus","ammianův"
    a=a.strip().lower()
    b=b.strip().lower()
    a_=preprocess(a)
    b_=preprocess(b)
    differ=difflib.Differ();
    dif=list(differ.compare(a_,b_)) #['  a', '  m', '  m', '  i', '  a', '  n', '- u', '- s', '+ ů', '+ v']  #TODO: UNCOMMENT THIS
    a_idx=0
    b_idx=0
    for i in range(len(dif)):
        type_,_, letter=dif[i]
        if(type_==" "):
            a_idx+=1
            b_idx+=1
        elif(type_=="+"):
            dif[i]="+ "+b[b_idx]
            b_idx+=1
        elif(type_=="-"):
            dif[i]="- "+a[a_idx]
            a_idx+=1
    #let's clean it up a little.
    dif2=[dif[0]]
    for x in dif[1:]:
        if(x[0]==dif2[-1][0]):
            dif2[-1]+=x[1:]
        else:
            dif2.append(x)
    dif3=[]
    for x in dif2:
        dif3.append(x[0]+x[1:].replace(" ",""))
    i=0
    maxi=len(dif3)-1
    while(i<maxi):
        if(dif3[i][0]=="+" and dif3[i+1][0]=="-"): #swap them
            dif3[i],dif3[i+1]=dif3[i+1],dif3[i]
            i+=1
        i+=1
    return dif3









"""
difftype1:
    jel   --> dojel         +_          //Why?  +do,_jel
    lodka --> lodicka       _+_         //Why?  _lod,+ic,_ka
    vyrazit --> porazit     -+_         //Why?  -po,+vy,_razit
"""
def difftype1(a,b):
    dif=diff(a,b)
    out=""
    for x in dif:
        out+=x[0]
    out=out.replace(" ","_")
    return out

def pdifftype1(a,b):
    return difftype1(preprocess(a),preprocess(b))

"""
difftype2:
    jel   --> dojel         +2_3       //Why? Two charracters added, and the following 3 remained the same
    lodka --> lodicka       _3+2_2     //Why? The first tree charracters remained the same, then two 2 charracters were added, and the following 2 remained the same.
"""
def difftype2(a,b):
    dif=diff(a,b)
    out=""
    for x in dif:
        out+=x[0]+str(len(x)-1)
    out=out.replace(" ","_")
    return out

def pdifftype2(a,b):
    return difftype2(preprocess(a),preprocess(b))

"""
difftype3:
    jel   --> dojel         +do_       //Why? "do" was added, the rest remained the same
    lodka --> lodicka       _+ic_      //Why?  ic was inserted in the middle of word.
"""
def difftype3(a,b):
    dif=diff(a,b)
    out=""
    for x in dif:
        if(x[0]==" "):
            out+="_"
        else:
            out+=x
    out=out.replace(" ","_")
    return out

difftype3_with_diacritics=difftype3

def pdifftype3(a,b):
    return difftype3(preprocess(a),preprocess(b))

#vylez->výlez = _-y+ý_
def pdifftype3_with_diacritics(a,b):
    return difftype3_with_diacritics(preprocess2(a),preprocess2(b))

def pdifftype3_showdiac(a,b):
    dif=diff_showdiac(a,b)
    out=""
    for x in dif:
        if(x[0]==" "):
            out+="_"
        else:
            out+=x
    out=out.replace(" ","_")
    return out


"""
difftype4:
    jel   --> dojel         +2_
    lodka --> lodicka       _+2_
"""
def difftype4(a,b):
    dif=diff(a,b)
    out=""
    for x in dif:
        if(x[0]!=" "):
            out+=x[0]+str(len(x)-1)
        else:
            out+="_"
    out=out.replace(" ","_")
    return out

def pdifftype4(a,b):
    return difftype4(preprocess(a),preprocess(b))


"""
for (a,b) in [("jel","dojel"),("lodka","lodicka"), ("vyrazit","porazit")]:
    print((a,b))
    for diff_fn in [difftype1,difftype2,difftype3,difftype4]:
        print(diff_fn(a,b))
    print()
"""



def basic_diff(string_a,string_b):
    diff=difflib.SequenceMatcher(None,string_a,string_b).find_longest_match(0,len(string_a),0,len(string_b))
    idx_a=diff.a
    idx_b=diff.b
    size=diff.size
    remove_prefix=""
    if(idx_a!=0):
        remove_prefix="-"+string_a[:idx_a]
    add_prefix=""
    if(idx_b!=0):
        add_prefix="+"+string_b[:idx_b]
    remove_suffix=""
    if(idx_a+size<len(string_a)):
        remove_suffix="-"+string_a[idx_a+size:]
    add_suffix=""
    if(idx_b+size<len(string_b)):
        add_suffix="+"+string_b[idx_b+size:]
    return remove_prefix+add_prefix+"_"+remove_suffix+add_suffix

def order(a,b):
    lena_=len(a)
    lenb_=len(b)
    if(lena_<lenb_):
        return a,b
    elif(lena_==lenb_):
        if(a<=b): #lexicographic ordering
            return a,b
        else:
            return b,a
    else:
        return b,a