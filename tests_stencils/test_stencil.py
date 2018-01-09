import unittest

from stencil import Mask
from stencil import SOLID, PUNCHED
from stencil import Stencil


class TestStencil(unittest.TestCase):

    def test_instance(self):
        self.assertIsInstance(Stencil(), Stencil)


if __name__ == '__main__':
    unittest.main()
