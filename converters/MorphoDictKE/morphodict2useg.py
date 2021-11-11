#!/usr/bin/env python3

import csv

import sys
sys.path.append('../../src/')
from useg import SegLex


import logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


if len(sys.argv) != 3:
    sys.stderr.write("Usage:\n  "+__file__+" MorphoDictKE-lex-file.txt converted-file.useg\n\n")

logging.info(f"Converting {sys.argv[1]} to {sys.argv[2]}")


lexicon = SegLex()


parse_pos = {
    'A': 'ADJ', 'S': 'NOUN', 'V': 'VERB', 'ADV': 'ADV', 'PR': 'ADP', 'APRO': 'PRON', 'SPRO': 'PRON',
    'ANUM': 'NUM', 'NUM': 'NUM', 'ADVPRO': 'ADV', 'CONJ': 'CONJ', 'PART': 'PART', 'PARENTH': 'X',
    'INTJ': 'INTJ', 'PRAEDIC': 'X', 'NONLEX': 'X', 'COM': 'NOUN'
}

with open(sys.argv[1], mode='r', encoding='U8') as infile:
    for lemma, morphs, roots, pos, morphs_init, _ in csv.reader(infile):
        morphs = morphs if type(morphs) is list else eval(morphs)
        roots = roots if type(roots) is list else eval(roots)
        morphs_init = morphs_init if type(morphs_init) is list else eval(morphs_init)

        lexeme = lexicon.add_lexeme(form=lemma, lemma=lemma, pos=parse_pos.get(pos, pos))

        seen_stem, between_stems = False, False
        for morph, init_index in zip(morphs, morphs_init):
            if len(roots) == 1:
                if morph in roots:
                    seen_stem = True
                    lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph),
                        features={'type': 'root'}
                    )
                elif not seen_stem:
                    lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph),
                        features={'type': 'prefix'}
                    )
                else:
                    if len(lemma) == init_index + len(morph):
                        lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph)
                    )
                    else:
                        lexicon.add_contiguous_morpheme(
                            lex_id=lexeme,
                            annot_name='?TODO?',
                            start=init_index,
                            end=init_index + len(morph),
                            features={'type': 'suffix'}
                        )
            else:
                if morph in roots:
                    if morph == roots[0]:
                        between_stems = True
                    elif morph == roots[-1]:
                        between_stems = False
                    seen_stem = True
                    lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph),
                        features={'type': 'root'}
                    )
                elif not seen_stem and not between_stems:
                    lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph),
                        features={'type': 'prefix'}
                    )
                elif seen_stem and not between_stems:
                    if len(lemma) == init_index + len(morph):
                        lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph)
                    )
                    else:
                        lexicon.add_contiguous_morpheme(
                            lex_id=lexeme,
                            annot_name='?TODO?',
                            start=init_index,
                            end=init_index + len(morph),
                            features={'type': 'suffix'}
                        )
                else:
                    lexicon.add_contiguous_morpheme(
                        lex_id=lexeme,
                        annot_name='?TODO?',
                        start=init_index,
                        end=init_index + len(morph)
                    )
    

with open(sys.argv[2], mode='w', encoding='U8') as outfile:
    lexicon.save(outfile)
logging.info(f"Converting completed.")
