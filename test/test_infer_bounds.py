import unittest

from useg.infer_bounds import infer_bounds

class TestInferBounds(unittest.TestCase):
    def test_simple(self):
        self.assertEqual([0, 1], infer_bounds(["a"], "a"))
        self.assertEqual([0, 2], infer_bounds(["aa"], "aa"))
        self.assertEqual([0, 2], infer_bounds(["ab"], "ab"))

    def test_multiple_matching(self):
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "bb"], "aabb"))
        self.assertEqual([0, 2, 4], infer_bounds(["ab", "ab"], "abab"))
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "ab"], "aaab"))
        self.assertEqual([0, 2, 4], infer_bounds(["ab", "aa"], "abaa"))
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "aa"], "aaaa"))

    def test_multiple_nonmatching(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "def"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["acc", "def"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["acc", "dcc"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "cef"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["abd", "def"], "abcdef"))

        self.assertEqual([0, 3, 6], infer_bounds(["abcx", "def"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "xdef"], "abcdef"))
        self.assertEqual([0, 3, 6], infer_bounds(["abcx", "xdef"], "abcdef"))

    def test_longer_prefix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["xabc", "def"], "abcdef"))

    def test_shorter_prefix(self):
        self.assertEqual([1, 4, 7], infer_bounds(["abc", "def"], "xabcdef"))

    def test_longer_suffix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "defx"], "abcdef"))

    def test_shorter_suffix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "def"], "abcdefx"))
