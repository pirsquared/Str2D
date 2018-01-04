import unittest

from stencil import Mask
from stencil import SOLID, PUNCHED


class TestMask(unittest.TestCase):

    def setUp(self):
        self.blank_that_remains_blank = Mask(size=12)
        self.blank_ready_to_punch = Mask(size=12)

        self.all_punched_mask = Mask(size=12)
        # protected access to make a 'mock'
        self.all_punched_mask._mask = tuple(PUNCHED for _ in range(12))

    def test_blank_mask_instance(self):
        self.assertIsInstance(self.blank_that_remains_blank, Mask)

    def test_blank_is_a_blank(self):
        self.assertTrue(self.blank_that_remains_blank.is_a_blank())

    def test_mask_is_not_a_blank(self):
        self.assertFalse(self.all_punched_mask.is_a_blank())

    def test_all_punched_mask_mask(self):
        pass


if __name__ == '__main__':
    unittest.main()
