from collections import namedtuple

Lexeme = namedtuple("Lexeme", ["lex_id", "form", "lemma", "pos", "features", "morphs"])

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

    def save(self, f):
        """
        Save the lexicon to the open file-like object `f`.
        """
        raise NotImplementedError()
        # TODO Sort the lexicon and iterate over it, producing the
        #  TSV output.

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
        raise NotImplementedError()

    def get_morphs(self, lex_id, annot_name):
        """
        Get a list of all morphs of lexeme with ID `lex_id` on
        annotation layer `annot_name`.
        """
        raise NotImplementedError()

    def get_morph(self, lex_id, annot_name, position):
        raise NotImplementedError()
