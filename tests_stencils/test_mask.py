import unittest

from stencil import Mask
from stencil import SOLID, PUNCHED


class TestMask(unittest.TestCase):
    """tests for the internals of Mask"""

    def setUp(self):
        self.blank_that_remains_blank = Mask(size=12)
        self.blank_ready_to_punch = Mask(size=12)

        self.mask1__0_1_0 = Mask(size=3)
        self.mask1__0_1_0._punch_mask([False, True, False])
        self.mask2__0_1_0 = Mask(size=3)
        self.mask2__0_1_0._punch_mask([False, True, False])

        # all instances of Mask created below (within setUp() require
        # protected access to inject values and avoid using the methods
        # of Mask or the Mask factories to build
        self.all_punched_mask = Mask(size=12)
        self.all_punched_mask._mask = tuple(PUNCHED for _ in range(12))

        # the two following instances are 'negative' of each other and
        # can be compared via the invert() method
        self.odd_are_punched = Mask(size=12)
        self.odd_are_punched._mask = tuple(SOLID if pos % 2 else PUNCHED for pos in range(12))
        self.even_are_punched = Mask(size=12)
        self.even_are_punched._mask = tuple(PUNCHED if pos % 2 else SOLID for pos in range(12))

    # -------------- TEST INSTANCE and INIT ---------------------------------
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
    # -------------- END TEST INSTANCE and INIT -----------------------------

    # -------------- TEST EQUALITY ---------------------------------
    def test_equality_blanks_of_same_size_are_equal(self):
        self.assertTrue(Mask(size=12) == self.blank_that_remains_blank)

    def test_equality_blanks_of_different_size_are_not_equal(self):
        self.assertFalse(Mask(size=10) == self.blank_that_remains_blank)

    def test_equality_masks_with_same_punched_pattern_are_equal(self):
        self.assertTrue(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_A(self):
        """if their self.punched_repr was changed"""
        self.mask1__0_1_0.punched_repr = '*'
        self.assertFalse(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_B(self):
        """if their self.solid_repr was changed"""
        self.mask1__0_1_0.solid_repr = 'w'
        self.assertFalse(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_C(self):
        """if their Mask.punched_repr was changed between instance creation"""
        Mask.punched_repr = '*'
        mask_case_c__0_1_0 = Mask(size=3)
        mask_case_c__0_1_0._punch_mask([False, True, False])
        self.assertFalse(self.mask1__0_1_0 == mask_case_c__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_D(self):
        """if their Mask.solid_repr was changed between instance creation"""
        Mask.solid_repr = '*'
        mask_case_d__0_1_0 = Mask(size=3)
        mask_case_d__0_1_0._punch_mask([False, True, False])
        self.assertFalse(self.mask1__0_1_0 == mask_case_d__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_in_case_E(self):
        """if Mask.punched_repr was changed before the two instance compared are created"""
        Mask.punched_repr = '*'
        mask_case_e1__0_1_0 = Mask(size=3)
        mask_case_e1__0_1_0._punch_mask([False, True, False])
        mask_case_e2__0_1_0 = Mask(size=3)
        mask_case_e2__0_1_0._punch_mask([False, True, False])
        self.assertTrue(mask_case_e1__0_1_0 == mask_case_e2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_in_case_F(self):
        """if Mask.solid_repr was changed before the two instance compared are created"""
        Mask.solid_repr = '*'
        mask_case_f1__0_1_0 = Mask(size=3)
        mask_case_f1__0_1_0._punch_mask([False, True, False])
        mask_case_f2__0_1_0 = Mask(size=3)
        mask_case_f2__0_1_0._punch_mask([False, True, False])
        self.assertTrue(mask_case_f1__0_1_0 == mask_case_f2__0_1_0)

    # not tested: case where both solid_repr and punched_repr are changed
    # -------------- END TEST EQUALITY -----------------------------


if __name__ == '__main__':
    unittest.main()
