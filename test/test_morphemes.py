import unittest
from useg import SegLex
from useg.seg_lex import Morpheme

class TestMorphemes(unittest.TestCase):
    def test_listing_single_morpheme(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4)

        self.assertIsInstance(lexicon.morpheme(lex_id, "Test segmentation", 0),
                              Morpheme)
        self.assertEqual(1, len(lexicon.morphemes(lex_id, "Test segmentation", position=0)))
        self.assertIs(lexicon.morpheme(lex_id, "Test segmentation", 0),
                      lexicon.morphemes(lex_id, "Test segmentation", position=0)[0])

    def test_morpheme_features(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4, {"my_data": "abc"})

        self.assertEqual(Morpheme({0, 1, 2, 3}, {"my_data": "abc"}),
                         lexicon.morpheme(lex_id, "Test segmentation", 0))

    def test_listing_nonexistent_morpheme(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4)

        self.assertEqual([], lexicon.morphemes(lex_id, "Test segmentation", position=6))
        self.assertIsNone(lexicon.morpheme(lex_id, "Test segmentation", 6))

    def test_overlapping_morphemes(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4)
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 6)

        self.assertEqual(2, len(lexicon.morphemes(lex_id, "Test segmentation", position=0)))
        self.assertEqual(2, len(lexicon.morphemes(lex_id, "Test segmentation", position=3)))
        self.assertEqual(1, len(lexicon.morphemes(lex_id, "Test segmentation", position=4)))
        self.assertEqual(1, len(lexicon.morphemes(lex_id, "Test segmentation", position=5)))
        self.assertEqual(0, len(lexicon.morphemes(lex_id, "Test segmentation", position=6)))

        self.assertIn(lexicon.morpheme(lex_id, "Test segmentation", 0),
                      lexicon.morphemes(lex_id, "Test segmentation", position=0))

    def test_simple_seg(self):
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4)
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 6)

        self.assertEqual(["exam", "pl", "e"], lexicon._simple_seg(lex_id, "Test segmentation"))

        # Test opposite order of addition as well.
        lexicon = SegLex()
        lex_id = lexicon.add_lexeme("example", "example", "NOUN")
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 6)
        lexicon.add_contiguous_morpheme(lex_id, "Test segmentation", 0, 4)

        self.assertEqual(["exam", "pl", "e"], lexicon._simple_seg(lex_id, "Test segmentation"))
