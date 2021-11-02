#!/usr/bin/env python3
"""
Read a MorphoLEX XLSX file, extract segmentations from it, convert it
to the Universal Segmentations format and print it to STDOUT.
"""

# Needs pandas and openpyxl

import argparse
import pandas as pd
import re
import sys

from useg import SegLex

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("morpholex", type=argparse.FileType("rb"), help="The name to use for storing the segmentation annotation.")
    parser.add_argument("--annot-name", required=True, help="The name to use for storing the segmentation annotation.")
    parser.add_argument("--allomorphs", required=True, type=argparse.FileType("rt", encoding="utf-8", errors="strict"), help="A file to load allomorphy information from.")
    return parser.parse_args()

def parse_segmentation(s):
    morphemes = []
    rest = s

    while rest:
        if rest[0] == "<":
            # Prefix.
            t = "prefix"
            end = rest.index("<", 1)
        elif rest[0] == ">":
            # Suffix.
            t = "suffix"
            end = rest.index(">", 1)
        elif rest[0] == "(":
            # Root.
            t = "root"
            end = rest.index(")", 1)
        elif rest[0] == "{":
            # Stem.
            # There can be recursive substems, so we have to parse the
            #  brackets by counting, making sure to skip over any inner
            #  matching pairs.
            # The recursive stems are probably an error in the original
            #  data.
            depth = 1
            for i in range(1, len(rest)):
                if rest[i] == "{":
                    depth += 1
                elif rest[i] == "}":
                    depth -= 1

                if depth == 0:
                    end = i
                    break

            stem = rest[1:end]
            # TODO Somehow record stem information and return it.
            morphemes.extend(parse_segmentation(stem))
            rest = rest[end + 1:]
            continue
        else:
            raise ValueError("Unparseable segmentation '{}'".format(s))

        morpheme = rest[1:end]
        morphemes.append((morpheme, t))
        rest = rest[end + 1:]

    # Check that there are no stray punctuation symbols (typically
    #  misplaced parentheses or braces) in the morpheme. That would
    #  indicate an error in the annotation. But apostrophes are
    #  naturally found in the English data and underscores are used to
    #  distinguish homonyms, so ignore those.
    for m, t in morphemes:
        assert m.replace("'", "").replace("_", "").isalpha(), "Morpheme '{}' of segmentation {} is not purely alphabetical.".format(m, s)

    return morphemes

def load_allomorphs(f):
    m = {}

    for line in f:
        allomorphs = line.rstrip().split("\t")
        morpheme = allomorphs[0]
        m[morpheme] = allomorphs

    return m

def gen_morphs(allomorphs, morpheme):
    m, t = morpheme

    if m in allomorphs:
        morphs = list(allomorphs[m])
    else:
        morphs = [m]

    g_morphs = list(morphs)
    # Iterate over the list in a weird way, because we need to change
    #  it while iterating and have the new elements be visible in the
    #  loop.
    i = 0
    while i < len(morphs):
        morph = morphs[i]
        i += 1

        # All the tests below require nonempty morph string.
        if not morph:
            print("Warning: empty allomorph of morpheme '{}' detected.".format(m), file=sys.stderr)
            continue

        if len(morph) >= 2 and morph[-1] == "e":
            # Append to the source list, because e.g. "reassured" needs
            #  both e-deletion and reduplication.
            morphs.append(morph[:-1])
            g_morphs.append(morph[:-1])

        if morph[0] in {"f", "m", "p", "s", "z"}:
            # Reduplication at the start.
            g_morphs.append(morph[0] + morph)
        if morph[0] == "k":
            # Reduplication of c + k at the start.
            g_morphs.append("c" + morph)

        if morph[-1] in {"b", "d", "g", "k", "l", "m", "n", "p", "r", "s", "t", "v", "z"}:
            # Reduplication at the end.
            g_morphs.append(morph + morph[-1])
        if morph[-1] == "c":
            # Reduplication of c + k at the end.
            g_morphs.append(morph + "k")
        if morph[-1] == "y":
            # Change of y->i at the end (e.g. anchovy - anchovies).
            g_morphs.append(morph[:-1] + "i")
        if morph[-1] == "f":
            # Change of f->v at the end (e.g. wolf - wolves).
            g_morphs.append(morph[:-1] + "v")

        # Change o -> ou.
        ou = re.sub(r"o([^u])", r"ou\1", morph)
        if ou != morph:
            g_morphs.append(ou)

    return (g_morphs, t)

def main(args):
    lexicon = SegLex()
    allomorphs = load_allomorphs(args.allomorphs)

    sheets = pd.read_excel(args.morpholex, sheet_name=None, header=0, dtype=str, engine="openpyxl", na_filter=False)
    for sheet_name, sheet in sheets.items():
        match = re.fullmatch("[0-9]+-[0-9]+-[0-9]+", sheet_name)
        if match is not None:
            for line in sheet.itertuples(name="MorphoLEX"):
                # Note: some words are in uppercase, for whatever reason.
                form = line.Word
                lform = form.lower()

                # This test is imperfect – if one character contracts
                #  while another elongates, we will not detect it and
                #  the mapping will be skewed.
                if len(lform) != len(form):
                    print("Word '{}' changes length when lowercasing; this will cause issues.".format(form), file=sys.stderr)

                poses = set(line.POS.split("|"))

                lexeme = lexicon.add_lexeme(form, form, line.POS, {"elp_id": int(line.ELP_ItemID)})

                segmentation = line.MorphoLexSegm
                morphemes = [gen_morphs(allomorphs, morpheme) for morpheme in parse_segmentation(segmentation)]

                # Generate the initial parses.
                parses = []
                morphs, t = morphemes[0]
                for morph in morphs:
                    if lform.startswith(morph):
                        # Record the initial parse.
                        parses.append(([(morph, t)], len(morph)))

                # Try to lengthen each parse, until we consume all morphemes.
                for morphs, t in morphemes[1:]:
                    next_parses = []

                    for morph in morphs:
                        for parse, end in parses:
                            start = end

                            if lform.startswith(morph, start):
                                # Success!
                                # Record the successful potential parse in next_parses.
                                next_parses.append((parse + [(morph, t)], start + len(morph)))
                            else:
                                # This parse failed, discard it.
                                pass

                    parses = next_parses

                if not parses:
                    # Error, no possible parses found.
                    # TODO
                    print("Err-stem", form, segmentation, sep="\t", end="\n")
                    continue

                # If there are unconsumed chars left, they may be one of
                #  the inflectional morphemes: {"s", "'s", "ed", "ing", "ings", "n't", "'d", "'ll", "'re", "'ve"}
                final_parses = []
                for parse, end in parses:
                    if end == len(lform):
                        final_parses.append(parse)
                    elif end < len(lform):
                        unmatched_suffix = lform[end:]

                        if unmatched_suffix == "ings":
                            parse.append(("ing", "suffix"))
                            parse.append(("s", "suffix"))
                            final_parses.append(parse)
                        elif unmatched_suffix in {"s", "'s", "es", "ed", "ing", "n't", "'d", "'ll", "'re", "'ve"}:
                            parse.append((unmatched_suffix, "suffix"))
                            final_parses.append(parse)
                    else:
                        raise Exception("We've parsed text longer than the form. ERROR!")

                if not final_parses:
                    # Error, no possible parses found.
                    # TODO
                    print("Err-suffix", form, segmentation, sep="\t", end="\n")
                    continue

                for i, parse in enumerate(final_parses):
                    print("OK-{}".format(i), form, " + ".join([morph for morph, t in parse]), sep="\t", end="\n")

                # FIXME multiple parses caused by deletion of e + -es.
                #  Triple parse in e.g. licensees, refugees

                # If NN, then it may end in plural "s" or "es".
                # If VB, it may end in 3rd person present singular "s" or "es".
                #  Similarly for NN|VB and VB|NN.
                # If VB|NN, NN|VB or VB|NN|JJ, it may end in "ing".
                # If VB, JJ or VB|JJ, it may end in "ed".
                # If encl or NN|encl, it may end in "'s".

                # We need to resolve allomorphy somehow. E.g. (tech) may match "techno".

                # Some morphemes (roots only?) contain underscores. Probably to resolve homonymy?

                # Errors in the DB:
                #  ogr-e
                #  ogr-es
                #  plum-es
                #  grat-es
                #  flu-es
                #  du-es
                #  dud-es
                #  dam-es
                #  crimin-g
                #  barge-es ?
                #  vulv-a
                #  val-e
                #  spir-e
                #  spir-es
                #  spor-e
                #  spor-es
                #  premier-es
                #  segmentation in, spir, ion, al of 'inspirational'   (missing -ate-)
                #  segmentation re, class, ify, ion of 'reclassification'   (dtto)

                # Unparseable segmentation:
                # DALY (9355 in 0-1-0)
                # gotten (23448 in 0-1-0)
                # FLOCCULATED (3764 in 0-1-1) has recursive stems
                # backboard (6361 in 0-2-0) and a few immediately following lexemes have switched brackets
                # complexions (2004 in 1-1-0) is in a wrong sheet and misses a bracket
                # impunity (4305 in 1-1-0) dtto
                # complexion (5085 in 1-1-0) dtto
                # staminate (6506 in 0-1-1) have an extra bracket
                # quintet (7767 in 0-1-1) and following 2 words
                # alternating (13198 in 0-1-1)
                # backyard (6382 in 0-2-0) and backyards (next line)
                # triplicated (4 in 1-2-1) and following several lexemes have a recursive root
                # intermediaries (18 in 1-2-1) and following
                #  and several others in that sheet

    #lexicon.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())
