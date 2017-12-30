"""General string parsing and manipulation functions"""
import random
import operator


def chunk(s: str, n: int) -> map:
    """Split a long string into `n` size pieces

    :param s: Thing to be chunked
    :param n: Size of each chunk
    :return: map object that is an iterable of strings

    >>> from str2d import utils
    ... tuple(utils.chunk('abcdefghij', 2))
    ('ab', 'cd', 'ef', 'gh', 'ij')
    """
    return map(''.join, zip(*(s[i::n] for i in range(n))))


def shuffle(s: str, seed=None) -> str:
    """Randomly shuffle a string.

    :param s: String to shuffle
    :param seed: random seed passed to random
    :return: str

    >>> from str2d import utils
    ... utils.shuffle('abcdefghij', seed=3.1415)
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

    >>> from str2d import utils
    ... utils.mask('abcdefghij', '-' * 5 + ' ' * 5, invert=True)
    'abcde     '

    >>> from str2d import utils
    ... utils.mask('abcdefghij', '-' * 5 + ' ' * 5, invert=False)
    '-----fghij'
    """

    op = operator.ne if invert else operator.eq
    return ''.join(
        s if op(m, char) else (replace or m)
        for s, m in zip(inp, msk)
    )
