from collections import namedtuple

import seg_tsv

Lexeme = namedtuple("Lexeme", ["lex_id", "form", "lemma", "pos", "features", "morphemes"])
Morpheme = namedtuple("Morpheme", ["span", "features"])

class SegLex:
    """
    A lexicon of segmentations.

    Lexemes are identified using their IDs. Each lexeme has a string
    form, which can be subdivided into morph(eme)s. Multiple alternative
    subdivisions are possible, each identified by an annotation name.
    """

    __slots__ = ("_lexemes", )

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
            for annot_name in lexeme.morphemes:
                annot = lexeme.features.copy()
                assert "segmentation" not in annot and "" not in annot
                annot["annot_name"] = annot_name
                # TODO Ensure span is not already defined.
                annot["segmentation"] = [morpheme.features | {"span": morpheme.span}
                                         for morpheme in self.morphemes(
                                             lexeme.lex_id,
                                             annot_name,
                                             sort=True
                                         )]

                simple_seg = []
                last_morpheme = self.morpheme(lexeme.lex_id, annot_name, 0)
                morph_str = ""
                for i in range(len(lexeme.form)):
                    morpheme = self.morpheme(lexeme.lex_id, annot_name, i)
                    if morpheme is last_morpheme:
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
        """
        Return the string form of the lexeme with ID `lex_id`.
        """
        return self._lexemes[lex_id].form

    def lemma(self, lex_id):
        """
        Return the string lemma of the lexeme with ID `lex_id`.
        """
        return self._lexemes[lex_id].lemma

    def pos(self, lex_id):
        """
        Return the part-of-speech tag of the lexeme with ID `lex_id`.
        """
        return self._lexemes[lex_id].pos

    def print_lexeme(self, lex_id):
        """
        Return a stringified form of the lexeme with ID `lex_id`.

        This method is meant to be used for pretty-printing the lexeme
        in logs, not as a serialization format – for that, use the
        method `SegLex.save` instead.
        """
        return "{}({}#{})".format(self.form(lex_id), self.lemma(lex_id), self.pos(lex_id))

    def add_contiguous_morpheme(self, lex_id, annot_name, start, end, features=None):
        """
        Subdivide the lexeme with `lex_id` using a new morpheme starting
        at 0-indexed position `start` (inclusive) and continuing through
        position `end` (exclusive) on annotation layer `annot_name`. The
        annotation `features` is saved together with the newly-created
        morpheme.
        """
        self.add_morpheme(lex_id, annot_name, list(range(start, end)), features)

    def add_morpheme(self, lex_id, annot_name, span, features=None):
        """
        Subdivide the lexeme with `lex_id` using a new morpheme spanning
        integer positions enumerated in `span` on annotation layer
        `annot_name`. The annotation `features` is saved together with the
        newly-created morpheme.
        """

        # Check that the morpheme span actually exists in the lexeme.
        span = frozenset(span)
        for pos in span:
            if pos < 0 or pos >= len(self.form(lex_id)):
                raise ValueError(
                    "Morpheme span position {} is out-of-bounds in lexeme {}".format(
                        pos,
                        self.print_lexeme(lex_id)
                    )
                )

        if features is None:
            features = {}

        # Add the morpheme.
        morpheme = Morpheme(span, features)

        if annot_name not in self._lexemes[lex_id].morphemes:
            self._lexemes[lex_id].morphemes[annot_name] = [morpheme]
        else:
            self._lexemes[lex_id].morphemes[annot_name].append(morpheme)

    def morphemes(self, lex_id, annot_name, sort=False, position=None):
        """
        Get a list of all morphemes of lexeme with ID `lex_id` on
        annotation layer `annot_name`. If `position` is filled in,
        return only those covering that position. If there are no
        morphemes or none cover the position, an empty list is returned.
        If `sort` is True, sort the morphemes by their span.
        """
        if annot_name not in self._lexemes[lex_id].morphemes:
            return []
        elif position is None:
            # Return a copy to prevent accidental mangling.
            morphemes = self._lexemes[lex_id].morphemes[annot_name]
            if sort:
                return sorted(morphemes, key=lambda morpheme: tuple(sorted(morpheme.span)))
            else:
                return list(morphemes)
        else:
            if position < 0 or position >= len(self.form(lex_id)):
                raise ValueError("Invalid position {} in lexeme {}; is out of bounds in the form".format(position, self.print_lexeme(lex_id)))

            m = []
            for morpheme in self._lexemes[lex_id].morphemes[annot_name]:
                if position in morpheme.span:
                    m.append(morpheme)

            if sort:
                return sorted(m, key=lambda morpheme: tuple(sorted(morpheme.span)))
            else:
                return m

    def morpheme(self, lex_id, annot_name, position):
        """
        Return one of the morphemes found at `position` of annotation
        layer `annot_name` in lexeme `lex_id`. If there are multiple
        morphemes at this position, silently choose one. Return None
        if no such morphemes exist.
        """
        if position < 0 or position >= len(self.form(lex_id)):
            raise ValueError("Invalid position {} in lexeme {}; is out of bounds in the form".format(position, self.print_lexeme(lex_id)))

        if annot_name in self._lexemes[lex_id].morphemes:
            for morpheme in self._lexemes[lex_id].morphemes[annot_name]:
                if position in morpheme.span:
                    return morpheme

        return None
