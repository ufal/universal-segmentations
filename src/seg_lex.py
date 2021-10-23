from collections import namedtuple

import seg_tsv

Lexeme = namedtuple("Lexeme", ["lex_id", "form", "lemma", "pos", "features", "morphs"])
Morph = namedtuple("Morph", ["span", "features"])

class SegLex:
    """
    A lexicon of segmentations.

    Lexemes are identified using their IDs. Each lexeme has a string
    form, which can be subdivided into morphs. Multiple alternative
    subdivisions are possible, each identified by an annotation name.
    """

    __slots__ = "_lexemes"

    def __init__(self):
        self._lexemes = []

    def load(self, f):
        """
        Load the lexicon from the open file-like object `f` and add all
        information contained therein to the internal lexicon of this
        object.
        """
        raise NotImplementedError()

    def _as_records(self):
        """
        Iterate over the lexicon as a sequence of SegRecords (not sorted).
        """
        for lexeme in self._lexemes:
            for annot_name in lexeme.morphs:
                annot = lexeme.features.copy()
                assert "segmentation" not in annot and "" not in annot
                annot["annot_name"] = annot_name
                # TODO Ensure span is not already defined.
                annot["segmentation"] = [morph.features | {"span": morph.span}
                                         for morph in lexeme.morphs[annot_name]]

                simple_seg = []
                last_morpheme = self.morph(lexeme.lex_id, annot_name, 0)
                morph_str = ""
                for i in range(len(lexeme.form)):
                    morpheme = self.morph(lexeme.lex_id, annot_name, i)
                    if morpheme == last_morpheme:
                        morph_str += lexeme.form[i]
                    else:
                        last_morpheme = morpheme
                        simple_seg.append(morph_str)
                        morph_str = lexeme.form[i]
                simple_seg.append(morph_str)

                yield seg_tsv.SegRecord(lexeme.form, lexeme.lemma, lexeme.pos, simple_seg, annot)

    def save(self, f):
        """
        Save the lexicon to the open file-like object `f`.
        """
        # Sort the lexicon and iterate over it, producing the TSV output.
        # TODO include the keys and values of features in the sorting as
        #  well.
        records = sorted(
            self._as_records(),
            key=lambda r: (r.lemma, r.pos, r.form, r.simple_seg, len(r.annot))
        )

        for record in records:
            f.write(seg_tsv.format_record(record))

        f.flush()


    def add_lexeme(self, form, lemma, pos, features=None):
        """
        Create a new lexeme with the specified form, lemma and
        morphological features. Returns an ID of the created lexeme.
        """
        if features is None:
            features = {}

        lex_id = len(self._lexemes)
        lexeme = Lexeme(lex_id, form, lemma, pos, features, {})
        self._lexemes.append(lexeme)

        return lex_id

    def delete_lexeme(self, lex_id):
        """
        Deletes the lexeme with the specified ID from the lexicon.
        """
        raise NotImplementedError()

    def form(self, lex_id):
        return self._lexemes[lex_id].form

    def lemma(self, lex_id):
        return self._lexemes[lex_id].lemma

    def pos(self, lex_id):
        return self._lexemes[lex_id].pos

    def print_lexeme(self, lex_id):
        return "{}({}#{})".format(self.form(lex_id), self.lemma(lex_id), self.pos(lex_id))

    def add_contiguous_morph(self, lex_id, annot_name, start, end, features=None):
        """
        Subdivide the lexeme with `lex_id` using a new morpheme starting
        at 0-indexed position `start` (inclusive) and continuing through
        position `end` (exclusive) on annotation layer `annot_name`. The
        annotation `features` is saved together with the newly-created
        morph.
        """
        self.add_morph(lex_id, annot_name, list(range(start, end)), features)

    def add_morph(self, lex_id, annot_name, span, features):
        """
        Subdivide the lexeme with `lex_id` using a new morpheme spanning
        integer positions enumerated in `span` on annotation layer
        `annot_name`. The annotation `features` is saved together with the
        newly-created morph.
        """

        # Check that the morph span actually exists in the lexeme.
        span = frozenset(span)
        for pos in span:
            if pos < 0:
                raise ValueError(
                    "Morph span position {} is out-of-bounds in lexeme {}".format(
                        pos,
                        self.print_lexeme(lex_id)
                    )
                )
            if pos > len(self.form(lex_id)):
                raise ValueError(
                    "Morph span position {} is out-of-bounds in lexeme {}".format(
                        pos,
                        self.print_lexeme(lex_id)
                    )
                )

        # The string form of the morph.
        morph = "".join([self.form(lex_id)[i] for i in sorted(span)])

        if features is None:
            features = {}

        # Add the morph.
        morph = Morph(span, features)

        if annot_name not in self._lexemes[lex_id].morphs:
            self._lexemes[lex_id].morphs[annot_name] = [morph]
        else:
            self._lexemes[lex_id].morphs[annot_name].append(morph)

    def morphs(self, lex_id, annot_name, position=None):
        """
        Get a list of all morphs of lexeme with ID `lex_id` on
        annotation layer `annot_name`. If `position` is filled in,
        return only those covering that position. If there are no
        morphs or none cover the position, an empty list is returned.
        """
        if annot_name not in self._lexemes[lex_id].morphs:
            return []
        elif position is None:
            # Return a copy to prevent accidental mangling.
            return list(self._lexemes[lex_id].morphs[annot_name])
        else:
            m = []
            for morph in self._lexemes[lex_id].morphs[annot_name]:
                if position in morph.span:
                    m.append(morph)
            return m

    def morph(self, lex_id, annot_name, position):
        """
        Return one of the morphs found at `position` of annotation layer
        `annot_name` in lexeme `lex_id`. If there are multiple morphs at
        this position, silently choose one. Return none if no such morphs
        exist.
        """
        if annot_name in self._lexemes[lex_id].morphs:
            for morph in self._lexemes[lex_id].morphs[annot_name]:
                if position in morph.span:
                    return morph

        return None
