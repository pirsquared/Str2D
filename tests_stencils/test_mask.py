import unittest

from masking import Mask
from masking import SOLID, PUNCHED


# keep track of original defaults to reset them in tearDown()
_STANDARD_PUNCHED_REPR = Mask.generic_punched_repr
_STANDARD_SOLID_REPR = Mask.generic_solid_repr


class TestMaskBase(unittest.TestCase):
    """Shared setUp() and tearDown() for Mask tests"""

    def setUp(self):
        self.blank_that_remains_blank = Mask(size=12)
        self.blank_ready_to_punch = Mask(size=12)

        self.mask1__0_1_0 = Mask(size=3)
        self.mask1__0_1_0._punch_mask([False, True, False])
        self.mask2__0_1_0 = Mask(size=3)
        self.mask2__0_1_0._punch_mask([False, True, False])

        # all instances of Mask created below, but within setUp() require
        # protected access to inject values and avoid using the methods
        # of Mask or the Mask factories to build
        self.all_punched_mask = Mask(size=12)
        self.all_punched_mask._mask = tuple(PUNCHED for _ in range(12))

        # the two following instances are 'negative' of each other and
        # can be compared via the invert() method
        self.even_are_punched = Mask(size=12)
        self.even_are_punched._mask = tuple(
            SOLID if pos % 2 else PUNCHED for pos in range(12)
        )
        self.odd_are_punched = Mask(size=12)
        self.odd_are_punched._mask = tuple(
            PUNCHED if pos % 2 else SOLID for pos in range(12)
        )

    def tearDown(self):

        # a hacky fix for the changes of class variable values that create problems in tests:
        Mask.generic_punched_repr = _STANDARD_PUNCHED_REPR
        Mask.generic_solid_repr = _STANDARD_SOLID_REPR


class TestMaskInternals(TestMaskBase):
    """tests for the internals of Mask"""

    # -------------- TEST INSTANCE and INIT ---------------------------------
    def test_blank_mask_instance(self):
        self.assertIsInstance(self.blank_that_remains_blank, Mask)

    def test_mask_with_size_is_None(self):
        with self.assertRaises(AssertionError) as context:
            none_mask = Mask(size=None)

    def test_mask_with_size_is_default_0(self):
        with self.assertRaises(AssertionError) as context:
            none_mask = Mask()

    def test_mask_with_size_is_0(self):
        with self.assertRaises(AssertionError) as context:
            none_mask = Mask(size=0)

    def test_blank_is_a_blank(self):
        """test is_a_blank() with a blank"""
        self.assertTrue(self.blank_that_remains_blank.is_a_blank())
        self.assertTrue(all(pos is SOLID for pos in self.blank_that_remains_blank.mask))

    def test_mask_is_not_a_blank(self):
        """test is_a_blank() with a mask whose values were injected"""
        self.assertFalse(self.all_punched_mask.is_a_blank())
        self.assertTrue(any(pos is not SOLID for pos in self.all_punched_mask.mask))

    # -------------- END TEST INSTANCE and INIT -----------------------------

    # -------------- TEST @property mask ---------------------------------
    def test_property_mask(self):
        self.assertEqual(self.mask1__0_1_0.mask, (SOLID, PUNCHED, SOLID))

    # -------------- TEST @property mask ---------------------------------

    # -------------- TEST EQUALITY AND INEQUALITY ---------------------------------
    def test_mask_equal_None(self):
        with self.assertRaises(AssertionError) as context:
            # Attention: must use '==' for this test, do not refactor to 'is None'
            a = self.mask1__0_1_0 == None

    def test_mask_equal_some_other_object(self):
        with self.assertRaises(AssertionError) as context:
            a = self.mask1__0_1_0 == [1, 2, 3]

    def test_equality_blanks_of_same_size_are_equal(self):
        self.assertTrue(Mask(size=12) == self.blank_that_remains_blank)

    def test_equality_blanks_of_different_size_are_not_equal(self):
        self.assertFalse(Mask(size=10) == self.blank_that_remains_blank)

    def test_equality_masks_with_same_punched_pattern_are_equal(self):
        self.assertTrue(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_A(self):
        """case_A: if their self.punched_repr was changed"""
        self.mask1__0_1_0.punched_repr = "*"
        self.assertFalse(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_B(self):
        """case_B: if their self.solid_repr was changed"""
        self.mask1__0_1_0.solid_repr = "w"
        self.assertFalse(self.mask1__0_1_0 == self.mask2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_C(self):
        """case_C: if their Mask.generic_punched_repr was changed between instance creation"""
        Mask.generic_punched_repr = "*"
        mask_case_c__0_1_0 = Mask(size=3)
        mask_case_c__0_1_0._punch_mask([False, True, False])
        self.assertFalse(self.mask1__0_1_0 == mask_case_c__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_but_not_case_D(self):
        """case_D: if their Mask.generic_solid_repr was changed between instance creation"""
        Mask.generic_solid_repr = "*"
        mask_case_d__0_1_0 = Mask(size=3)
        mask_case_d__0_1_0._punch_mask([False, True, False])
        self.assertFalse(self.mask1__0_1_0 == mask_case_d__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_in_case_E(self):
        """case_E: if Mask.generic_punched_repr was changed before the two instance compared are created"""
        Mask.generic_punched_repr = "*"
        mask_case_e1__0_1_0 = Mask(size=3)
        mask_case_e1__0_1_0._punch_mask([False, True, False])
        mask_case_e2__0_1_0 = Mask(size=3)
        mask_case_e2__0_1_0._punch_mask([False, True, False])
        self.assertTrue(mask_case_e1__0_1_0 == mask_case_e2__0_1_0)

    def test_equality_masks_with_same_punched_pattern_are_equal_in_case_F(self):
        """case_F: if Mask.generic_solid_repr was changed before the two instance compared are created"""
        Mask.generic_solid_repr = "*"
        mask_case_f1__0_1_0 = Mask(size=3)
        mask_case_f1__0_1_0._punch_mask([False, True, False])
        mask_case_f2__0_1_0 = Mask(size=3)
        mask_case_f2__0_1_0._punch_mask([False, True, False])
        self.assertTrue(mask_case_f1__0_1_0 == mask_case_f2__0_1_0)

    def test_inequality_blanks_of_same_size_are_equal(self):
        self.assertFalse(Mask(size=12) != self.blank_that_remains_blank)

    def test_inequality_blanks_of_different_size_are_not_equal(self):
        self.assertTrue(Mask(size=10) != self.blank_that_remains_blank)

    def test_inequality_masks_with_same_punched_pattern_are_equal(self):
        self.assertFalse(self.mask1__0_1_0 != self.mask2__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_but_not_case_A(self):
        """case_A: if their self.punched_repr was changed"""
        self.mask1__0_1_0.punched_repr = "*"
        self.assertTrue(self.mask1__0_1_0 != self.mask2__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_but_not_case_B(self):
        """case_B: if their self.solid_repr was changed"""
        self.mask1__0_1_0.solid_repr = "w"
        self.assertTrue(self.mask1__0_1_0 != self.mask2__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_but_not_case_C(self):
        """case_C: if their Mask.generic_punched_repr was changed between instance creation"""
        Mask.generic_punched_repr = "*"
        mask_case_c__0_1_0 = Mask(size=3)
        mask_case_c__0_1_0._punch_mask([False, True, False])
        self.assertTrue(self.mask1__0_1_0 != mask_case_c__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_but_not_case_D(self):
        """case_D: if their Mask.generic_solid_repr was changed between instance creation"""
        Mask.generic_solid_repr = "*"
        mask_case_d__0_1_0 = Mask(size=3)
        mask_case_d__0_1_0._punch_mask([False, True, False])
        self.assertTrue(self.mask1__0_1_0 != mask_case_d__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_in_case_E(self):
        """case_E: if Mask.generic_punched_repr was changed before the two instance compared are created"""
        Mask.generic_punched_repr = "*"
        mask_case_e1__0_1_0 = Mask(size=3)
        mask_case_e1__0_1_0._punch_mask([False, True, False])
        mask_case_e2__0_1_0 = Mask(size=3)
        mask_case_e2__0_1_0._punch_mask([False, True, False])
        self.assertFalse(mask_case_e1__0_1_0 != mask_case_e2__0_1_0)

    def test_inequality_masks_with_same_punched_pattern_are_equal_in_case_F(self):
        """case_F: if Mask.generic_solid_repr was changed before the two instance compared are created"""
        Mask.generic_solid_repr = "*"
        mask_case_f1__0_1_0 = Mask(size=3)
        mask_case_f1__0_1_0._punch_mask([False, True, False])
        mask_case_f2__0_1_0 = Mask(size=3)
        mask_case_f2__0_1_0._punch_mask([False, True, False])
        self.assertFalse(mask_case_f1__0_1_0 != mask_case_f2__0_1_0)

    # -------------- END TEST EQUALITY AND INEQUALITY -----------------------------

    # -------------- TEST _punch_mask - not unit test, it accesses the internals ------
    def test_punch_mask_all_through(self):
        """not a unit test --> it accesses the internals"""
        self.blank_ready_to_punch._punch_mask(
            [True for _ in range(self.blank_ready_to_punch.size)]
        )
        self.assertEqual(self.all_punched_mask, self.blank_ready_to_punch)

    # -------------- END TEST _punch_mask ---------------------------------------------

    # -------------- TEST __str__() ---------------------------------
    def test_str_all_solid(self):
        expected = "------------"
        self.assertEqual(expected, str(self.blank_ready_to_punch))

    def test_str_all_punched(self):
        expected = "^^^^^^^^^^^^"
        self.assertEqual(expected, str(self.all_punched_mask))

    def test_str_odd_punched(self):
        expected = "-^-^-^-^-^-^"
        self.assertEqual(expected, str(self.odd_are_punched))

    def test_str_even_punched(self):
        expected = "^-^-^-^-^-^-"
        self.assertEqual(expected, str(self.even_are_punched))

    def test_str_when_Mask_generic_solid_repr_is_changed(self):
        """Mask.generic_solid_repr is changed to '*'"""
        Mask.generic_solid_repr = "*"
        mask_1_0_1 = Mask.from_pattern("^-^")
        expected = "^*^"
        self.assertEqual(expected, str(mask_1_0_1))

    def test_str_when_Mask_generic_punched_repr_is_changed(self):
        """Mask.generic_punched_repr is changed to 'w'"""
        Mask.generic_punched_repr = "w"
        mask_1_0_1 = Mask.from_pattern("^-^")
        expected = "w-w"
        self.assertEqual(expected, str(mask_1_0_1))

    def test_str_when_Mask_generic_solid_repr_is_changed_and_Mask_generic_punched_repr_is_changed(
        self,
    ):
        """Mask.generic_solid_repr is changed to '*' and Mask.generic_punched_repr is changed to 'w'"""
        Mask.generic_solid_repr = "*"
        Mask.generic_punched_repr = "w"
        mask_1_0_1 = Mask.from_pattern("^-^")
        expected = "w*w"
        self.assertEqual(expected, str(mask_1_0_1))

    # -------------- END TEST __str__() -----------------------------


class TestMaskUsage(TestMaskBase):
    """tests for the internals of Mask"""

    # -------------- TEST invert -------------------------------------------------
    def test_invert_does_not_mutate_original_mask(self):
        self.assertEqual(self.mask2__0_1_0, self.mask1__0_1_0)  # two masks equal before
        self.mask1__0_1_0.invert()
        self.assertEqual(self.mask2__0_1_0, self.mask1__0_1_0)  # still equal after

    def test_invert_full_solid(self):
        # this is also accessing the internals...
        fully_punched = self.blank_ready_to_punch.invert()
        self.assertTrue(
            fully_punched._mask
            == tuple(PUNCHED for _ in range(self.blank_ready_to_punch.size))
        )

    def test_invert_full_punched(self):
        full_solid = self.all_punched_mask.invert()
        self.assertTrue(full_solid.is_a_blank())

    def test_0101___to_1010___(self):
        self.assertEqual(self.odd_are_punched.invert(), self.even_are_punched)

    def test_1010___to_0101___(self):
        self.assertEqual(self.even_are_punched.invert(), self.odd_are_punched)

    def test_invert_and_then_revert_to_original(self):
        go = self.even_are_punched.invert()
        back = go.invert()
        self.assertEqual(back, self.even_are_punched)

    # -------------- END TEST invert ---------------------------------------------

    # -------------- TEST MASK FACTORY from_pattern() ----------------------------
    def test_make_mask_from_pattern_pattern_is_None(self):
        with self.assertRaises(AssertionError) as context:
            a = Mask.from_pattern(pattern=None)

    def test_make_mask_from_pattern_pattern_is_size_0(self):
        with self.assertRaises(AssertionError) as context:
            a = Mask.from_pattern(pattern=[])

    def test_make_fully_punched(self):
        size = 12
        pattern = "^" * size
        fully_punched = Mask.from_pattern(pattern=pattern)
        self.assertTrue(fully_punched == self.all_punched_mask)

    def test_make_oddly_punched(self):
        size = 12
        pattern = "".join("^" if idx % 2 == 1 else "w" for idx in range(size))
        oddly_punched = Mask.from_pattern(pattern=pattern)
        self.assertTrue(oddly_punched == self.odd_are_punched)

    def test_make_evenly_punched(self):
        size = 12
        pattern = "".join("^" if idx % 2 == 0 else "w" for idx in range(size))
        evenly_punched = Mask.from_pattern(pattern=pattern)
        self.assertTrue(evenly_punched == self.even_are_punched)

    def test_make_evenly_punched_from_collection_of_values_to_punch(self):
        """this takes a sequence of values to punch, and assembles it in a pattern
        where locations at an even indice must be punched, and locations at odd indices
        must remain solid. It then creates a mask using this pattern, and the same
        values_to_punch provided in a diferent order to the factory"""
        size = 12
        values_to_punch_in_order = ["3", " ", "x", "?", "w", "t"]
        values_to_punch_in_disorder = set(elt for elt in ("t", "3", "x", " ", "w", "?"))
        pattern = "".join(
            values_to_punch_in_order[idx // 2] if idx % 2 == 0 else "-"
            for idx in range(size)
        )
        evenly_punched = Mask.from_pattern(
            pattern=pattern, values_to_punch=values_to_punch_in_disorder
        )
        self.assertTrue(evenly_punched == self.even_are_punched)

    # -------------- END TEST MASK FACTORY from_pattern() ------------------------

    # -------------- TEST MASK FACTORY from_indices() ----------------------------
    def test_make_mask_from_indices_size_is_None(self):
        with self.assertRaises(AssertionError) as context:
            indices_to_punch = [0, 2, 4, 6, 8, 10]
            evens = Mask.from_indices(size=None, indices_to_punch=indices_to_punch)

    def test_make_mask_from_indices_size_is_0(self):
        with self.assertRaises(AssertionError) as context:
            indices_to_punch = [0, 2, 4, 6, 8, 10]
            evens = Mask.from_indices(size=0, indices_to_punch=indices_to_punch)

    def test_make_mask_from_indices_too_large(self):
        with self.assertRaises(AssertionError) as context:
            indices_to_punch = [0, 2, 4, 14, 10]
            evens = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)

    def test_make_mask_from_indices_too_small(self):
        with self.assertRaises(AssertionError) as context:
            indices_to_punch = [-13, -10, -2]
            evens = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)
            self.assertEqual(self.even_are_punched, evens)

    def test_make_even_mask_from_indices(self):
        indices_to_punch = [0, 2, 4, 6, 8, 10]
        evens = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)
        self.assertEqual(self.even_are_punched, evens)

    def test_make_odd_mask_from_indices(self):
        indices_to_punch = [1, 3, 5, 7, 9, 11]
        odds = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)
        self.assertEqual(self.odd_are_punched, odds)

    def test_make_even_mask_from_negative_indices(self):
        indices_to_punch = [-12, -10, -8, -6, -4, -2]
        evens = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)
        self.assertEqual(self.even_are_punched, evens)

    def test_make_odd_mask_from_negative_indices(self):
        indices_to_punch = [-11, -9, -7, -5, -3, -1]
        odds = Mask.from_indices(size=12, indices_to_punch=indices_to_punch)
        self.assertEqual(self.odd_are_punched, odds)

    # -------------- END TEST MASK FACTORY from_indices() ------------------------

    # -------------- TEST apply_to() ---------------------------------------------
    def test_apply_to_sequence_of_different_size_than_mask(self):
        with self.assertRaises(AssertionError) as context:
            input_str = "all your bases are belong to us"
            unmatching_pattern = (
                "-----------------------------"  # pattern size != input_str size
            )
            dummy_expected = "-------------------------------"
            mask = Mask.from_pattern(pattern=unmatching_pattern, values_to_punch="^")
            self.assertEqual(dummy_expected, mask.apply_to(input_str))

    def test_all_solid_apply_to_str(self):
        input_str = "all your bases are belong to us"
        pattern = "-------------------------------"
        expected = "-------------------------------"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.apply_to(input_str))

    def test_mask_apply_to_str_1(self):
        input_str = "all your bases are belong to us"
        pattern = "^^^------^^^^^-----^^^^^^----^^"
        expected = "all------bases-----belong----us"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.apply_to(input_str))

    def test_all_solid_apply_to_str_with_substitute_is_empty_str(self):
        input_str = "all your bases are belong to us"
        pattern = "-------------------------------"
        expected = "-------------------------------"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(pattern, mask.apply_to(input_str, substitute=""))

    def test_mask_apply_to_str_1_with_substitute_is_empty_str(self):
        input_str = "all your bases are belong to us"
        pattern = "^^^------^^^^^-----^^^^^^----^^"
        expected = "all------bases-----belong----us"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.apply_to(input_str, substitute=""))

    def test_mask_apply_to_str_with_substitute(self):
        input_str = "all your bases are belong to us"
        pattern = "^^^------^^^^^-----^^^^^^----^^"
        expected = "all      bases     belong    us"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.apply_to(input_str, substitute=" "))

    def test_mask_invert_apply_to_str(self):
        """not quite unit test --> chaining of Mask methods"""
        input_str = "all your bases are belong to us"
        pattern = "^^^------^^^^^-----^^^^^^----^^"
        expected = "--- your ----- are ------ to --"
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.invert().apply_to(input_str))

    def test_mask_invert_apply_to_str_with_substitute(self):
        """not quite unit test --> chaining of Mask methods"""
        input_str = "all your bases are belong to us"
        pattern = "^^^------^^^^^-----^^^^^^----^^"
        expected = "    your       are        to   "
        mask = Mask.from_pattern(pattern=pattern, values_to_punch="^")
        self.assertEqual(expected, mask.invert().apply_to(input_str, substitute=" "))

    # -------------- END TEST apply_to() -----------------------------------------


if __name__ == "__main__":
    unittest.main()
