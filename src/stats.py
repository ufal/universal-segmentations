#!/usr/bin/env python3

import multiprocessing
if __name__ == "__main__":
    multiprocessing.set_start_method('forkserver')

import argparse
from os import path

from useg import SegLex

def parse_args():
    parser = argparse.ArgumentParser(
        allow_abbrev=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("seg_lex", nargs='*', help="The USeg file(s) to compute statictics of")
    parser.add_argument("--printer", choices=("tex", "tsv"), default="tex", help="The format to use for printing")
    parser.add_argument("--threads", type=int, default=1, help="The number of worker threads to run in parallel")
    return parser.parse_args()


class TypeTokenStats(object):
    __slots__ = ("_types", "_tokens", "_min", "_max", "_length")

    def __init__(self):
        self._types = set()
        self._tokens = 0

        self._min = float('inf')
        self._max = 0
        self._length = 0

    def record(self, string):
        self._types.add(string)
        self._tokens += 1

        self._min = min(self._min, len(string))
        self._max = max(self._max, len(string))
        self._length += len(string)

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
    seg_lex.load(filename)

    lexeme_cnt = 0
    segmented_lexeme_cnt = 0

    form_stats = TypeTokenStats()
    lemma_stats = TypeTokenStats()
    pos_stats = TypeTokenStats()
    morpheme_stats = TypeTokenStats()
    morph_stats = TypeTokenStats()
    annot_stats = TypeTokenStats()

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
                morph_stats.record(morph(seg_lex.form(lex_id), morpheme))

                if "morpheme" in morpheme.features:
                    morpheme_stats.record(morpheme.features["morpheme"])

        if is_segmented:
            segmented_lexeme_cnt += 1

    resource_name = filename
    dirname = path.basename(path.dirname(resource_name))
    if dirname:
        resource_name = dirname

    return (
        resource_name,
        lexeme_cnt,
        segmented_lexeme_cnt,
        form_stats.type_count(),
        lemma_stats.type_count(),
        pos_stats.type_count(),

        form_stats.mean_length(),

        morph_stats.token_count(),
        morph_stats.type_count(),
        morph_stats.min_length(),
        morph_stats.mean_length(),
        morph_stats.max_length(),
        # TODO the same for roots, prefixes, suffixes.
    )

def prn_tsv(*args):
    print(*args, sep="\t", end="\n")

def prn_tex(*args):
    print(*args, sep=" & ", end=" \\\\\n")

def get_prn(t):
    if t == "tsv":
        return prn_tsv
    elif t == "tex":
        return prn_tex

def main(args):
    if args.printer == "tex":
        print("\\begin{tabular}{lrrrrrrrrrrr} \\toprule")
    prn = get_prn(args.printer)
    prn("Resource name",
        "Lexeme count",
        "Segmented lexeme count",
        "Form count",
        "Lemma count",
        "POS count",

        "Avg. form length",

        "Morph token count",
        "Morph type count",
        "Min morph length",
        "Avg. morph length",
        "Max morph length",
    )
    if args.printer == "tex":
        print("\midrule")

    with multiprocessing.Pool(args.threads) as pool:
        for ret in pool.imap(process_file, args.seg_lex, 1):
            prn(*ret)

    if args.printer == "tex":
        print("\\bottomrule\n\\end{tabular}")


if __name__ == "__main__":
    main(parse_args())
