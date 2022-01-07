#!/usr/bin/env python3

import regex as re
from collections import defaultdict

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" CroDeriV-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[3]}")


lexicon = SegLex()


with open(sys.argv[1], mode='r', encoding='U8') as infile:
    content = ''.join(infile.readlines())
    content = content.replace('\n', '')
    entries = re.findall(r'\<a href\=\"\/Entry\/Details\/(.*?)(Details)', content)


manual_annotation = defaultdict()
with open(sys.argv[2], mode='r', encoding='U8') as infile:  # manual annotation
    for line in infile:
        lemma, annotation = line.strip().split('\t')
        manual_annotation[lemma.strip()] = eval(annotation)


for item, _ in entries:
    lemma = re.search(r'[0-9]\"\>(.*?)\<', item).group(1).strip()
    morphs = re.findall(r'<a*s*p*a*n* class=\"(.*?)\".*?>&nbsp;(.*?)&nbsp;</a*s*p*a*n*>', item)

    if lemma.endswith('ti') or lemma.endswith('ći') or lemma.endswith(' se'):
        pos = 'VERB'
    else:
        pos = 'NOUN'
    
    lexeme = lexicon.add_lexeme(lemma, lemma, pos)
    if manual_annotation.get(lemma, False):
        morphs = manual_annotation[lemma]
        logging.info(f'Lemma "{lemma}" annotated manualy as {morphs} becouse of troubles in the original data')

    start = 0
    for label, morph in morphs:
        morph = re.sub(r'[0-9]', '', morph)

        if morph == '&#;':
            continue

        try:
            lexicon.add_contiguous_morpheme(
                lex_id=lexeme,
                annot_name='CroDeriV-1.0',
                start=start,
                end=start + len(morph),
                features={'type': label.lower()}
            )
            start = start + len(morph)
        except:
            logging.error(f'Troubles with "{morph}" in the segmentation of "{lemma}" which is "{morphs}"')
            break


with open(sys.argv[3], mode='w', encoding='U8') as outfile:
    lexicon.save(outfile)
logging.info(f"Converting completed.")
