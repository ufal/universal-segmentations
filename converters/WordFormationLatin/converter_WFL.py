import argparse
import sys
import re

from seg_lex import SegLex

def is_substr(find, data):

    if len(data) < 1 and len(find) < 1:
        return(False)

    for i in range(len(data)):
        if find not in data[i]:
            return False

    return(True)

def lcs(x,y):
    data = [x,y]
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and is_substr(data[0][i:i+j], data):
                    substr = data[0][i:i+j]
    return(substr)

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

def return_segmentation(x, data, prefixline=[], suffixline=[]):
    if type(x) != str:
        x = str(x)

    uderline = data[x]

    affix_info = parse_affix_info(data[x][-3])

    if affix_info == 'Root':
        return (prefixline + [((uderline[1]), "root")] + suffixline)

    if affix_info == 'Conversion':
        return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))


    elif affix_info[0] == 'Derivation':
        if affix_info[-1] == 'suffix':
            suffixline = [((affix_info[1]), "Suffix")] + suffixline
            # print(uderline)
            return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))
        elif affix_info[-1] == 'prefix':
            prefixline = prefixline + [((affix_info[1]), "Prefix")]
            return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))
        else:
            raise Exception("What? Only 'Suffix' or 'Prefix' should be in the data! Unbelievable")

    elif affix_info[0] == 'Compounding':
        suffixline = [((return_segmentation(i, prefixline=prefixline, suffixline=suffixline), "Root")) for i in affix_info[1]]
        return (return_segmentation(uderline[-4], prefixline=prefixline, suffixline=suffixline))

    else:
        raise Exception("What? Only Conv, Der, Comp, Root possible, but the data dropped {}".format(affix_info[0]))

def disambiguate_morphs(lemma, morphemelist):
    lst = []
    morphemelist = [i[0] for i in morphemelist]

    for morpheme in morphemelist:
        morpheme = morpheme.replace(" (negation)", "").replace(" (entering)", "")
        morpheme = morpheme.replace("/", "|").replace("(", "[").replace(")", "]?")
        match = re.search(morpheme, lemma)
        if match is not None:
            lst.append((match.group(), match.span()))
        else:
            longest_common_string = lcs(morpheme, lemma)
            lst.append((longest_common_string, re.search(longest_common_string, lemma).span()))

    return(lst)

def parse_feats(x):
    if x == [] or x == "" or x is None:
        return None
    else:
        feats = x.split("&")

        dict = {}
        for i in feats:
            i = i.split("=")
            dict[i[0]] = i[1]
        return (dict)

def main():
    uder = {i.split("\t")[0]: i.split("\t")[1:] for i in sys.stdin}
    seg_lexicon = SegLex()
    print("seglex")

    for uder_key in uder.keys():
        uderline = uder[uder_key]

        morphemelist = return_segmentation(uder_key, uder)
        lemma = uderline[1]
        lexid = uderline[0]

        print("uder_key")

        morpheme_strings = [i[0] for i in morphemelist]
        morphs = disambiguate_morphs(morpheme_strings, uder)

        morpheme_annotations = [i[1] for i in morphemelist]

        seg_lexeme = seg_lexicon.add_lexeme(uderline[1],
                                            uderline[1],
                                            pos=uderline[2],
                                            features=parse_feats(uderline[3]))
        for index,morph in enumerate(morphs):
            seg_lexicon.add_contiguous_morpheme(lex_id=seg_lexeme,
                                                annot_name=morph,
                                                start=morph[1][0],
                                                end=morph[1][1],
                                                features={"type": morphemelist[index][1],
                                                          "morpheme": morphemelist[index][0]})

    seg_lexicon.save(sys.stdout)

if __name__ == "__main__":
    main()