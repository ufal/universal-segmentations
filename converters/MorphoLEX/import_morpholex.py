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
from useg.infer_bounds import infer_bounds

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("morpholex", type=argparse.FileType("rb"), help="The name to use for storing the segmentation annotation.")
    parser.add_argument("--annot-name", required=True, help="The name to use for storing the segmentation annotation.")
    parser.add_argument("--allomorphs", required=True, type=argparse.FileType("rt", encoding="utf-8", errors="strict"), help="A file to load allomorphy information from.")
    return parser.parse_args()

def parse_segmentation_eng(s):
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
            morphemes.extend(parse_segmentation_eng(stem))
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

def parse_segmentation_fra(s):
    # The French segmentation seems not to be recursive and has no stem
    #  marks.
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
            # There may be parentheses inside, so we have to scan for
            #  a matching paren.
            paren_depth = 1
            end = None
            for i, char in enumerate(rest[1:], start=1):
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1

                if paren_depth == 0:
                    end = i
                    break
            else:
                raise ValueError("Unbalanced parentheses in '{}'".format(s))
        else:
            raise ValueError("Unparseable segmentation '{}'".format(s))

        morpheme = rest[1:end]
        morphemes.append((morpheme, t))
        rest = rest[end + 1:]

    return morphemes

def load_allomorphs(f):
    m = {}

    for line in f:
        allomorphs = line.rstrip().split("\t")
        morpheme = allomorphs[0]
        m[morpheme] = allomorphs

    return m

def gen_morphs_eng(allomorphs, morpheme):
    m, t = morpheme

    if m in allomorphs:
        morphs = list(allomorphs[m])
    else:
        morphs = [m]

    g_morphs = list(morphs)
    for morph in morphs:
        # All the tests below require nonempty morph string.
        if not morph:
            print("Warning: empty allomorph of morpheme '{}' detected.".format(m), file=sys.stderr)
            continue

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
        # FIXME if there are multiple o's, generate the last one? Or all possibilities?
        last_o = morph.rfind("o")
        if last_o != -1 and (last_o == len(morph) - 1 or morph[last_o + 1] != "u"):
            morph_ou = morph[:last_o] + "ou" + morph[last_o + 1:]
            g_morphs.append(morph_ou)

    return (g_morphs, t)

def gen_morphs_fra(allomorphs, morpheme):
    m, t = morpheme

    # Some French morphemes end in numerals. This seems to be an error.
    #  Delete the numeral.
    if re.search(r"\d$", m) is not None:
        m = re.sub(r"\d*$", "", m)

    if m in allomorphs:
        morphs = list(allomorphs[m])
    else:
        morphs = [m]

    g_morphs = []
    # Iterate over the list in a weird way, because we need to change
    #  it while iterating and have the new elements be visible in the
    #  loop.
    i = 0
    while i < len(morphs):
        morph = morphs[i]
        i += 1

        if "/" in morph:
            if morph == "ant/ent":
                morphs.append("ant")
                morphs.append("ent")
                continue

            parts = morph.split("/")
            assert len(parts) == 2, "More than two alternatives are not supported"
            base, alt = parts
            morphs.append(base)
            for n in range(min(len(alt) + 1, len(base))):
                # Try to delete up to n + 1 characters from the base
                #  and replace them with the alternative suffix.
                # Don't use base[:-n], because -0 == 0 == empty word.
                remaining = len(base) - n
                morphs.append(base[:remaining] + alt)

            continue
        else:
            # The morpheme itself is one of the morphs.
            g_morphs.append(morph)

    return (g_morphs, t)

def add_endings_eng(form, joined_segmentation, morphemes):
    if form.endswith("ingly") and morphemes[-1][0][0] == "ly" and not joined_segmentation.endswith("ingly"):
        morphemes = morphemes[:-1] + [(["ing"], "suffix")] + [morphemes[-1]]

    if form.endswith("ings") and not joined_segmentation.endswith("ings"):
        morphemes.append((["ing"], "suffix"))
        morphemes.append((["s"], "suffix"))
        return morphemes

    if form[-3:] in {"ing", "n't", "'ll", "'re", "'ve"}:
        s = form[-3:]
        if not joined_segmentation.endswith(s):
            morphemes.append(([s], "suffix"))
        return morphemes

    if form[-2:] in {"'s", "'d"}:
        s = form[-2:]
        if not joined_segmentation.endswith(s):
            morphemes.append(([s], "suffix"))
        return morphemes

    if form[-2:] == "ed":
        if joined_segmentation[-1] == "e":
            morphemes.append((["ed", "d"], "suffix"))
        elif not joined_segmentation.endswith("ed"):
            morphemes.append((["ed"], "suffix"))
        return morphemes

    if form[-2:] == "id" and joined_segmentation[-1] == "y":
        morphemes.append((["ed", "d"], "suffix"))
        return morphemes

    if form[-1] == "s" and joined_segmentation[-1] != "s":
        if form[-2:] == "es" and joined_segmentation[-1] != "e":
            morphemes.append((["s", "es"], "suffix"))
        else:
            morphemes.append((["s"], "suffix"))
        return morphemes

    return morphemes

def record_morphemes(seg_lex, lex_id, annot_name, form, morphemes):
    # First, generate all allomorph combinations to map.
    # Generate the initial state.
    parses = []
    morphs, t = morphemes[0]
    for morph in morphs:
        # Record the initial parse.
        parses.append([morph])

    # Lengthen each combination, until we consume all morphemes.
    for morphs, t in morphemes[1:]:
        next_parses = []

        for morph in morphs:
            for parse in parses:
                next_parses.append(parse + [morph])

        parses = next_parses

    # Map each combination to the form and select the best one.
    best_cost = float("inf")
    best_mapping = None
    for parse in parses:
        mapping, cost = infer_bounds(parse, form)
        if cost < best_cost:
            best_cost = cost
            best_mapping = mapping

    if best_mapping[0] != 0:
        print("Ignored prefix '{}' of {}".format(form[:best_mapping[0]], form), file=sys.stderr)
    if best_mapping[-1] != len(form):
        print("Ignored suffix '{}' of {}".format(form[best_mapping[-1]:], form), file=sys.stderr)


    for i, (morphs, t) in enumerate(morphemes):
        start = best_mapping[i]
        end = best_mapping[i + 1]
        morpheme = morphs[0]

        if start < end:
            seg_lex.add_contiguous_morpheme(lex_id, annot_name, start, end, {"morpheme": morpheme, "type": t})
        else:
            print("Missed morpheme nr. {} '{}' in {}".format(i+1, morpheme, form), file=sys.stderr)

def main(args):
    lexicon = SegLex()
    allomorphs = load_allomorphs(args.allomorphs)

    sheets = pd.read_excel(args.morpholex, sheet_name=None, header=0, dtype=str, engine="openpyxl", na_filter=False)
    for sheet_name, sheet in sheets.items():
        match = re.fullmatch("[0-9]+-[0-9]+-[0-9]+", sheet_name)
        if match is not None:
            if "Word" in sheet.columns:
                lang = "eng"
            elif "item" in sheet.columns:
                lang = "fra"
            else:
                assert False, "Unknown language"

            for line_no, line in enumerate(sheet.itertuples(name="MorphoLEX")):
                # Note: some words are in uppercase, for whatever reason.
                if lang == "eng":
                    # The English data stores the word form in `Word`.
                    form = line.Word
                else:
                    # The French data documents the form as being stored
                    #  in `Word`, but it is actually in `item`.
                    form = line.item

                if not form:
                    print("No form found at sheet {}, line {}.".format(sheet_name, line_no), file=sys.stderr)
                    continue

                lform = form.lower()

                # This test is imperfect – if one character contracts
                #  while another elongates, we will not detect it and
                #  the mapping will be skewed.
                if len(lform) != len(form):
                    print("Word '{}' changes length when lowercasing; this will cause issues.".format(form), file=sys.stderr)

                if lang == "eng":
                    # The English data has parts of speech, with
                    #  possibly multiple options per lexeme.
                    pos = line.POS
                    poses = set(pos.split("|"))

                    segmentation = line.MorphoLexSegm
                    segmentation = parse_segmentation_eng(segmentation)
                    morphemes = [gen_morphs_eng(allomorphs, morpheme) for morpheme in segmentation]

                    if line.ELP_ItemID:
                        # Some English lexemes have interlinked IDs,
                        #  some don't.
                        features = {"elp_id": int(line.ELP_ItemID)}
                    else:
                        features = None
                else:
                    # The French data has no POSes and the IDs are
                    #  probably not interlinked with anything.
                    pos = ""

                    segmentation = line.canon_segm
                    segmentation = parse_segmentation_fra(segmentation)
                    morphemes = [gen_morphs_fra(allomorphs, morpheme) for morpheme in segmentation]

                    features = None





                lex_id = lexicon.add_lexeme(form, form, pos, features)

                joined_segmentation = "".join([m for m, t in segmentation])
                if lang == "eng":
                    morphemes = add_endings_eng(lform, joined_segmentation, morphemes)

                record_morphemes(lexicon, lex_id, args.annot_name, lform, morphemes)

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

    lexicon.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())
