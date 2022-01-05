#!/usr/bin/env python3

import multiprocessing
if __name__ == "__main__":
    multiprocessing.set_start_method('forkserver')

import argparse
from os import path
import sys

from useg import SegLex

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("seg_lex", nargs='*', help="The USeg file(s) to compute statictics of")
    parser.add_argument("--printer", choices=("tex", "tsv"), default="tex", help="The format to use for printing")
    parser.add_argument("--only", choices=("both", "left", "right"), default="both", help="Which parts of the table to print")
    parser.add_argument("--threads", type=int, default=1, help="The number of worker threads to run in parallel")
    return parser.parse_args()


class TypeTokenStats(object):
    __slots__ = ("_types", "_tokens", "_min", "_max", "_length", "_length_counts")

    def __init__(self):
        self._types = set()
        self._tokens = 0

        self._min = float('inf')
        self._max = 0
        self._length = 0

        self._length_counts = {}

    def record(self, string):
        self._types.add(string)
        self._tokens += 1

        l = len(string)

        self._min = min(self._min, l)
        self._max = max(self._max, l)
        self._length += l

        if l in self._length_counts:
            self._length_counts[l] += 1
        else:
            self._length_counts[l] = 1

    def type_count(self):
        return len(self._types)

    def token_count(self):
        return self._tokens

    def min_length(self):
        return self._min

    def max_length(self):
        return self._max

    def mean_length(self):
        if self._tokens == 0:
            return 0.0
        return self._length / self._tokens

    def count_of_length(self, l):
        """
        Return how many tokens have length of `l`.
        """
        return self._length_counts.get(l, 0)

    def count_of_length_ge(self, min_l):
        """
        Return how many tokens have length of at least `min_l`.
        """
        total = 0
        for l, c in self._length_counts.items():
            if l >= min_l:
                total += l
        return total

    def freq_of_length(self, l):
        """
        Return the proportion of tokens which have length of `l`.
        """
        tokens = self.token_count()
        if tokens == 0:
            return 0

        return self.count_of_length(l) / tokens

    def freq_of_length_ge(self, min_l):
        """
        Return the proportion of tokens which have length of at least `min_l`.
        """
        tokens = self.token_count()
        if tokens == 0:
            return 0

        return self.count_of_length_ge(min_l) / tokens


def morph(form, morpheme):
    """
    Return the string form of `morpheme`.
    """
    if morpheme.span:
        span = sorted(morpheme.span)

        last_idx = span[0]
        morph = form[last_idx]

        for idx in span[1:]:
            if idx == last_idx + 1:
                # This part of the morph is contiguous.
                morph += form[idx]
            else:
                morph += " + " + form[idx]
            last_idx = idx

        return morph
    else:
        # Empty morpheme spans are weird, but support them anyway.
        return ""

def process_file(filename):
    seg_lex = SegLex()
    try:
        seg_lex.load(filename)
    except Exception as exc:
        print("Cannot load file {}".format(filename), file=sys.stderr)
        raise exc

    lexeme_cnt = 0
    segmented_lexeme_cnt = 0

    form_stats = TypeTokenStats()
    lemma_stats = TypeTokenStats()
    pos_stats = TypeTokenStats()
    morpheme_stats = TypeTokenStats()
    morph_stats = TypeTokenStats()
    root_stats = TypeTokenStats()
    prefix_stats = TypeTokenStats()
    suffix_stats = TypeTokenStats()
    annot_stats = TypeTokenStats()

    morph_stats_types = {"root": root_stats,
                         "prefix": prefix_stats,
                         "suffix": suffix_stats}

    morph_count_counts = {}

    for lex_id in seg_lex.iter_lexemes():
        lexeme_cnt += 1
        form_stats.record(seg_lex.form(lex_id))
        lemma_stats.record(seg_lex.lemma(lex_id))
        pos_stats.record(seg_lex.pos(lex_id))

        is_segmented = False

        for annot_name in seg_lex.annot_names(lex_id):
            annot_stats.record(annot_name)

            morphemes = seg_lex.morphemes(lex_id, annot_name)

            if morphemes:
                is_segmented = True

            for morpheme in morphemes:
                morph_string = morph(seg_lex.form(lex_id), morpheme)
                morph_stats.record(morph_string)

                if "morpheme" in morpheme.features:
                    morpheme_stats.record(morpheme.features["morpheme"])

                if "type" in morpheme.features and isinstance(morpheme.features["type"], str) and morpheme.features["type"] in morph_stats_types:
                    morph_stats_types[morpheme.features["type"]].record(morph_string)

            morph_count = len(morphemes)
            if morph_count in morph_count_counts:
                morph_count_counts[morph_count] += 1
            else:
                morph_count_counts[morph_count] = 1

        if is_segmented:
            segmented_lexeme_cnt += 1

    resource_name = filename
    dirname = path.basename(path.dirname(resource_name))
    if dirname:
        resource_name = dirname

    annot_cnt = annot_stats.token_count()

    #print("Length counts for {}:".format(resource_name), morph_stats._length_counts, file=sys.stderr)

    return (
        resource_name,
        lexeme_cnt,
        #segmented_lexeme_cnt,
        #form_stats.type_count(),
        #lemma_stats.type_count(),
        #pos_stats.type_count(),

        #morph_stats.type_count(),
        #root_stats.type_count(),
        #prefix_stats.type_count(),
        #suffix_stats.type_count(),

        #morph_stats.token_count(),
        #root_stats.token_count(),
        #prefix_stats.token_count(),
        #suffix_stats.token_count(),

        #morph_count_counts.get(0, 0),
        morph_count_counts.get(1, 0),
        morph_count_counts.get(2, 0),
        morph_count_counts.get(3, 0),
        sum([cc for c, cc in morph_count_counts.items() if c >= 4]),

        form_stats.mean_length(),
        morph_stats.mean_length(),

        morph_stats.token_count() / annot_cnt if annot_cnt > 0 else 0.0,
        #morph_stats.min_length(),
        #morph_stats.mean_length(),  # Already above
        #morph_stats.max_length(),

        root_stats.token_count() / annot_cnt if annot_cnt > 0 else 0.0,
        #root_stats.min_length(),
        #root_stats.mean_length(),
        #root_stats.max_length(),

        prefix_stats.token_count() / annot_cnt if annot_cnt > 0 else 0.0,
        #prefix_stats.min_length(),
        #prefix_stats.mean_length(),
        #prefix_stats.max_length(),

        suffix_stats.token_count() / annot_cnt if annot_cnt > 0 else 0.0,
        #suffix_stats.min_length(),
        #suffix_stats.mean_length(),
        #suffix_stats.max_length(),
    )

def prn_tsv(*args):
    print(*args, sep="\t", end="\n")

def prn_tex(*args):
    print(*("{:,.2f}".format(arg) if isinstance(arg, float) else "{:,}".format(arg) if isinstance(arg, int) else str(arg).replace("_", r"\_") for arg in args), sep=" & ", end=" \\\\\n")

def get_prn(t):
    if t == "tsv":
        return prn_tsv
    elif t == "tex":
        return prn_tex

def main(args):
    prn = get_prn(args.printer)

    if args.printer == "tex":
        if args.only == "both":
            print(r"\begin{tabular}{lr|rrrr|rrrrrrr} \toprule")
            print(r"              &      & \multicolumn{4}{c}{Morpheme count} & Mean word & Mean morph & Morphs  & Morph  & Roots per & Prefixes  & Suffixes \\")
            print(r"Resource name & Size & 1 & 2 & 3 & 4+                     & length    & length     & per lex & avg. len & lexeme & per lexeme & per lex \\ \midrule")
        elif args.only == "left":
            print(r"\begin{tabular}{lr|rrrr|rr} \toprule")
            print(r"              &      & \multicolumn{4}{c}{Morpheme count} & Mean word     & Mean morph \\")
            print(r"Resource name & Size & 1 & 2 & 3 & 4+                     & length [char] & length [char] \\ \midrule")
        elif args.only == "right":
            print(r"\begin{tabular}{rrrr} \toprule")
            print(r"Morphs  & Roots per & Prefixes  & Suffixes \\")
            print(r"per lex & lexeme   & per lexeme & per lex \\ \midrule")
    else:
        to_print = []
        if args.only in {"left", "both"}:
            to_print += [
                "Resource name",
                #"Lexemes",
                #"Segmented lexemes",
                "Size", #"Forms",
                #"Lemmas",
                #"POSes",

                #"Morph types",
                #"Root types",
                #"Prefix types",
                #"Suffix types",

                #"Morph tokens",
                #"Root tokens",
                #"Prefix tokens",
                #"Suffix tokens",

                "Words with 1 morpheme",
                "Words with 2 morphemes",
                "Words with 3 morphemes",
                "Words with 4+ morphemes",

                "Mean word len",
                "Mean morph len",
            ]
        if args.only in {"right", "both"}:
            to_print += [
                "Morphs per lexeme",
                #"Morph min",
                #"Morph avg.", # Already above
                #"Morph max",

                "Roots per lexeme",
                #"Root min",
                #"Root avg.",
                #"Root max",

                "Prefixes per lexeme",
                #"Prefix min",
                #"Prefix avg.",
                #"Prefix max",

                "Suffixes per lexeme",
                #"Suffix min",
                #"Suffix avg.",
                #"Suffix max",
            ]
        prn(*to_print)

    with multiprocessing.Pool(args.threads) as pool:
        for ret in pool.imap(process_file, args.seg_lex, 1):
            if args.only == "both":
                prn(*ret)
            elif args.only == "left":
                prn(*ret[:8])
            elif args.only == "right":
                prn(*ret[8:])
            else:
                raise ValueError("Unknown `only` {}".format(args.only))

    if args.printer == "tex":
        print("\\bottomrule\n\\end{tabular}")


if __name__ == "__main__":
    main(parse_args())
