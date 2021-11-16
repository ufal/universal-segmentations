#!/usr/bin/env python3

import logging
import re
import sys

from derinet import Lexicon
from derinet.utils import DerinetMorphError
from useg import SegLex

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

logger = logging.getLogger(__name__)


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


def record_boundaries(lexeme, segments):
    """
    The list of strings `segments` is the lexeme's lemma broken down into
    contiguous segments (potentially multi-morph). That means that boundaries
    between the segments are morph boundaries in lexeme. Record them.
    """
    position = 0
    for segment in segments:
        position += len(segment)
        lexeme.add_boundary(position, True)

def main():
    seg_lex = SegLex()

    lexicon = Lexicon()
    lexicon.load(sys.stdin)

    for lexeme in lexicon.iter_lexemes():
        feats = dict(lexeme.misc, **lexeme.feats)
        if "segmentation" in feats:
            feats["segmentation_stem"] = feats["segmentation"]
            del feats["segmentation"]
        lex_id = seg_lex.add_lexeme(lexeme.lemma, lexeme.lemma, lexeme.pos, feats)

        # Ignore lexemes which don't contain the necessary information.
        if "segmentation" not in lexeme.misc or "segmentation_hierarch" not in lexeme.misc:
            logger.warning("Lexeme {} doesn't contain segmentation information".format(lexeme))
            continue

        lemma = lexeme.lemma.lower()
        segments = lexeme.misc["segmentation"].lower().split(sep=";")
        flat_morphemes, hier_morphemes = hier_to_morphemes(lexeme.misc["segmentation_hierarch"].lower())

        # Fixup verbs, which lack the (inflectional) infinitive marker at
        #  the end.
        # FIXME this is probably mostly valid for German and Dutch, but
        #  definitely not for English.
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

        #print(flat_morphemes, hier_morphemes)

        # Record the boundaries present in the stem list.
        if "".join(segments) == lemma:
            # The boundaries can be simply concatenated, there are no
            #  phonological or other changes. Easy!
            #print("Stem segmentation success:", lemma, segments)
            record_boundaries(lexeme, segments)
        else:
            logger.info("Stem segmentation fail in {}: {}".format(lexeme, segments))
            pass

        # Record the boundaries present in the morpheme list.
        if "".join(flat_morphemes) == lemma:
            # The boundaries can be simply concatenated, there are no
            #  phonological or other changes. Easy!
            #print("Full morpheme segmentation success:", lemma, flat_morphemes)
            end = 0
            for morph in flat_morphemes:
                start = end
                end = start + len(morph)
                seg_lex.add_contiguous_morpheme(lex_id, "gCELEX", start, end, {"morpheme": morph})
        else:
            #print("Full morpheme segmentation fail:", lemma, flat_morphemes)

            # Try to record as many segments as possible from the start of
            #  the lemma.
            position = 0
            used_start_morphemes = 0
            for morpheme in flat_morphemes:
                if lemma.startswith(morpheme, position):
                    end_position = position + len(morpheme)
                    # FIXME check that we don't overlap an existing boundary
                    #  inferred from the stem segmentation.
                    #print("Partially start-segmenting", lemma, "with", morpheme, "at", position, end_position)
                    try:
                        seg_lex.add_contiguous_morpheme(lex_id, "gCELEX", position, end_position, {"morpheme": morpheme})
                    except DerinetMorphError as ex:
                        # FIXME we can probably use the hierarchical segmentation for this.
                        #  If the hier segmentation has three immediate constituents, these
                        #  should correspond to three stems. So we ought to know which stems
                        #  contain which morphemes. But I should verify this idea first.
                        logger.info("Morph segmentation overlaps with stem segmentation in {}: {}".format(lemma, ex))
                        break
                    position = end_position
                    used_start_morphemes += 1
                else:
                    break

            if position < 0 or position >= len(lemma):
                #assert False, "The lemma '{}' shouldn't have been fully segmented by '{}', because segmentation ought to have failed".format(lemma, flat_morphemes)
                # This happens e.g. in the lemma abtransport, which is
                #  segmented as ['ab', 'transport', 'ier']. It's probably
                #  an error in the data, which should be cleaned up.
                continue
            # Remember where the segmentation stopped matching.
            residual_morph_start = position

            # Now try to record as many segments as possible from the end.
            end_position = len(lemma)
            used_end_morphemes = 0
            for morpheme in reversed(flat_morphemes):
                position = end_position - len(morpheme)
                if lemma.startswith(morpheme, position):
                    #print("Partially end-segmenting", lemma, "with", morpheme, "at", position, end_position)
                    if position <= residual_morph_start:
                        # The segmentations from the start and end ran into
                        #  one another. That means there is a character in
                        #  the lemma which ought to belong to both of them.
                        #  For example, "Achtelliter" should be segmented as
                        #  "acht+tel+liter", making the "t" double-covered.
                        # This means the whole segmentation is unsound.
                        # FIXME remove the offending morpheme which was
                        #  added during the forward pass.
                        break
                    seg_lex.add_contiguous_morpheme(lex_id, "gCELEX", position, end_position, {"morpheme": morpheme})
                    end_position = position
                    used_end_morphemes += 1
                else:
                    break

            assert 0 < end_position <= len(lemma), "The lemma '{}' shouldn't have been fully segmented by '{}', because segmentation ought to have failed".format(lemma, flat_morphemes)
            residual_morph_end = end_position

            # If there is only one morpheme left, it must correspond to the
            #  part of the lemma that is unused.
            unused_morphemes = flat_morphemes[used_start_morphemes:len(flat_morphemes)-used_end_morphemes]

            # FIXME add the leftover part to the morpheme where it belongs,
            #  it is probably a duplicate character, as the extra `s` in
            #  'aussenantenne' → '['aus', 'en', 'antenne']'.
            #assert len(unused_morphemes) >= 1, "Segmentation of '{}' by '{}' failed, yet there are no unused morphemes".format(lemma, flat_morphemes)
            if len(unused_morphemes) < 1:
                continue

            # Record the residual morpheme.
            if len(unused_morphemes) == 1:
                try:
                    seg_lex.add_contiguous_morpheme(lex_id, "gCELEX", residual_morph_start, residual_morph_end, {"morpheme": unused_morphemes[0], "residual": True})
                    #print("Residual segmentation of", lemma, "succeeded by mapping", unused_morphemes[0], "to", lemma[residual_morph_start:residual_morph_end])
                except DerinetMorphError as ex:
                    logger.info("Residual segmentation of {} tried and failed because of residual morph overlap: {}".format(lexeme, flat_morphemes))
            else:
                logger.info("Residual segmentation fail in {}: {}".format(lexeme, flat_morphemes))

    seg_lex.save(sys.stdout)

if __name__ == "__main__":
    main()
