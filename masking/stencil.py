from typing import Sequence

from masking.mask import Mask


class Stencil:
    """a rectangular "cover" on a grid surface that is "perforated" at some
    positions to let the elements through, while the other positions are
    blocked and conceal the elements.
    an aggregate of `Mask` of same length, defining a rectangle of
    SOLID and PUNCHED positions
    """

    def __init__(self) -> None:
        self.num_rows: int = 0
        self.num_cols: int = 0
        self.masks = None
        self.size = None

    def __str__(self) -> str:
        return "\n".join([str(mask) for mask in self.masks])

    def invert(self) -> "Stencil":
        """inverses the stencil patterns and return a new Stencil object where
        all Masks are inverted
        """

        # produces the correct output, however, it does not quite produce a
        # 'clean result' on a grid -> see printed output from a main xeq
        # inverted masked elements are combined with table separators.
        # in a workflow pipeline, the mask/stencil ought to be applied on the elements
        # rather than on the string
        # I think we need to clarify and separate the use cases.

        inverted_masks = [m.invert() for m in self.masks]
        return Stencil.from_masks(masks=inverted_masks)

    @staticmethod
    def from_masks(masks: Sequence["Mask"]) -> "Stencil":
        """factory method to make a Stencil from a Sequence of Mask

        :param masks: a Sequence of Mask
        :return: a new Stencil object composed of the provided Sequence of Mask
        """
        assert masks is not None, "please provide a sequence of Mask, not None"
        assert len(masks) > 0, "please provide a non empty sequence of Mask"
        assert all(
            masks[0].size == m.size for m in masks
        ), "all masks must be of the same size"
        stencil = Stencil()
        stencil.num_rows = len(masks)
        stencil.num_cols = masks[0].size
        stencil.masks = masks
        stencil.size = len(masks)
        return stencil

    def apply_to(
        self, seq_of_seq: Sequence[Sequence], substitute: str = "-"
    ) -> Sequence[Sequence]:
        """applies the Stencil to the sequence of sequences provided, and return
        a new sequence of sequences of same dimensions where only the elements
        located at punched positions on each masks are visible;
        the other elements are concealed with the Masks self.solid_repr by default,
        or a substitute if one is provided

        :param seq_of_seq: a sequence of sequences to be masked
        :param substitute: a character to be substituted to the SOLID
                           positions in each mask
        :return: a new sequence of sequences where the elements marked SOLID on
                 each mask have been concealed by the substitute character.
        """
        assert (
            len(seq_of_seq) == self.size
        ), "the number of masks must match the number of sequences provided"
        sequences_with_stencil_applied = []
        for mask, seq in zip(self.masks, seq_of_seq):
            sequences_with_stencil_applied.append(
                mask.apply_to(seq, substitute=substitute)
            )
        return "\n".join(sequences_with_stencil_applied)


if __name__ == "__main__":

    # some printed tests to show the application of a stencil on a sequence of sequence

    print("regular:", end="\n")
    seq_of_s = [" 0  1  2  3", " 4  5  6  7", " 8  9 10 11", "12 13 14 15"]
    assert all(len(seq) == len(seq_of_s[0]) for seq in seq_of_s)
    patterns = ["^^^  ^  ^  ", "  ^^^^  ^  ", "  ^  ^^^^^^", "^^^  ^  ^  "]
    masks_1 = [Mask.from_pattern(pattern) for pattern in patterns]
    stencil_1 = Stencil.from_masks(masks=masks_1)

    result = stencil_1.apply_to(seq_of_s)
    print(result)

    print("\nsubstitute *:", end="\n")
    seq_of_s = [" 0  1  2  3", " 4  5  6  7", " 8  9 10 11", "12 13 14 15"]
    assert all(len(seq) == len(seq_of_s[0]) for seq in seq_of_s)
    patterns = ["^^^  ^  ^  ", "  ^^^^  ^  ", "  ^  ^^^^^^", "^^^  ^  ^  "]
    masks_2 = [Mask.from_pattern(pattern) for pattern in patterns]
    stencil_2 = Stencil.from_masks(masks=masks_2)

    result = stencil_2.apply_to(seq_of_s, "*")
    print(result)

    print("\nregular inverted:", end="\n")
    inverted_stencil_1 = stencil_1.invert()
    result = inverted_stencil_1.apply_to(seq_of_s)
    print(result)

    print("\nsubstitute # inverted:", end="\n")
    result = inverted_stencil_1.apply_to(seq_of_s, substitute="#")
    print(result)
