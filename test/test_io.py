from io import StringIO
import unittest

from useg import SegLex

class TestIO(unittest.TestCase):
    def test_load_empty(self):
        # Test loading an empty lexicon.
        str_io = StringIO()
        seg_lex = SegLex()

        seg_lex.load(str_io)

        self.assertEqual([], list(seg_lex.iter_lexemes()))

    def test_save_empty(self):
        # Test saving an empty lexicon.
        str_io = StringIO()
        seg_lex = SegLex()

        seg_lex.save(str_io)

        str_io.seek(0)
        content = str_io.read()

        self.assertEqual("", content)

    def test_save_lexemes_count(self):
        # Test saving lexemes with no segmentation.
        str_io = StringIO()
        seg_lex = SegLex()

        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("examples", "example", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("exemplar", "exemplar", "ADJ")
        seg_lex.save(str_io)

        str_io.seek(0)
        content = str_io.read()

        self.assertEqual(6, content.count("\n"))
