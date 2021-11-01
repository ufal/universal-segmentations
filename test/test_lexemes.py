import unittest
from useg import SegLex

class TestLexemes(unittest.TestCase):
    def test_lexeme_creation_basic(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")

        self.assertIsNotNone(lex_id)
        self.assertIsInstance(lex_id, int)

    def test_lexeme_creation_not_id(self):
        lexicon = SegLex()
        lex_id_1 = lexicon.add_lexeme("example", "example", "NOUN")
        lex_id_2 = lexicon.add_lexeme("examples", "example", "NOUN")

        self.assertNotEqual(lex_id_1, lex_id_2)
