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

hier_extract_regex = re.compile("\((.*)\)\[([^][]*)\]")
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
    tags = match[2]

    div = tags.find("|")
    if div == -1:
        # The divisor is not there, therefore the brackets contain just
        #  the POS tag.
        pos = tags
        t = "root"
    else:
        pos = tags[:div]
        affix_mark = tags[div + 1:]
        dot_position = affix_mark.find(".")
        assert dot_position != -1, "No dot in {}".format(s)
        previous = affix_mark[:dot_position]
        following = affix_mark[dot_position + 1:]

        t = None
        if not previous or set(previous) == {"x"}:
            # No previous morphemes or only other prefixes.
            t = "prefix"
        if not following or set(following) == {"x"}:
            # No following morphemes or only other suffixes.
            # Sometimes a lone dot is also used for weird marking of roots.
            if t is None:
                t = "suffix"
            elif t == "prefix":
                logger.warning("Dot used for marking a root in {}".format(s))
                t = "root"
            else:
                assert False
        if t is None:
            # Between two roots/stems.
            t = "interfix"

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
            if len(flat_parsed_part) == 1 and isinstance(flat_parsed_part[0], str):
                flat_morphemes.append({"type": t, "morpheme": flat_parsed_part[0]})
            else:
                assert t == "root", "String {} denotes a multi-morpheme affix".format(s)
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
    if len(flat_parsed_part) == 1 and isinstance(flat_parsed_part[0], str):
        flat_morphemes.append({"type": t, "morpheme": flat_parsed_part[0]})
    else:
        assert t == "root", "String {} denotes a multi-morpheme affix".format(s)
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
                    flat_morphemes.append({"type": "suffix", "morpheme": "en"})
                    hier_morphemes.append(["en"])
                elif lemma.endswith("ln") or lemma.endswith("rn") or lemma.endswith("in") or lemma.endswith("tun"):
                    segments.append("n")
                    # TODO The morpheme should be "en" here, only the morph is "n".
                    flat_morphemes.append({"type": "suffix", "morpheme": "n"})
                    hier_morphemes.append(["n"])
                else:
                    logger.warning("Unknown verbal ending in {}".format(lexeme))
            elif lexeme.pos == "NOUN":
                if flat_morphemes[-1]["morpheme"] == "bieg" and lemma.endswith("bogen"):
                    segments.append("en")
                    flat_morphemes[-1]["morpheme"] = "bog"
                    flat_morphemes.append({"type": "suffix", "morpheme": "en"})
                    hier_morphemes.append(["en"])
                if flat_morphemes[-1]["morpheme"] == "tu" and lemma.endswith("tat"):
                    # Manually fix allomorphy.
                    #  FIXME do the same for segments and hier_morphemes.
                    flat_morphemes[-1]["morpheme"] = "tat"
                elif lemma.endswith("t") and flat_morphemes[-1]["morpheme"].endswith("h"):
                    segments.append("t")
                    flat_morphemes.append({"type": "suffix", "morpheme": "t"})
                    hier_morphemes.append(["t"])
                elif lemma.endswith("d") and flat_morphemes[-1]["morpheme"].endswith("g"):
                    segments.append("d")
                    flat_morphemes.append({"type": "suffix", "morpheme": "d"})
                    hier_morphemes.append(["d"])
                elif lemma.endswith("e") and not flat_morphemes[-1]["morpheme"].endswith("e"):
                    segments.append("e")
                    flat_morphemes.append({"type": "suffix", "morpheme": "e"})
                    hier_morphemes.append(["e"])
            elif lexeme.pos == "ADP":
                if lemma.endswith("er") and not flat_morphemes[-1]["morpheme"].endswith("er"):
                    segments.append("er")
                    flat_morphemes.append({"type": "suffix", "morpheme": "er"})
                    hier_morphemes.append(["er"])

        bounds, cost = infer_bounds([m["morpheme"] for m in flat_morphemes], lemma)

        assert len(bounds) == len(flat_morphemes) + 1

        if bounds[0] != 0:
            logger.warning("Ignored prefix '{}' of {} segmented as {}".format(lemma[:bounds[0]], lemma, lexeme.misc["segmentation_hierarch"]))
        if bounds[-1] != len(lemma):
            logger.warning("Ignored suffix '{}' of {} segmented as {}".format(lemma[bounds[-1]:], lemma, lexeme.misc["segmentation_hierarch"]))

        for i, morpheme in enumerate(flat_morphemes):
            start = bounds[i]
            end = bounds[i + 1]

            if start < end:
                seg_lex.add_contiguous_morpheme(lex_id, annot_name, start, end, morpheme)
            else:
                logger.error("Missed morpheme nr. {} '{}' in {} segmented as {}".format(i+1, morpheme["morpheme"], lemma, lexeme.misc["segmentation_hierarch"]))

        if cost > 0.0:
            logger.info("Fuzziness {} needed when mapping {} to {} as {}".format(cost, lexeme.misc["segmentation_hierarch"], lemma, " + ".join(seg_lex._simple_seg(lex_id, annot_name))))

    seg_lex.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())
