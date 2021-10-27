#!/usr/bin/env python3
"""
Read a DeriNet-2.0-formatted file from STDIN, extract segmentations from
it, convert it to the Universal Segmentations format and print it to
STDOUT.
"""

import argparse
import sys

from derinet import Lexicon
from useg.seg_lex import SegLex

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--annot-name", required=True, help="The name to use for storing the segmentation annotation.")
    return parser.parse_args()

def main(args):
    der_lexicon = Lexicon()
    der_lexicon.load(sys.stdin)

    seg_lexicon = SegLex()

    for der_lexeme in der_lexicon.iter_lexemes(sort=False):
        seg_lexeme = seg_lexicon.add_lexeme(der_lexeme.lemma, der_lexeme.lemma, pos=der_lexeme.pos, features=der_lexeme.feats)
        for morpheme in der_lexeme.segmentation:
            features = {k: v for k, v in morpheme.items() if k not in {"Start", "End", "Type", "Morph"}}

            if "Type" in morpheme:
                features["type"] = morpheme["Type"].lower()

            seg_lexicon.add_contiguous_morpheme(seg_lexeme, args.annot_name, morpheme["Start"], morpheme["End"], features=features)

    seg_lexicon.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())
