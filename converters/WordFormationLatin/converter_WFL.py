import argparse
import sys
import re

from seg_lex import SegLex

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--annot-name", required=True, help="The name to use for storing the segmentation annotation.")
    return parser.parse_args()

def parse_affix_info(x):
    """
    Take a string from WFL's 8th column as input and return:

     if it's a derivative:
     ('Derivation', morph, suffix/prefix)

    or

    if it's a compound:
    ('Compounding', list of references to parents)

    or

    if it's a conversion:
    ('Conversion')

    or

    if it's a root:
    ('Root')
    """

    if x == "":
        return (('Root'))
    else:
        affix_info = x.replace("&", "=").split("=")

        if affix_info[-1] == "Derivation":
            return (('Derivation', affix_info[1], affix_info[0]))
        elif affix_info[-1] == "Conversion":
            return (('Conversion'))
        elif affix_info[-1] == "Compounding":
            return (('Compounding', affix_info[1].split(".")))
        else:
            raise Exception("Unknown Word Formation Process")

def return_segmentation(x, prefixline=[], suffixline=[]):
    if type(x) != str:
        x = str(x)

    uderline = uder[x]

    affix_info = parse_affix_info(uder[x][-3])

    if affix_info == 'Root':
        return (prefixline + [uderline[1]] + suffixline)

    if affix_info == 'Conversion':
        return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))


    elif affix_info[0] == 'Derivation':
        if affix_info[-1] == 'Suffix':
            suffixline = [affix_info[1]] + suffixline
            # print(uderline)
            return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))
        elif affix_info[-1] == 'Prefix':
            prefixline = prefixline + [affix_info[1]]
            return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))
        else:
            raise Exception("What? Only 'Suffix' or 'Prefix' should be in the data! Unbelievable")

    elif affix_info[0] == 'Compounding':
        suffixline = [return_segmentation(i, prefixline=prefixline, suffixline=suffixline) for i in affix_info[1]]
        return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))

    else:
        raise Exception("What? Only Conv, Der, Comp, Root possible, but the data dropped {}".format(affix_info[0]))

def disambiguate_morphs(lemma, morphemelist):
    lst = []

    for morpheme in morphemelist:
        morpheme = morpheme.replace(" (negation)", "")
        morpheme = morpheme.replace("/", "|").replace("(", "[").replace(")", "]?")
        lst.append((re.search(morpheme, lemma).group(), re.search(morpheme, lemma).span()))

    return(lst)

def parse_feats(x):
    feats = x.split("&")

    dict = {}
    for i in feats:
        i = i.split("=")
        dict[i[0]] = i[1]
    return (dict)

def main(args):
    with open("converters/WordFormationLatin/UDer-1.1-la-WFL.tsv") as file:
        uder = {i.split("\t")[0]: i.split("\t")[1:] for i in file.readlines()}

    seg_lexicon = SegLex()

    for uder_key in uder.keys():
        uderline = uder[uder_key]
        seg_lexeme = seg_lexicon.add_lexeme(uderline[1],
                                            uderline[1],
                                            pos=uderline[2],
                                            features=parse_feats(uderline[3]))

        seg_lexicon.add_morphemes_from_list(seg_lexeme,
                                            return_segmentation(uder_key))

    seg_lexicon.save(sys.stdout)

if __name__ == "__main__":
    main(parse_args())