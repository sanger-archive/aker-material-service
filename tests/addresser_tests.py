import unittest

from addresser import Addresser


class AddresserTests(unittest.TestCase):
    def _test_addresser(self, addresser, expected):
        self.assertEqual(len(addresser), len(expected))
        self.assertEqual(list(addresser), expected)
        for i, address in enumerate(expected):
            self.assertTrue(address in addresser)
            self.assertEqual(addresser[i], address)
            self.assertEqual(addresser.index(address), i)
        for address in '999 1:Z Z:1 99:A A:99 Z:Z nonsense :::'.split():
            self.assertFalse(address in addresser)

    def test_addresser_row_alpha(self):
        self._test_addresser(Addresser(2, 3, True, False), "A:1 A:2 A:3 B:1 B:2 B:3".split())

    def test_addresser_col_alpha(self):
        self._test_addresser(Addresser(2, 3, False, True), "1:A 1:B 1:C 2:A 2:B 2:C".split())

    def test_addresser_both_alpha(self):
        self._test_addresser(Addresser(2, 3, True, True), "A:A A:B A:C B:A B:B B:C".split())

    def test_addresser_numeric(self):
        self._test_addresser(Addresser(2, 3, False, False), map(str, xrange(1, 7)))
