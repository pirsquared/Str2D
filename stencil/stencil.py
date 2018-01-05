"""
stencil.py

a module to produce Stencils and Masks that selectively conceal or reveal
elements of a sequence.
More of a discrete Jacquard than a continuous stencil, but, maybe, the noun
stencil is more universally understood.

# there is wonderful trivia and vocabulary to learn and maybe use here:
# https://en.wikipedia.org/wiki/Jacquard_loom#Principles_of_operation
"""


from enum import Enum
from typing import ClassVar, Iterable, List, Sequence, Tuple, Union


class Perforation(Enum):
    """represents the state of a position in a `Mask`, `SOLID` or `PUNCHED`
    """
    SOLID = 0
    PUNCHED = 1

    def toggle(self) -> 'Perforation':
        """returns PUNCHED if SOLID, SOLID if PUNCHED"""
        return (Perforation.PUNCHED, Perforation.SOLID)[self.value]


SOLID = Perforation.SOLID
PUNCHED = Perforation.PUNCHED


class Crib:
    """a superposition of several `Stencil`, where the perforated positions
    remain perforated if all `Stencil` are perforated at that position, and
    blocked otherwise
    (A la "breaking the Enigma" kind of Crib)

    # this could maybe be a function or method `make_crib(list of Stencil)`,
    # returning an aggregate Stencil?

    # Note (that probably takes us far out of scope):
    # Stencils forming a Crib could be moved/perturbated, to discover a
    # pattern?
    # the Masks forming a Stencil could also be slided?
    """


class Stencil:
    """a "cover" on a grid surface that is "perforated" at some positions to
    let the elements through, while the other positions are blocked and
    conceal the elements.
    an aggregate of `Mask`
    """


class Mask:
    """a "cover" on a sequence that is "perforated" at some positions to
    let the elements through, while the other positions are blocked and
    conceal the elements.

    :class_var punched_repr: str, the character used to generically represent
                                  a PUNCHED position in a Mask
    :class_var solid_repr: str, the character used to generically represent
                                a SOLID position in a Mask
    """

    # for fault of a better name: calling these class variables punched_repr and
    # solid_repr created masking issues with mypy as follows:
    # stencil.py:79: error: Cannot assign to class variable "punched_repr" via instance
    # stencil.py:80: error: Cannot assign to class variable "solid_repr" via instance
    # @TODO: dicsuss this design issue with Sean
    generic_punched_repr = '^'   # type: ClassVar[str]
    generic_solid_repr = '-'     # type: ClassVar[str]

    def __init__(self, size: int=None) -> None:
        """Make a 'blank': a solid Mask of size=size without punched positions

        :param size: int, the size of the mask
        """
        assert size is not None and size > 0, "a Mask must have a size > 0"
        self.size: int = size
        self._mask: Union[List, Tuple] = [SOLID for _ in range(self.size)]
        # the following allows to maintain a degree of immutability for
        # instances of Mask even if class variables are modified at some point
        # this should maybe be a named tuple to guarantee immutability
        self.punched_repr: str = Mask.generic_punched_repr
        self.solid_repr: str = Mask.generic_solid_repr

    @property
    def mask(self) -> Union[List, Tuple]:
        return self._mask

    def _punch_mask(self, pattern: Sequence) -> None:
        """Punches a blank Mask at the positions marked True in pattern.

        This can only be done once.
        This method has side effects: it modifies self._mask
        :param pattern: a sequence of boolean where
                        True represents the sites to be punched,
                        and False the sites to remain solid
        """
        assert self.is_a_blank(), \
            "you must use a blank, a Mask cannot be re-punched"
        assert len(pattern) == self.size, \
            "you must use a pattern that matches the blank size"
        self._mask = tuple([PUNCHED if pos
                            else SOLID for pos in pattern])

    def is_a_blank(self) -> bool:
        """return True if the Mask is a blank, False otherwise
        """
        return all(elt == SOLID for elt in self._mask)

    def __str__(self) -> str:
        return ''.join([str(self.punched_repr) if pos == PUNCHED
                        else self.solid_repr for pos in self._mask])

    def __eq__(self, other) -> bool:
        """two masks are equal if their SOLID/PUNCHED patterns are equal
        and their punched_repr and solid_repr are equal"""
        return self.mask == other.mask and \
            self.punched_repr == other.punched_repr and \
            self.solid_repr == other.solid_repr

    def invert_mask(self) -> 'Mask':
        """inverses the mask pattern and return a new Mask object where punched
        positions are solid and solid positions are punched
        """
        inverted_mask = Mask(size=self.size)
        inverted_mask._punch_mask([True if perf.toggle() == PUNCHED else False
                                   for perf in self._mask])
        return inverted_mask

    @staticmethod
    def from_pattern(pattern: Sequence, to_punch: Iterable= '^') -> 'Mask':
        """Mask factory that makes and returns a new Mask object from a pattern
        of values, a sequence, that can be compared to the values in to_punch to
        determine which positions to punch, and which to retain solid

        :param pattern: a Sequence whose elements indicate where to punch and
                        where to keep solid - these elements are evaluated in
                        comparison to the ones provided in to_punch
        :param to_punch: a collection of elements representing a
                         punching action - each position in pattern for which
                         the value is in to_punch is marked punched, all other
                         positions are marked solid.
        :return: A new Mask object representative of pattern
        """
        # ? opimization if to_punch is large > 64, maybe?:
        # _to_punch = set([elt for elt in to_punch])
        mask = Mask(size=len(pattern))
        mask._punch_mask([True if elt in to_punch else False for elt in pattern])
        return mask

    def apply_to(self, sequence: Sequence):
        """applies the mask to the sequence provided, and return a new
        sequence of same length where only the elements located at punched
        positions on the mask are visible; the other elements are concealed

        :param sequence: a sequence to be masked
        :return: a new sequence masked

               *** ATTENTION, not polymorphic ***
        @TODO: make polymorphic to accept other Sequence objects
        """
        return ''.join([str(elt) if mask_value is PUNCHED
                        else self.solid_repr
                        for elt, mask_value in zip(sequence, self._mask)])

    def substitute_at(self, seq, elt):
        """constructs a new sequence where the elements at marked locations
        in mask are replaced by elt
        :param seq:
        :param elt:
        :return:
        """
        # maybe also need a multi substitute where a sequence of elements to
        # be subtstituted is passed?
        raise NotImplemented

    # @staticmethod
    # def make_mask_from_iterable(inp: Iterable='', values_to_mask: Iterable='',
    #                             masking_value='^', replacement_value='-'):
    #     """makes and returns a Mask object from an iterable of True or False values
    #
    #     :param inp: a sequence of elements
    #     :param values_to_mask: Iterable, a collection of the values to mask
    #                            must be Hashable too
    #     :param masking_value: str of length=1, the character that marks the
    #                            masked positions
    #     :param replacement_value: str of length=1, the character that replaces
    #                               the original at the masked positions
    #     :return: A Mask object
    #     """
    #     _values_to_mask = set(values_to_mask)
    #     pattern = [True if c in _values_to_mask else False for c in inp]
    #     mask = Mask(punched_repr=masking_value,
    #                 solid_repr=replacement_value)
    #     mask._punch_mask(pattern)

    # @staticmethod
    # def make_from_indices(inp: Iterable='', indices_of_values_to_mask: Iterable='',
    #                             masking_value='^', replacement_value='-'):
    #     """
    #     # similar to np.where()
    #
    #     :param inp:
    #     :param indices_of_values_to_mask:
    #     :param masking_value:
    #     :param replacement_value:
    #     :return:
    #     """
    #     raise NotImplemented


def tests():
    print("test mask:")
    inp = 'the truth is out there'
    print(inp)
    mask = Mask.from_pattern('^   ^     ^  ^   ^    ')
    print(mask)
    print(mask.apply_to(inp))
    print()
    print("test inverted mask:")
    inverted_mask = mask.invert_mask()
    print(inp)
    print(inverted_mask)
    print(inverted_mask.apply_to(inp))


if __name__ == '__main__':

    tests()


    # Use A Generic Sequence
    # a = [1, 2, 3]
    # b = type(a)()
    # b
    #
    # def double(seq):
    #     t = type(seq)
    #     return t([2 * u for u in seq])
    #
    #
    # print(double({1, 2, 3}))
    # # output
    # {2, 4, 6}
    #
    # must make a special case for str?
