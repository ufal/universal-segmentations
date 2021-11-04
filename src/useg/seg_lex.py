from collections import namedtuple

from useg import seg_tsv

Lexeme = namedtuple("Lexeme", ["lex_id", "form", "lemma", "pos", "features", "morphemes"])
Morpheme = namedtuple("Morpheme", ["span", "features"])

class SegLex:
    """
    A lexicon of segmentations.

    Lexemes are identified using their IDs. Each lexeme has a string
    form, which can be subdivided into morph(eme)s. Multiple alternative
    subdivisions are possible, each identified by an annotation name.
    """

    __slots__ = ("_lexemes", "_poses", "_forms")

    def __init__(self):
        self._lexemes = []
        self._poses = {}
        self._forms = {}

    def load(self, f):
        """
        Load the lexicon from `f`, which is either an open file-like
        object open for reading text or a string filename, and add all
        information contained therein to the internal lexicon of this
        object.
        """

        # If f is a filename, we open the file ourselves and therefore
        #  should also close it after reading from it.
        actual_f = None
        close_at_end = False

        try:
            if isinstance(f, str):
                close_at_end = True
                actual_f = open(f, "rt", encoding="utf-8")
            else:
                # We assume f is already an open file object.
                actual_f = f

            for line in actual_f:
                record = seg_tsv.parse_line(line)
                features = {k: v for k, v in record.annot.items() if k not in {"annot_name", "segmentation"}}

                if "segmentation" in record.annot:
                    if "annot_name" not in record.annot:
                        # Unnamed segmentation. Reject it.
                        raise ValueError("Line '{}' has unnamed segmentation".format(line))

                    annot_name = record.annot["annot_name"]
                    segmentation = record.annot["segmentation"]
                else:
                    segmentation = []

                lexeme = self.add_lexeme(record.form, record.lemma, record.pos, features)

                for segment in segmentation:
                    span = segment["span"]
                    del segment["span"]
                    self.add_morpheme(lexeme, annot_name, span, segment)
        finally:
            if actual_f is not None and close_at_end:
                actual_f.close()

    def _as_records(self):
        """
        Iterate over the lexicon as a sequence of SegRecords (not sorted).
        """
        for lexeme in self._lexemes:
            if not lexeme.morphemes:
                # Return a lexeme with no records in it, because the
                #  loop below is not going to execute.
                assert "segmentation" not in lexeme.features and "annot_name" not in lexeme.features
                yield seg_tsv.SegRecord(lexeme.form, lexeme.lemma, lexeme.pos, [], lexeme.features)

            for annot_name in lexeme.morphemes:
                annot = lexeme.features.copy()
                assert "segmentation" not in annot and "annot_name" not in annot
                annot["annot_name"] = annot_name
                # TODO Ensure span is not already defined.
                annot["segmentation"] = [{**morpheme.features, "span": morpheme.span}
                                         for morpheme in self.morphemes(
                                             lexeme.lex_id,
                                             annot_name,
                                             sort=True
                                         )]

                simple_seg = []
                last_morpheme = self.morpheme(lexeme.lex_id, annot_name, 0)
                morph_str = ""
                for i, char in enumerate(lexeme.form):
                    morpheme = self.morpheme(lexeme.lex_id, annot_name, i)
                    if morpheme is last_morpheme:
                        morph_str += char
                    else:
                        last_morpheme = morpheme
                        simple_seg.append(morph_str)
                        morph_str = char
                simple_seg.append(morph_str)

                yield seg_tsv.SegRecord(lexeme.form, lexeme.lemma, lexeme.pos, simple_seg, annot)

    def save(self, f):
        """
        Save the lexicon to `f`, which is either an open file-like
        object open for writing or appending text, or a string filename.
        """
        # Sort the lexicon and iterate over it, producing the TSV output.
        # TODO include the keys and values of features in the sorting as
        #  well.
        records = sorted(
            self._as_records(),
            key=lambda r: (r.lemma, r.pos, r.form, r.simple_seg, len(r.annot))
        )

        # If f is a filename, we open the file ourselves and therefore
        #  should also close it after writing to it.
        actual_f = None
        close_at_end = False

        try:
            if isinstance(f, str):
                close_at_end = True
                actual_f = open(f, "wt", encoding="utf-8", newline="\n")
            else:
                # We assume f is already an open file object.
                actual_f = f

            for record in records:
                actual_f.write(seg_tsv.format_record(record, False))

        finally:
            if actual_f is not None:
                actual_f.flush()
                if close_at_end:
                    actual_f.close()


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

        # Add the lexeme to the lookup dicts.
        if pos in self._poses:
            if lemma in self._poses[pos]:
                self._poses[pos][lemma].append(lex_id)
            else:
                self._poses[pos][lemma] = [lex_id]
        else:
            self._poses[pos] = {lemma: [lex_id]}

        if form in self._forms:
            self._forms[form].append(lex_id)
        else:
            self._forms[form] = [lex_id]

        return lex_id

    def iter_lexemes(self, form=None, lemma=None, pos=None):
        """
        Find all lexemes with the specified properties. If neither
        `form`, `lemma` or `pos` are specified, iterate over all
        lexemes in the lexicon.

        Return an iterator over IDs of matching lexemes.
        """
        if form is not None:
            # Use the `form` dict for lookup.
            if form in self._forms:
                for lex_id in self._forms[form]:
                    if (lemma is None or self.lemma(lex_id) == lemma) \
                       and (pos is None or self.pos(lex_id) == pos):
                        yield lex_id

            return

        # `form` is None, so use the `pos` dict for lookup.

        if pos is None and lemma is None:
            # No constraints specified, iterate over the whole lexicon.
            # TODO when deleting lexemes, what happens to the
            #  slot in the _lexemes?
            yield from range(len(self._lexemes))
            return

        # Either POS or lemma is specified. Find all applicable POSes
        #  (there may be multiple if `pos` is None).
        if pos is None:
            poses = self._poses.values()
        elif pos in self._poses:
            poses = (self._poses[pos], )
        else:
            # A POS was specified, but is not found.
            return

        if lemma is None:
            # Yield all lexemes with the specified POS.
            for lemmas in poses:
                for lexemes in lemmas.values():
                    yield from lexemes
        else:
            # We have a dictionary for the applicable part-of-speech and
            #  a given lemma to search for.
            for lemmas in poses:
                if lemma in lemmas:
                    yield from lemmas[lemma]

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

    def features(self, lex_id):
        """
        Return the `features` dict of lexeme with ID `lex_id`. You can
        freely edit the information therein.
        """
        return self._lexemes[lex_id].features

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

    def add_morphemes_from_list(self, lex_id, annot_name, morphemes):
        """
        If `morphemes` is a list of morph strings which, when
        concatenated, produce exactly the form of lexeme `lex_id`, add
        morphemes corresponding to the morphs.

        If any morphs don't correspond to their respective piece
        of the form, add no morphemes and raise an error.
        """
        form = self.form(lex_id)
        to_add = []
        end = 0
        for morpheme in morphemes:
            start = end
            if isinstance(morpheme, str):
                morph = morpheme
            else:
                raise NotImplementedError("Only strings are supported as morphemes, {} given.".format(morpheme.__class__))

            if form.startswith(morph, start):
                end = start + len(morph)
                to_add.append((start, end, None))
            else:
                raise ValueError("Morph '{}' not found in form '{}' at position {} (possibly because an earlier morph blocked it).".format(morph, form, start))

        for start, end, features in to_add:
            self.add_contiguous_morpheme(lex_id, annot_name, start, end, features)

    def morphemes(self, lex_id, annot_name, sort=False, position=None):
        """
        Get a list of all morphemes of lexeme with ID `lex_id` on
        annotation layer `annot_name`. If `position` is filled in,
        return only those covering that position. If there are no
        morphemes or none cover the position, an empty list is returned.
        If `sort` is True, sort the morphemes by their span.
        """
        if annot_name not in self._lexemes[lex_id].morphemes:
            # The annotation layer is not present, so there are no
            #  annotations there.
            return []

        if position is None:
            # Return all morphemes on the annotation layer.
            # Return a copy to prevent accidental mangling.
            morphemes = self._lexemes[lex_id].morphemes[annot_name]
            if sort:
                return sorted(morphemes, key=lambda morpheme: tuple(sorted(morpheme.span)))
            else:
                return list(morphemes)
        else:
            # Return only morphemes at the specified position.
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

    def morph(self, lex_id, annot_name, position):
        """
        Return the string form of one of the morphemes found at
        `position` of annotation layer `annot_name` in lexeme `lex_id`,
        or None if no such morpheme exists.

        FIXME this API is really unwieldy, come up with something
        better? Maybe introduce morpheme IDs, like we have lex IDs?
        """
        morpheme = self.morpheme(lex_id, annot_name, position)

        if morpheme is None:
            return None

        if morpheme.span:
            form = self.form(lex_id)
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
