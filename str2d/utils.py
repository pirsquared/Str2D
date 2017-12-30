"""General string parsing and manipulation functions"""
import random
import operator


def chunk(s: str, chunk_size: int) -> map:
    """Split a long string into pieces of size=chunk_size

    :param s: Thing to be chunked
    :param chunk_size: Size of each chunk
    :return: map object that is an iterable of strings
             Attention: the last incomplete chunk is dropped (not included)

    >>> tuple(chunk('abcdefghij', 2))
    ('ab', 'cd', 'ef', 'gh', 'ij')

    >>> tuple(chunk('abcdefghij', 3))
    ('abc', 'def', 'ghi')
    """
    return map(''.join, zip(*(s[i::chunk_size] for i in range(chunk_size))))


def shuffle(s: str, seed=None) -> str:
    """Randomly shuffle a string.

    :param s: String to shuffle
    :param seed: random seed passed to random
    :return: str

    >>> shuffle('abcdefghij', seed=3.1415)
    'gdjhfcebia'
    """
    random.seed(seed)
    l = list(s)
    random.shuffle(l)
    return ''.join(l)


def mask(inp: str, msk: str, char: str = ' ',
         replace: str = None, invert: bool = False) -> str:
    """Mask a string

    :param inp: String to mask
    :param msk: String to use as mask
    :param char: Character within `msk` that will do the masking
    :param replace: What to replace `char` with.  If `None` will use characters
        from `msk`
    :param invert: We could invert the mask
    :return: str

    >>> mask('abcdefghij', '-' * 5 + ' ' * 5, invert=True)
    'abcde     '

    >>> mask('abcdefghij', '-' * 5 + ' ' * 5, invert=False)
    '-----fghij'
    """

    op = operator.ne if invert else operator.eq
    return ''.join(
        s if op(m, char) else (replace or m)
        for s, m in zip(inp, msk)
    )


if __name__ == '__main__':

    import doctest
    doctest.testmod()
