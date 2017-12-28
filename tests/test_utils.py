from str2d import utils
from functools import partial


def test_chunk():
    inp = 'abcdefghij'
    c = partial(utils.chunk, inp)
    o01 = tuple(inp)
    o02 = ('ab', 'cd', 'ef', 'gh', 'ij')
    o03 = ('abc', 'def', 'ghi')
    o05 = ('abcde', 'fghij')
    o10 = (inp,)
    assert tuple(c(1)) == o01
    assert tuple(c(2)) == o02
    assert tuple(c(3)) == o03
    assert tuple(c(5)) == o05
    assert tuple(c(10)) == o10


def test_shuffle():
    assert utils.shuffle('abcdefghij', seed=3.1415) == 'gdjhfcebia'


def test_mask():
    inp = 'abcd'
    msk = ' _ _'
    m = partial(utils.mask, inp, msk)
    assert m() == 'a_c_'
    assert m(char='_') == ' b d'
    assert m(replace='*') == 'a*c*'
    assert m(invert=True) == ' b d'
