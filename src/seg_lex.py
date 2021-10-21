class SegLex:
    """
    A lexicon of segmentations.

    Lexemes are identified using their IDs. Each lexeme has a string
    form, which can be subdivided into morphs. Multiple alternative
    subdivisions are possible, each identified by an annotation name.
    """

    def __init__(self):
        raise NotImplementedError()

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

    def create_lexeme(self, form, lemma, features=None):
        """
        Create a new lexeme with the specified form, lemma and
        morphological features. Returns an ID of the created lexeme.
        """
        raise NotImplementedError()

    def delete_lexeme(self, lex_id):
        """
        Deletes the lexeme with the specified ID from the lexicon.
        """
        raise NotImplementedError()

    def add_contiguous_morph(self, lex_id, annot_name, start, end, annot=None):
        """
        Subdivide the lexeme with `lex_id` using a new morpheme starting
        at 0-indexed position `start` (inclusive) and continuing through
        position `end` (exclusive) on annotation layer `annot_name`. The
        annotation `annot` is saved together with the newly-created
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
