import unittest

from stencil import Mask
from stencil import SOLID, PUNCHED
from stencil import Stencil


class TestStencilBase(unittest.TestCase):

    def setUp(self):
        # @TODO: use mocks for Mask?
        self.even_are_punched = Mask(size=12)
        self.even_are_punched._mask = tuple(SOLID if pos % 2 else PUNCHED for pos in range(12))
        self.odd_are_punched = Mask(size=12)
        self.odd_are_punched._mask = tuple(PUNCHED if pos % 2 else SOLID for pos in range(12))
        masks_eo = [self.even_are_punched, self.odd_are_punched, self.even_are_punched, self.odd_are_punched,
                    self.even_are_punched, self.odd_are_punched, self.even_are_punched, self.odd_are_punched,
                    self.even_are_punched, self.odd_are_punched, self.even_are_punched, self.odd_are_punched,]
        self.stencil_12_12_alternate_even_odd = Stencil.from_masks(masks_eo)

        masks_oe = [self.odd_are_punched, self.even_are_punched, self.odd_are_punched, self.even_are_punched,
                    self.odd_are_punched, self.even_are_punched, self.odd_are_punched, self.even_are_punched,
                    self.odd_are_punched, self.even_are_punched, self.odd_are_punched, self.even_are_punched]
        self.stencil_12_12_alternate_odd_even = Stencil.from_masks(masks_oe)


class TestStencil(TestStencilBase):

    def test_instance(self):
        self.assertIsInstance(Stencil(), Stencil)

    def test_from_masks(self):
        mask1__0_1_0 = Mask(size=3)
        mask1__0_1_0.from_pattern('_^_')
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


if __name__ == '__main__':
    unittest.main()
