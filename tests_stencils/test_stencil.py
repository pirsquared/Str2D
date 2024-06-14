import unittest

from masking import Mask
from masking import SOLID, PUNCHED
from masking import Stencil


class TestStencilBase(unittest.TestCase):

    def setUp(self):
        # @TODO: use mocks for Mask?
        self.even_are_punched = Mask(size=12)
        self.even_are_punched._mask = tuple(
            SOLID if pos % 2 else PUNCHED for pos in range(12)
        )
        self.odd_are_punched = Mask(size=12)
        self.odd_are_punched._mask = tuple(
            PUNCHED if pos % 2 else SOLID for pos in range(12)
        )
        masks_eo = [
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
        ]
        self.stencil_12_12_alternate_even_odd = Stencil.from_masks(masks_eo)

        masks_oe = [
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
            self.odd_are_punched,
            self.even_are_punched,
        ]
        self.stencil_12_12_alternate_odd_even = Stencil.from_masks(masks_oe)

        self.seq_of_seq_1 = [" 0  1  2  3", " 4  5  6  7", " 8  9 10 11", "12 13 14 15"]
        assert all(len(seq) == len(self.seq_of_seq_1[0]) for seq in self.seq_of_seq_1)
        patterns = ["^^^  ^  ^  ", "  ^^^^  ^  ", "  ^  ^^^^^^", "^^^  ^  ^  "]
        masks = [Mask.from_pattern(pattern) for pattern in patterns]
        self.stencil_1 = Stencil.from_masks(masks=masks)


class TestStencil(TestStencilBase):
    # @TODO: add tests for raised AssertErrors

    def test_instance(self):
        self.assertIsInstance(Stencil(), Stencil)

    def test_from_masks(self):
        mask1__0_1_0 = Mask(size=3)
        mask1__0_1_0.from_pattern("_^_")
        stencil = Stencil.from_masks([mask1__0_1_0, mask1__0_1_0])
        self.assertIsInstance(stencil, Stencil)

    def test_str_1(self):
        expected = "^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^"
        actual = str(self.stencil_12_12_alternate_even_odd)
        self.assertEqual(actual, expected)

    def test_str_2(self):
        expected = "-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-\n-^-^-^-^-^-^\n^-^-^-^-^-^-"
        actual = str(self.stencil_12_12_alternate_odd_even)
        self.assertEqual(actual, expected)

    def test_apply_stencil_to_seqofseq(self):
        actual = self.stencil_1.apply_to(self.seq_of_seq_1)
        expected = " 0 -- -- --\n--  5 -- --\n-- -- 10 11\n12 -- -- --"
        self.assertEqual(expected, actual)

    def test_apply_stencil_to_seqofseq_w_substitute(self):
        actual = self.stencil_1.apply_to(self.seq_of_seq_1, substitute="*")
        expected = " 0 ** ** **\n**  5 ** **\n** ** 10 11\n12 ** ** **"
        self.assertEqual(expected, actual)

    def test_invert_stencil_using_apply_to(self):
        inverted_stencil_1 = self.stencil_1.invert()
        expected = "--- 1- 2- 3\n 4---- 6- 7\n 8- 9------\n---13-14-15"
        actual = inverted_stencil_1.apply_to(self.seq_of_seq_1)
        self.assertEqual(expected, actual)

    def test_invert_stencil_using_apply_to_w_substitute(self):
        inverted_stencil_1 = self.stencil_1.invert()
        expected = "### 1# 2# 3\n 4#### 6# 7\n 8# 9######\n###13#14#15"
        actual = inverted_stencil_1.apply_to(self.seq_of_seq_1, substitute="#")
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
