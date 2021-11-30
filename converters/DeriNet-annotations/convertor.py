import sys
sys.path.append('../../src/')
from useg import SegLex

if(len(sys.argv)!=4 or sys.argv[1] not in ["lemmas1","lemmas2","forms1"]):
    print("Usage:")
    print("python convertor.py IN_FORMAT[lemmas1|lemmas2|forms1] IN_FILE OUT_FILE")
    exit(-1)

format=sys.argv[1]
fname_in=sys.argv[2]
fname_out=sys.argv[3]

data=[]
fin=open(fname_in, "r", encoding="utf-8")
for line in fin:
  try:
    line=line.strip()
    if(line==""):
        continue
    line=line.split("\t")
    if(format=="lemmas1"):
        word=line[0]
        batch=line[1]
        try:
          pos=line[2]
        except:
          print(line)
          raise
        segmentations=line[3].split()
        if(pos==""):
            pos="none"
        data.append([word, word, segmentations, pos])
    elif(format=="lemmas2"):
        word=line[0]
        segmentations=line[1].split()
        pos="none"
        data.append([word, word, segmentations, pos])
    elif(format=="forms1"):
        form=line[0]
        lemma=line[2]
        form_segmentation=line[1].split()
        lemma_segmentation=line[3].split()
        pos="none"
        data.append([form, lemma, form_segmentation, pos])
        data.append([lemma, lemma, lemma_segmentation, pos])
  except:
    print(line)
    raise

fin.close()


lexicon = SegLex()
for word,lemma, morphs,pos in data:
    lexeme=lexicon.add_lexeme(form=word, lemma=lemma, pos=pos)
    idx=0
    for i,morph in enumerate(morphs):
        if(len(morph)!=0 and morph[0]=="+"):
            morph_class="INTERFIX"
            morph=morph[1:]
        elif(len(morph)!=0 and morph[0]=="-"):
            morph_class="ENDING"
            if(morph=="-0"):
                morph=""
            else:
                morph=morph[1:]
        else:
            morph_class="UNKNOWN"
        len_=len(morph)
        lexicon.add_contiguous_morpheme(
            lex_id=lexeme,
            annot_name="Derinet-ManualAnnotations",
            start=idx,
            end=idx+len_,
            features={"morph": morph, "morpheme":morph, "type":morph_class},
        )
        idx+=len_
fout=open(fname_out, "w", encoding='utf-8')
lexicon.save(fout)
fout.close()