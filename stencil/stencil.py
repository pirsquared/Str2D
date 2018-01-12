
from typing import Sequence   #ClassVar, Iterable, List, Sequence, Tuple, Union

from stencil.mask import Mask


class Stencil:
    """a rectangular "cover" on a grid surface that is "perforated" at some
    positions to let the elements through, while the other positions are
    blocked and conceal the elements.
    an aggregate of `Mask` of same length, defining a rectangle of
    SOLID and PUNCHED positions
    """
    def __init__(self):
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.masks = None        # array of blanks [Mask(size=num_cols) for _ in range(num_rows)]

    def __str__(self):
        return '\n'.join([str(mask) for mask in self.masks])

    @staticmethod
    def from_masks(masks: Sequence['Mask']):
        """factory method to make a Stencil from a Sequence of Mask

        :param masks: a Sequence of Mask
        :return: a new Stencil object composed of the provided Sequence of Mask
        """
        assert masks is not None, 'please provide a sequence of Mask, not None'
        assert len(masks) > 0, 'please provide a non empty sequence of Mask'
        assert all(masks[0].size == m.size for m in masks), 'all masks must be of the same size'
        stencil = Stencil()
        stencil.num_rows = len(masks)
        stencil.num_cols = masks[0].size
        stencil.masks = masks
        return stencil

    def apply_to(self, sequence: Sequence[Sequence],
                 substitute: str='-') -> Sequence[Sequence]:
        """applies the Stencil to the sequence of sequences provided, and return
        a new sequence of sequences of same dimensions where only the elements
        located at punched positions on each masks are visible;
        the other elements are concealed with the Masks self.solid_repr by default,
        or a substitute if one is provided

        :param sequence: a sequence of sequences to be masked
        :param substitute: a character to be substituted to the SOLID
                           positions in each mask
        :return: a new sequence of sequences where the elements marked SOLID on
                 each mask have been concealed by the substitute character.
        """

