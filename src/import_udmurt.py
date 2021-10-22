#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET

from seg_lex import SegLex

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

    for line in sys.stdin:
        line = line.rstrip()
        w = ET.fromstring(line)
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
            trans_ru = ana.attrib["trans_ru"]

            # TODO what are these two?
            #lex2 = ana.attrib["lex2"]
            #trans_ru2 = ana.attrib["trans_ru2"]

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
                        assert form.startswith(prefix), "Prefix '{}' not in form '{}'".format(prefix, form)

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

                    #print("Unparseable dashed word '{}' found, skipping.".format(form), file=sys.stderr)
                    #continue
            else:
                morphs = parts.split("-")

            assert len(morphs) == len(morphemes), "The morph and morpheme lists don't match for line '{}'".format(line)

            morpho_tags = gr.split(",")
            pos = gr_to_upos(morpho_tags)

            features = {
                "morpho_tags": morpho_tags,
                "trans_ru": trans_ru
            }

            lexeme = lexicon.add_lexeme(form, lex, pos=pos, features=features)

            end = 0
            for morph, morpheme in zip(morphs, morphemes):
                start = end
                end += len(morph)

                lexicon.add_contiguous_morph(lexeme, "Uniparser UDM", start, end, annot={"morpheme": morpheme})

    lexicon.save(sys.stdout)

if __name__ == "__main__":
    main()
