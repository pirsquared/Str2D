import unittest

from stencil import Mask
from stencil import SOLID, PUNCHED


class TestMask(unittest.TestCase):

    def setUp(self):
        self.blank_that_remains_blank = Mask(size=12)
        self.blank_ready_to_punch = Mask(size=12)

        self.all_punched_mask = Mask(size=12)
        # protected access to inject values and make an instance outside of factory
        self.all_punched_mask._mask = tuple(PUNCHED for _ in range(12))

    def test_blank_mask_instance(self):
        self.assertIsInstance(self.blank_that_remains_blank, Mask)

    def test_blank_is_a_blank(self):
        """test is_a_blank with a blank"""
        self.assertTrue(self.blank_that_remains_blank.is_a_blank())
        self.assertTrue(all(pos is SOLID for pos in self.blank_that_remains_blank.mask))

    def test_mask_is_not_a_blank(self):
        """test is_a_blank with a mask whose values were injected"""
        self.assertFalse(self.all_punched_mask.is_a_blank())
        self.assertTrue(any(pos is not SOLID for pos in self.all_punched_mask.mask))

    def test_all_punched_mask_mask(self):
        pass


if __name__ == '__main__':
    unittest.main()
