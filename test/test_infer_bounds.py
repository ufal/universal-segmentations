import unittest

from useg.infer_bounds import infer_bounds

class TestInferBounds(unittest.TestCase):
    def test_simple(self):
        self.assertEqual([0, 1], infer_bounds(["a"], "a")[0])
        self.assertEqual([0, 2], infer_bounds(["aa"], "aa")[0])
        self.assertEqual([0, 2], infer_bounds(["ab"], "ab")[0])

    def test_multiple_matching(self):
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "bb"], "aabb")[0])
        self.assertEqual([0, 2, 4], infer_bounds(["ab", "ab"], "abab")[0])
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "ab"], "aaab")[0])
        self.assertEqual([0, 2, 4], infer_bounds(["ab", "aa"], "abaa")[0])
        self.assertEqual([0, 2, 4], infer_bounds(["aa", "aa"], "aaaa")[0])

    def test_multiple_nonmatching(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "def"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["acc", "def"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["acc", "dcc"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "cef"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["abd", "def"], "abcdef")[0])

        self.assertEqual([0, 3, 6], infer_bounds(["abcx", "def"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "xdef"], "abcdef")[0])
        self.assertEqual([0, 3, 6], infer_bounds(["abcx", "xdef"], "abcdef")[0])

    def test_longer_prefix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["xabc", "def"], "abcdef")[0])

    def test_shorter_prefix(self):
        self.assertEqual([1, 4, 7], infer_bounds(["abc", "def"], "xabcdef")[0])

    def test_longer_suffix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "defx"], "abcdef")[0])

    def test_shorter_suffix(self):
        self.assertEqual([0, 3, 6], infer_bounds(["abc", "def"], "abcdefx")[0])

    def test_missing_prefix(self):
        self.assertEqual([0, 0, 3], infer_bounds(["xxx", "abc"], "abc")[0])

    def test_missing_suffix(self):
        self.assertEqual([0, 3, 3], infer_bounds(["abc", "xxx"], "abc")[0])

    def test_missing_center(self):
        self.assertEqual([0, 3, 3, 6], infer_bounds(["abc", "xxx", "def"], "abcdef")[0])
