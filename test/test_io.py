from io import StringIO
import unittest
from unittest.mock import patch, mock_open

from useg import SegLex

sample_file = """ежгурт	Ёжгурт	PROPN	ежгурт	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "nom"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}], "trans_ru": "Ёжево"}
ежгуртын	Ёжгурт	PROPN	ежгурт + ын	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "loc"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}, {"morpheme": "LOC", "span": [6, 7], "type": "suffix"}], "trans_ru": "Ёжево"}
ёжгурт	Ёжгурт	PROPN	ёжгурт	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "nom"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}], "trans_ru": "Ёжево"}
ёжгуртын	Ёжгурт	PROPN	ёжгурт + ын	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "loc"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}, {"morpheme": "LOC", "span": [6, 7], "type": "suffix"}], "trans_ru": "Ёжево"}
ёжгуртысь	Ёжгурт	PROPN	ёжгурт + ысь	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "el"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}, {"morpheme": "EL", "span": [6, 7, 8], "type": "suffix"}], "trans_ru": "Ёжево"}
ёжгуртэ	Ёжгурт	PROPN	ёжгурт + э	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "ill"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}, {"morpheme": "ILL", "span": [6], "type": "suffix"}], "trans_ru": "Ёжево"}
ёжгуртэ	Ёжгурт	PROPN	ёжгурт + э	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "nom", "1sg"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4, 5], "type": "stem"}, {"morpheme": "P.1SG", "span": [6], "type": "suffix"}], "trans_ru": "Ёжево"}
-ёжево	Ёжево	PROPN	- + ёжево	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "nom"], "segmentation": [{"morpheme": "-", "span": [0], "type": "connector"}, {"morpheme": "STEM", "span": [1, 2, 3, 4, 5], "type": "stem"}], "trans_ru": "Ёжево"}
ежево	Ёжево	PROPN	ежево	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "nom"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4], "type": "stem"}], "trans_ru": "Ёжево"}
ежевоысь	Ёжево	PROPN	ежево + ысь	{"annot_name": "Uniparser UDM", "morpho_tags": ["N", "PN", "topn", "sg", "el"], "segmentation": [{"morpheme": "STEM", "span": [0, 1, 2, 3, 4], "type": "stem"}, {"morpheme": "EL", "span": [5, 6, 7], "type": "suffix"}], "trans_ru": "Ёжево"}
"""

sample_file_lexemes = """counterexample	counterexample	NOUN		{}
counterexample	counterexample	NOUN		{}
example	exam	NOUN		{}
example	example	ADJ		{}
example	example	NOUN		{}
example	example	NOUN		{}
examples	example	NOUN		{}
exemplar	exemplar	ADJ		{}
"""

sample_file_morphemes = """counterexample	counterexample	NOUN	counter + example	{"annot_name": "annot1", "segmentation": [{"morpheme": "contra", "span": [0, 1, 2, 3, 4, 5, 6], "type": "prefix"}, {"morpheme": "example", "span": [7, 8, 9, 10, 11, 12, 13], "type": "root"}]}
counterexample	counterexample	NOUN	counter + example	{"annot_name": "annot1", "segmentation": [{"morpheme": "example", "span": [7, 8, 9, 10, 11, 12, 13], "type": "root"}]}
example	example	NOUN		{}
example	example	NOUN	ex + ample	{"annot_name": "annot1", "segmentation": [{"span": [0, 1]}, {"span": [2, 3, 4, 5, 6]}]}
example	example	NOUN	exam + ple	{"annot_name": "annot1", "segmentation": [{"span": [0, 1, 2, 3]}, {"span": [4, 5, 6]}]}
example	example	NOUN	exampl + e	{"annot_name": "annot2", "segmentation": [{"span": [0, 1, 2, 3, 4, 5]}, {"span": [6]}]}
examples	example	NOUN	example + s	{"annot_name": "annot1", "segmentation": [{"morpheme": "example", "span": [0, 1, 2, 3, 4, 5, 6], "type": "root"}, {"morpheme": "PL", "span": [7], "type": "suffix"}]}
exemplar	exemplar	ADJ	exempl + ar	{"annot_name": "annot1", "segmentation": [{"morpheme": "example", "span": [0, 1, 2, 3, 4, 5], "type": "root"}]}
"""

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

    def test_load_lexemes(self):
        # Test loading lexemes with no segmentation.
        str_io = StringIO(initial_value=sample_file_lexemes)
        seg_lex = SegLex()
        seg_lex.load(str_io)

        self.assertEqual(8, len(list(seg_lex.iter_lexemes())))
        self.assertEqual(4, len(list(seg_lex.iter_lexemes(form="example"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(form="examples"))))
        self.assertEqual(2, len(list(seg_lex.iter_lexemes(form="counterexample"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(form="exemplar"))))
        self.assertEqual(2, len(list(seg_lex.iter_lexemes(pos="ADJ"))))
        self.assertEqual(6, len(list(seg_lex.iter_lexemes(pos="NOUN"))))
        self.assertEqual(4, len(list(seg_lex.iter_lexemes(lemma="example"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(lemma="exam"))))
        self.assertEqual(2, len(list(seg_lex.iter_lexemes(lemma="counterexample"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(lemma="exemplar"))))

        for lex_id in seg_lex.iter_lexemes():
            self.assertEqual({}, seg_lex.features(lex_id))
            self.assertIn(seg_lex.pos(lex_id), {"NOUN", "ADJ"})

    def test_save_lexemes_count(self):
        # Test saving lexemes with no segmentation.
        str_io = StringIO()
        seg_lex = SegLex()

        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("examples", "example", "NOUN")
        seg_lex.add_lexeme("example", "example", "ADJ")
        seg_lex.add_lexeme("example", "exam", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("exemplar", "exemplar", "ADJ")
        seg_lex.save(str_io)

        str_io.seek(0)
        content = str_io.read()

        self.assertEqual(8, content.count("\n"))
        self.assertEqual(sample_file_lexemes, content)

    def test_load_morphemes(self):
        # Test loading lexemes with concatenative segmentation.
        # And with morpheme features.
        str_io = StringIO(initial_value=sample_file_morphemes)
        seg_lex = SegLex()
        seg_lex.load(str_io)

        self.assertEqual(7, len(list(seg_lex.iter_lexemes())))
        self.assertEqual(3, len(list(seg_lex.iter_lexemes(form="example"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(form="examples"))))
        self.assertEqual(2, len(list(seg_lex.iter_lexemes(form="counterexample"))))
        self.assertEqual(1, len(list(seg_lex.iter_lexemes(form="exemplar"))))

    def test_save_morphemes(self):
        # Test saving lexemes with concatenative segmentation.
        # And with morpheme features.
        str_io = StringIO()
        seg_lex = SegLex()

        lex_id_1 = seg_lex.add_lexeme("example", "example", "NOUN")
        lex_id_2 = seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_morphemes_from_list(lex_id_2, "annot1", ["exam", "ple"])
        lex_id_3 = seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_morphemes_from_list(lex_id_3, "annot1", ["ex", "ample"])
        seg_lex.add_morphemes_from_list(lex_id_3, "annot2", ["exampl", "e"])
        lex_id_4 = seg_lex.add_lexeme("examples", "example", "NOUN")
        seg_lex.add_contiguous_morpheme(lex_id_4, "annot1", 0, 7, {"type": "root", "morpheme": "example"})
        seg_lex.add_contiguous_morpheme(lex_id_4, "annot1", 7, 8, {"type": "suffix", "morpheme": "PL"})
        lex_id_5 = seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_contiguous_morpheme(lex_id_5, "annot1", 0, 7, {"type": "prefix", "morpheme": "contra"})
        seg_lex.add_contiguous_morpheme(lex_id_5, "annot1", 7, 14, {"type": "root", "morpheme": "example"})
        lex_id_6 = seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_contiguous_morpheme(lex_id_6, "annot1", 7, 14, {"type": "root", "morpheme": "example"})
        lex_id_7 = seg_lex.add_lexeme("exemplar", "exemplar", "ADJ")
        seg_lex.add_contiguous_morpheme(lex_id_7, "annot1", 0, 6, {"type": "root", "morpheme": "example"})
        seg_lex.save(str_io)

        str_io.seek(0)
        content = str_io.read()

        self.maxDiff = None

        self.assertEqual(8, content.count("\n"))
        self.assertEqual(sample_file_morphemes, content)

    def test_load_file_name(self):
        # Test loading from a filename.
        seg_lex = SegLex()

        open_mock = mock_open(read_data=sample_file)
        with patch("useg.seg_lex.open", open_mock, create=True):
            seg_lex.load("test-example.useg")

        open_mock.assert_called_once_with("test-example.useg", "rt", encoding="utf-8")

        handle = open_mock()
        handle.write.assert_not_called()
        handle.__iter__.assert_called_once()
        handle.close.assert_called_once()

        self.assertEqual(10, len(list(seg_lex.iter_lexemes())))

    def test_save_file_name(self):
        # Test saving to a filename.
        seg_lex = SegLex()
        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("example", "example", "NOUN")
        seg_lex.add_lexeme("examples", "example", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("counterexample", "counterexample", "NOUN")
        seg_lex.add_lexeme("exemplar", "exemplar", "ADJ")

        open_mock = mock_open()
        with patch("useg.seg_lex.open", open_mock, create=True):
            seg_lex.save("test-example.useg")

        open_mock.assert_called_once_with("test-example.useg", "wt", encoding="utf-8", newline='\n')

        handle = open_mock()
        handle.read.assert_not_called()
        handle.write.assert_called()
        handle.close.assert_called_once()

        self.assertEqual(6, handle.write.call_count)

    def test_round_trip(self):
        str_io_src = StringIO(initial_value=sample_file)
        str_io_tgt = StringIO()

        seg_lex = SegLex()
        seg_lex.load(str_io_src)
        seg_lex.save(str_io_tgt)

        str_io_tgt.seek(0)
        content = str_io_tgt.read()

        self.assertEqual(sample_file, content)
