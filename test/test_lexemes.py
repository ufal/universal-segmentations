from io import StringIO
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

    def test_correct_props(self):
        lexicon = SegLex()
        lex_id_1 = lexicon.add_lexeme("example", "example", "NOUN")
        lex_id_2 = lexicon.add_lexeme("examples", "example", "NOUN", {"number": "pl"})

        self.assertEqual("example", lexicon.form(lex_id_1))
        self.assertEqual("example", lexicon.lemma(lex_id_1))
        self.assertEqual("NOUN", lexicon.pos(lex_id_1))
        self.assertEqual({}, lexicon.features(lex_id_1))

        self.assertEqual("examples", lexicon.form(lex_id_2))
        self.assertEqual("example", lexicon.lemma(lex_id_2))
        self.assertEqual("NOUN", lexicon.pos(lex_id_2))
        self.assertEqual({"number": "pl"}, lexicon.features(lex_id_2))

    def test_iter(self):
        lexicon = SegLex()
        lex_id_1 = lexicon.add_lexeme("example", "example", "NOUN")
        lex_id_2 = lexicon.add_lexeme("example", "example", "NOUN")
        lex_id_3 = lexicon.add_lexeme("examples", "example", "NOUN")
        lex_id_4 = lexicon.add_lexeme("counterexample", "counterexample", "NOUN")
        lex_id_5 = lexicon.add_lexeme("counterexample", "counterexample", "NOUN")
        lex_id_6 = lexicon.add_lexeme("exemplar", "exemplar", "ADJ")

        self.assertCountEqual([lex_id_1,
                               lex_id_2,
                               lex_id_3,
                               lex_id_4,
                               lex_id_5,
                               lex_id_6],
                              list(lexicon.iter_lexemes()))

        self.assertCountEqual([lex_id_1,
                               lex_id_2],
                              list(lexicon.iter_lexemes(form="example")))

        self.assertCountEqual([lex_id_1,
                               lex_id_2,
                               lex_id_3],
                              list(lexicon.iter_lexemes(lemma="example")))

        self.assertCountEqual([lex_id_4,
                               lex_id_5],
                              list(lexicon.iter_lexemes(lemma="counterexample")))

        self.assertCountEqual([lex_id_4,
                               lex_id_5],
                              list(lexicon.iter_lexemes(lemma="counterexample", pos="NOUN")))

        self.assertCountEqual([lex_id_4,
                               lex_id_5],
                              list(lexicon.iter_lexemes(form="counterexample", lemma="counterexample")))

        self.assertCountEqual([lex_id_4,
                               lex_id_5],
                              list(lexicon.iter_lexemes(form="counterexample", lemma="counterexample", pos="NOUN")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(form="counterexample", lemma="counterexample", pos="ADJ")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(form="counterexamples", lemma="counterexample", pos="NOUN")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(form="counterexample", lemma="counterexamples", pos="NOUN")))

        self.assertCountEqual([lex_id_1,
                               lex_id_2,
                               lex_id_3,
                               lex_id_4,
                               lex_id_5],
                              list(lexicon.iter_lexemes(pos="NOUN")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(form="silly")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(lemma="silly")))

        self.assertEqual([],
                         list(lexicon.iter_lexemes(pos="VERB")))

    def test_forbidden_features_annot_name(self):
        seg_lex = SegLex()
        seg_lex.add_lexeme("example", "example", "NOUN", {"annot_name": "fail"})

        io = StringIO()
        with self.assertRaises(Exception):
            seg_lex.save(io)

    def test_forbidden_features_segmentation(self):
        seg_lex = SegLex()
        seg_lex.add_lexeme("example", "example", "NOUN", {"segmentation": []})

        io = StringIO()
        with self.assertRaises(Exception):
            seg_lex.save(io)

    def test_forbidden_features_annot_name_with_seg(self):
        seg_lex = SegLex()
        lex_id = seg_lex.add_lexeme("example", "example", "NOUN", {"annot_name": "fail"})
        seg_lex.add_contiguous_morpheme(lex_id, "seg", 0, 7)

        io = StringIO()
        with self.assertRaises(Exception):
            seg_lex.save(io)

    def test_forbidden_features_segmentation_with_seg(self):
        seg_lex = SegLex()
        lex_id = seg_lex.add_lexeme("example", "example", "NOUN", {"segmentation": []})
        seg_lex.add_contiguous_morpheme(lex_id, "seg", 0, 7)

        io = StringIO()
        with self.assertRaises(Exception):
            seg_lex.save(io)
