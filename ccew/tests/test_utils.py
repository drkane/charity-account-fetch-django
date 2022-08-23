from unittest import TestCase

from ccew.utils import list_to_string, regex_search, to_titlecase


class TestUtils(TestCase):
    def test_regex_search(self):
        self.assertTrue(regex_search("abc", r"abc"))
        self.assertFalse(regex_search("abc", r"def"))

    def test_list_to_string(self):
        cases = [
            (["a"], "a"),
            (["a", "b"], "a and b"),
            (["a", "b", "c"], "a, b and c"),
            (["a", "b", "c", "d"], "a, b, c and d"),
            ("Blah blah", "Blah blah"),
        ]
        for items, expected in cases:
            self.assertEqual(list_to_string(items), expected)

        self.assertEqual(
            list_to_string(["a", "b", "c", "d"], final_sep=" or "),
            "a, b, c or d",
        )
        self.assertEqual(
            list_to_string(["a", "b", "c", "d"], sep="", final_sep=""),
            "abcd",
        )
        self.assertEqual(
            list_to_string(["a", "b", "c", "d"], sep="|", final_sep="@"),
            "a|b|c@d",
        )
        self.assertIsInstance(list_to_string(set(("a", "b", "c", "d"))), str)

    def test_to_titlecase(self):
        cases = [
            ("", ""),
            ("a", "A"),
            ("a b", "A B"),
            ("a b c", "A B C"),
            ("aB", "aB"),
            ("MRS SMITH", "Mrs Smith"),
            ("MRS SMITH'S", "Mrs Smith's"),
            ("i don't know", "I Don't Know"),
            ("the 1st place", "The 1st Place"),
            ("mr smith", "Mr Smith"),
            # ("mr. smith", "Mr. Smith"),  # currently fails - should work
            ("MR O'TOOLE", "Mr O'Toole"),
            ("TOM OF TABLE CIC", "Tom of Table CIC"),
            (500, 500),
            (None, None),
        ]
        for s, expected in cases:
            self.assertEqual(to_titlecase(s), expected)

        self.assertEqual(
            to_titlecase("you're a silly billy", sentence=True),
            "You're a silly billy",
        )

        self.assertEqual(
            to_titlecase("you're a silly billy. and so are you.", sentence=True),
            "You're a silly billy. And so are you.",
        )
