"""General string parsing and manipulation functions"""

import random
import operator


def chunk(inp: str, chunk_size: int) -> map:
    """Split a long string into pieces of size=chunk_size

    :param inp: Thing to be chunked
    :param chunk_size: Size of each chunk
    :return: map object that is an iterable of strings
             Attention: the last incomplete chunk is dropped (not included)

    >>> tuple(chunk('abcdefghij', 2))
    ('ab', 'cd', 'ef', 'gh', 'ij')

    >>> tuple(chunk('abcdefghij', 3))
    ('abc', 'def', 'ghi')
    """
    return map("".join, zip(*(inp[i::chunk_size] for i in range(chunk_size))))


def shuffle(inp: str, seed=None) -> str:
    """Randomly shuffle a string.

    :param inp: String to shuffle
    :param seed: random seed passed to random
    :return: str, a new string consisting of inp randomly shuffled

    >>> shuffle('abcdefghij', seed=3.1415)
    'gdjhfcebia'
    """
    random.seed(seed)
    seq = list(inp)
    random.shuffle(seq)
    return "".join(seq)


def apply_mask(
    inp: str = "",
    mask: str = "",
    char: str = " ",
    substitute_char: str = None,
    invert: bool = False,
) -> str:
    """Mask a string

    :param inp: str, the string to apply the mask to
    :param mask: str, the string used as mask on inp
    :param char: Character in `mask` that does the masking - default is ` `
    :param substitute_char: What to replace `char` with.  If `None`           # replace_with?
                            uses characters from `msk`
    :param invert: We could invert the mask
    :return: str

    >>> apply_mask(inp='abcdefghij', mask='-----     ', invert=True)
    'abcde     '

    >>> apply_mask(inp='abcdefghij', mask='-----     ', invert=False)
    '-----fghij'
    """
    try:
        assert len(inp) == len(mask)
    except AssertionError as a:
        raise a
        # ParameterLengthDoNotMatchError
        # or could return inp if msk size does not match
    op = operator.ne if invert else operator.eq
    return "".join(
        c if op(m, char) else (substitute_char or m) for c, m in zip(inp, mask)
    )


if __name__ == "__main__":

    import doctest

    print(doctest.testmod())
