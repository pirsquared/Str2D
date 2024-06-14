from typing import ClassVar, Iterable, List, Sequence, Tuple, Union
from masking.perforation import SOLID, PUNCHED

# from perforation import SOLID, PUNCHED


class Mask:
    """a "cover" on a sequence that is "perforated" at some positions to
    let the elements through, while the other positions are blocked and
    conceal the elements.

    :class_var punched_repr: str, the character used to generically represent
                                  a PUNCHED position in a Mask
    :class_var solid_repr: str, the character used to generically represent
                                a SOLID position in a Mask
    """

    generic_punched_repr = "^"  # type: ClassVar[str]
    generic_solid_repr = "-"  # type: ClassVar[str]

    def __init__(self, size: int = 0) -> None:
        """Make a 'blank': a solid Mask of size=size without punched positions

        :param size: int, the size of the mask
        """
        assert (
            size is not None and size > 0
        ), f"a Mask must have a size > 0, the size provided was size={size}"
        self.size: int = size
        self._mask: Union[List, Tuple] = [SOLID for _ in range(self.size)]

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
        assert self.is_a_blank(), "you must use a blank, a Mask cannot be re-punched"
        assert (
            len(pattern) == self.size
        ), "you must use a pattern that matches the blank size: \
            \npattern size:{len(pattern)} != mask size:{self.size}"
        self._mask = tuple([PUNCHED if pos else SOLID for pos in pattern])

    def is_a_blank(self) -> bool:
        """return True if the Mask is a blank, False otherwise"""
        return all(elt == SOLID for elt in self._mask)

    def __str__(self) -> str:
        return "".join(
            [
                str(self.punched_repr) if pos == PUNCHED else self.solid_repr
                for pos in self._mask
            ]
        )

    def __eq__(self, other: "Mask") -> bool:
        """two masks are equal if their SOLID/PUNCHED patterns are equal
        and their punched_repr and solid_repr are equal"""
        assert other is not None and type(other) == Mask
        return (
            self.mask == other.mask
            and self.punched_repr == other.punched_repr
            and self.solid_repr == other.solid_repr
        )

    def invert(self) -> "Mask":
        """inverses the mask pattern and return a new Mask object where punched
        positions are solid and solid positions are punched
        """
        inverted_mask = Mask(size=self.size)
        inverted_mask._punch_mask(
            [True if perf.toggle() == PUNCHED else False for perf in self._mask]
        )
        return inverted_mask

    @staticmethod
    def from_pattern(pattern: Sequence = "", values_to_punch: Iterable = "^") -> "Mask":
        """Mask factory that makes and returns a new Mask object from a pattern
        of values, a sequence, that can be compared to the values in to_punch to
        determine which positions to punch, and which to retain solid

        :param pattern: a Sequence whose elements indicate where to punch and
                        where to keep solid - these elements are evaluated in
                        comparison to the ones provided in to_punch

                        if pattern is None, or of size=0, raises an
                        AssertionError

                        if pattern does not contain elements from
                        values_to_punch, it returns a blank of the size of
                        pattern

        :param values_to_punch: a collection of elements representing a
                         punching action - each position in pattern for which
                         the value is in to_punch is marked punched, all other
                         positions are marked solid.

        :return: A new Mask object representative of pattern
        """
        # ? opimization if values_to_punch is large > 64, maybe?:
        # _to_punch = set([elt for elt in values_to_punch])
        assert pattern is not None, "pattern must not be None"
        assert (
            len(pattern) > 0
        ), f"you must provide a valid pattern, the pattern provides had size={len(pattern)}"
        mask = Mask(size=len(pattern))
        mask._punch_mask([True if elt in values_to_punch else False for elt in pattern])
        return mask

    @staticmethod
    def from_indices(size: int = 0, indices_to_punch: Iterable[int] = set()) -> "Mask":
        """Mask factory that makes a new Mask object where the positions to
        punch are at the given indices.

        # similar to np.where()

        :param size: int, the size of the mask to create
        :param indices_to_punch: the indices of the positions to punch
                                 indices can be negative values
        :return: A new Mask object where the positions to punch are at
                 the given indices
        """
        assert (
            size is not None and size > 0
        ), f"a Mask must have a size > 0, the size provided was size={size}"
        _mitp1 = max(indices_to_punch)
        assert (
            max(indices_to_punch) < size
        ), f"some of the positive indices provided are too large: {_mitp1} >= {size}"
        _mitp2 = min(indices_to_punch)
        assert (
            min(indices_to_punch) >= -size
        ), f"some of the negative indices provided are too small: {_mitp2} < -{size}"
        mask = Mask(size=size)
        pattern = [False for _ in range(size)]
        for pos_to_punch in indices_to_punch:
            pattern[pos_to_punch] = True
        mask._punch_mask(pattern=pattern)
        return mask

    def apply_to(self, sequence: Sequence, substitute: str = "-") -> Sequence:
        """applies the mask to the sequence provided, and return a new
        sequence of same length where only the elements located at punched
        positions on the mask are visible; the other elements are concealed
        with self.solid_repr by default, or a substitute if one is provided

        :param sequence: a sequence to be masked
        :param substitute: a character to be substituted to the SOLID
                           positions in the mask
        :return: a new sequence where the elements marked SOLID on the mask
                 have been concealed by the substitute character.
        """
        assert (
            len(sequence) == self.size
        ), f"the Mask must be the same size as the sequence to apply it to: \
             \nlen(sequence): {len(sequence)} != mask size: {self.size}"
        if substitute == "":
            substitute = self.solid_repr
        return "".join(
            [
                str(elt) if mask_value is PUNCHED else substitute
                for elt, mask_value in zip(sequence, self._mask)
            ]
        )


if __name__ == "__main__":
    pass

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
