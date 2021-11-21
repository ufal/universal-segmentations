#!/usr/bin/env python3
"""
Read the Uniparser XML-like file with analyses from STDIN, convert it
to the Universal Segmentations format and print it to STDOUT.
"""

import sys
import xml.etree.ElementTree as ET

from useg import SegLex

gr_upos_table = {
    "A": "X", # TODO
    "ADJ": "ADJ",
    "ADJPRO": "X", # TODO
    "ADV": "ADV",
    "ADVPRO": "X", # TODO
    "CNJ": "CCONJ", # TODO or SCONJ as well?
    "IMIT": "X", # TODO
    "INTRJ": "INTJ",
    "N": "NOUN",
    "NUM": "NUM",
    "PARENTH": "X", # TODO
    "PART": "PART",
    "POST": "ADP",
    "PREDIC": "X", # TODO
    "PREP": "ADP",
    "PRO": "PRON",
    "V": "VERB",
}

def gr_to_upos(morpho_tags):
    """
    Convert morphological information from the `gr` format stored in
    the parsed wordlist to an universal POS tag.
    """
    gr_pos = morpho_tags[0]
    if gr_pos == "N" and len(morpho_tags) >= 2 and morpho_tags[1] == "PN":
        return "PROPN"
    else:
        return gr_upos_table.get(gr_pos, "X")

def main():
    lexicon = SegLex()
    annot_name = "Uniparser UDM"

    for line in sys.stdin:
        line = line.rstrip()
        try:
            w = ET.fromstring(line)
        except ET.ParseError as exc:
            print("Unparseable line '{}'".format(line), file=sys.stderr)
            raise exc
        assert w.tag == "w"

        form = "".join(w.itertext())
        # If there is a dash in the word form, it means problems for
        #  parsing the segmentation information, which marks segment
        #  boundaries with dashes. But if the dash is at the very
        #  beginning or end of the form, it marks an affix and is not
        #  included in the segmentation markup, therefore not causing
        #  problems.
        has_dash = "-" in form[1:-1]

        for ana in w:
            assert ana.tag == "ana"
            lex = ana.attrib["lex"]
            gr = ana.attrib["gr"]
            parts = ana.attrib["parts"]
            gloss = ana.attrib["gloss"]
            features = {k: v for k, v in ana.attrib.items() if k not in {"lex", "gr", "parts", "gloss"} and v}

            # TODO what are these two?
            #lex2 = ana.attrib["lex2"]
            #trans_ru2 = ana.attrib["trans_ru2"]

            if "<" in gloss:
                print("Problematic infixation (?) in {} {} {} {}, skipping".format(form, lex, gloss, parts), file=sys.stderr)
                continue

            morphemes = gloss.split("-")

            # The length-mismatch detection is there to detect words
            #  which have a dash in them, but the dash corresponds to
            #  a morph boundary.
            # Theoretically, it is possible for a word to have two
            #  dashes, one boundary-making and the other one
            #  stem-internal. That case cannot be solved by the code
            #  below, but it is fortunately not encountered in the data.
            if len(parts.split("-")) != len(morphemes) and has_dash:
                # We have a problem, the form of the word contains
                #  a dash and the morph list is therefore not easily
                #  parseable.
                if len(morphemes) == 1:
                    # But there is only one morph here, so we can easily
                    #  recover.
                    morphs = [parts]
                else:
                    # The segmentation cannot be easily analyzed.
                    # Go morph-by-morph and try to find where the dash
                    #  is supposed to go.
                    morphs = parts.split("-")

                    prefix = ""
                    i = 0
                    while i < len(morphs):
                        assert form.startswith(prefix), \
                            "Prefix '{}' not in form '{}'".format(prefix, form)

                        morph = morphs[i]

                        if form[len(prefix)] == "-":
                            prefix += '-' + morph

                            if i > 0:
                                # This morph should be concatenated with the
                                #  previous one.
                                morphs[i-1] += '-' + morph
                                morphs = morphs[:i] + morphs[i+1:]

                            # Repeat the cycle with the same `i`.
                            continue
                        else:
                            prefix += morph
                            i += 1
            else:
                morphs = parts.split("-")

            if len(morphs) != len(morphemes):
                print("The morph and morpheme lists don't match for line '{}'".format(line), file=sys.stderr)
                continue

            morpho_tags = gr.split(",")
            pos = gr_to_upos(morpho_tags)

            features["morpho_tags"] = morpho_tags

            lexeme = lexicon.add_lexeme(form, lex, pos=pos, features=features)

            end = 0
            # There is some infixation, in which case there are multiple
            #  stems with an infix in between them. Detect infixes by
            #  counting stems and considering everything between them an
            #  infix.
            nr_stems = sum(m == "STEM" for m in morphemes)
            seen_stems = 0
            # Remember the span of the stem, which may be discontiguous
            #  due to the infixes.
            stem_morph_span = []

            for morph, morpheme in zip(morphs, morphemes):
                if form[end] == "-" and not morph.startswith("-"):
                    # The word form starts with a dash, indicating its
                    #  affixal nature; or contains a dash, representing
                    #  a connector. The dash is not part of the
                    #  segmentation, and should not be (at least in the
                    #  first case). Skip it.
                    lexicon.add_contiguous_morpheme(
                        lexeme,
                        annot_name,
                        end,
                        end + 1,
                        # FIXME the type should be different when it is
                        #  at the beginning or end of the word – attachment
                        #  point, maybe?
                        features={"morpheme": "-", "type": "connector"}
                    )
                    start = end + 1
                else:
                    start = end

                end = start + len(morph)

                if morpheme == "STEM":
                    seen_stems += 1
                    stem_morph_span += list(range(start, end))
                    # We add the stem last, to account for discontiguous
                    #  stems.
                    continue
                elif seen_stems == nr_stems:
                    morpheme_type = "suffix"
                elif seen_stems == 0:
                    morpheme_type = "prefix"
                else:
                    morpheme_type = "infix"

                lexicon.add_contiguous_morpheme(
                    lexeme,
                    annot_name,
                    start,
                    end,
                    features={"morpheme": morpheme, "type": morpheme_type}
                )

            if stem_morph_span:
                # Add the (potentially discontiguous) stem morpheme.
                lexicon.add_morpheme(
                    lexeme,
                    annot_name,
                    stem_morph_span,
                    features={"type": "stem"}
                )
            else:
                assert nr_stems == 0
                print("Stemless word form '{}' detected".format(form), file=sys.stderr)

            if end == len(form) - 1 and form[end] == "-":
                # The word ends with a dash, which we didn't process before.
                #  Add it as a connector now.
                lexicon.add_contiguous_morpheme(
                    lexeme,
                    annot_name,
                    end,
                    end + 1,
                    # FIXME the type should be different when it is
                    #  at the beginning or end of the word – attachment
                    #  point, maybe?
                    features={"morpheme": "-", "type": "connector"}
                )

                end += 1

            assert end == len(form), "We didn't process the whole word '{}'".format(form)

    lexicon.save(sys.stdout)

if __name__ == "__main__":
    main()
