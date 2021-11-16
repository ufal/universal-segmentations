#!/usr/bin/env python3

import argparse
import logging
import re
import sys

from derinet import Lexicon
from derinet.utils import DerinetMorphError
from useg import SegLex
from useg.infer_bounds import infer_bounds

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--lang", required=True, choices=("deu", "eng", "nld"), help="The language code of the resource to convert.")
    return parser.parse_args()

hier_extract_regex = re.compile("\((.*)\)\[[^][]*\]")
def hier_to_morphemes(s):
    """
    Parse the hierarchical information `s` from a CELEX lexeme info to a list
    of morphemes contained therein.

    Example: (((arbeit)[V],(er)[N|V.])[N],((dicht)[V],(er)[N|V.])[N])[N]
    """
    match = hier_extract_regex.fullmatch(s)
    if not match:
        # The hierarchy is not further subdivisible, therefore the entire string
        #  is the morpheme we were looking for.
        return [s], s

    inside = match[1]

    flat_morphemes = []
    hier_morphemes = []

    paren_level = 0
    part = ""

    # Use a very naive recursive algorithm for parsing the content in parentheses.
    for char in inside:
        if paren_level < 0:
            raise ValueError("Paren level must not be negative in '{}'".format(s))

        if char == "," and paren_level == 0:
            flat_parsed_part, hier_parsed_part = hier_to_morphemes(part)
            flat_morphemes += flat_parsed_part
            hier_morphemes.append(hier_parsed_part)
            part = ""
        elif char == "(":
            paren_level += 1
            part += char
        elif char == ")":
            paren_level -= 1
            part += char
        else:
            part += char

    # Parse the last part, which has no ',' after it.
    flat_parsed_part, hier_parsed_part = hier_to_morphemes(part)
    flat_morphemes += flat_parsed_part
    hier_morphemes.append(hier_parsed_part)

    return flat_morphemes, hier_morphemes


def main(args):
    seg_lex = SegLex()

    lexicon = Lexicon()
    lexicon.load(sys.stdin)

    annot_name = {"deu": "gCELEX",
                  "eng": "eCELEX",
                  "nld": "dCELEX"}[args.lang]

    for lexeme in lexicon.iter_lexemes():
        feats = dict(lexeme.misc, **lexeme.feats)
        if "segmentation" in feats:
            feats["segmentation_stem"] = feats["segmentation"]
            del feats["segmentation"]
        lex_id = seg_lex.add_lexeme(lexeme.lemma, lexeme.lemma, lexeme.pos, feats)

        # Ignore lexemes which don't contain the necessary information.
        if "segmentation" not in lexeme.misc or "segmentation_hierarch" not in lexeme.misc:
            logger.info("Lexeme {} doesn't contain segmentation information".format(lexeme))
            continue

        lemma = lexeme.lemma.lower()
        segments = lexeme.misc["segmentation"].lower().split(sep=";")
        flat_morphemes, hier_morphemes = hier_to_morphemes(lexeme.misc["segmentation_hierarch"].lower())

        # Fixup verbs, which lack the (inflectional) infinitive marker at
        #  the end.
        # FIXME this is probably mostly valid for German and Dutch, but
        #  definitely not for English.
        if args.lang == "deu":
            if lexeme.pos == "VERB":
                if lemma.endswith("en"):
                    segments.append("en")
                    flat_morphemes.append("en")
                    hier_morphemes.append(["en"])
                elif lemma.endswith("ln") or lemma.endswith("rn") or lemma.endswith("in") or lemma.endswith("tun"):
                    segments.append("n")
                    flat_morphemes.append("n")
                    hier_morphemes.append(["n"])
                else:
                    logger.warning("Unknown verbal ending in {}".format(lexeme))

        bounds, cost = infer_bounds(flat_morphemes, lemma)

        assert len(bounds) == len(flat_morphemes) + 1

        if bounds[0] != 0:
            logger.warning("Ignored prefix '{}' of {} segmented as {}".format(lemma[:bounds[0]], lemma, lexeme.misc["segmentation_hierarch"]))
        if bounds[-1] != len(lemma):
            logger.warning("Ignored suffix '{}' of {} segmented as {}".format(lemma[bounds[-1]:], lemma, lexeme.misc["segmentation_hierarch"]))

        for i, morpheme in enumerate(flat_morphemes):
            start = bounds[i]
            end = bounds[i + 1]
            morpheme = flat_morphemes[i]

            if start < end:
                seg_lex.add_contiguous_morpheme(lex_id, annot_name, start, end, {"morpheme": morpheme})
            else:
                logger.error("Missed morpheme nr. {} '{}' in {} segmented as {}".format(i+1, morpheme, lemma, lexeme.misc["segmentation_hierarch"]))

        if cost > 0.0:
            logger.info("Fuzziness {} needed when mapping {} to {} as {}".format(cost, lexeme.misc["segmentation_hierarch"], lemma, " + ".join(seg_lex._simple_seg(lex_id, annot_name))))

    seg_lex.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())
