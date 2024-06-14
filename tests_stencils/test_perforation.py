from enum import Enum
import unittest

from masking import Perforation
from masking import SOLID, PUNCHED


class TestPerforation(unittest.TestCase):
    """tests for enum Perforation"""

    def test_is_instance_of_Enum(self):
        self.assertIsInstance(Perforation.SOLID, Enum)
        self.assertIsInstance(Perforation.PUNCHED, Enum)

    def test_is_instance_of_Perforation(self):
        self.assertIsInstance(Perforation.SOLID, Perforation)
        self.assertIsInstance(Perforation.PUNCHED, Perforation)

    def test_Perforation_singletons_values(self):
        self.assertEqual(Perforation.SOLID.value, 0)
        self.assertEqual(Perforation.PUNCHED.value, 1)

    def test_perforation_toggle_returned_object(self):
        state = Perforation.SOLID
        new_state = state.toggle()
        self.assertIs(new_state, Perforation.PUNCHED)
        new_state_2 = new_state.toggle()
        self.assertIs(new_state_2, Perforation.SOLID)
        new_state_3 = new_state_2.toggle()
        self.assertIs(new_state_3, Perforation.PUNCHED)

    def test_perforation_toggle_no_side_effect(self):
        state = Perforation.SOLID
        new_state = state.toggle()
        self.assertIsNot(state, Perforation.PUNCHED)
        self.assertIs(state, Perforation.SOLID)

    def test_monkey_patch_Perforation_singletons(self):
        """test the monkey patching 'for convenience' of SOLID and PUNCHED"""
        self.assertIs(Perforation.SOLID, SOLID)
        self.assertIs(Perforation.PUNCHED, PUNCHED)


if __name__ == "__main__":
    unittest.main()
