from functools import reduce
from str2d import utils


class Str2D(object):
    def __init__(
            self, inp,
            min_width=None, halign='left', hfill='',
            min_height=None, valign='top', vfill=''
    ):

        self.halign = halign
        self.valign = valign
        self.hfill = hfill
        self.vfill = vfill

        if isinstance(inp, str):
            self.s = tuple(inp.split('\n'))
        elif hasattr(inp, '__iter__'):
            self.s = tuple(map(str, inp))
        elif isinstance(inp, type(self)):
            self.s = inp.s

        self._norm_height(min_height)
        self._norm_width(min_width)

################################################################################
# Internals
################################################################################

    def _norm_width(self, min_width=None):

        halign = self.halign
        hfill = self.hfill
        width = max(self.width, min_width or 0)

        align_dict = dict(right='>', left='<', center='^')
        alignment = align_dict.get(halign.lower(), '<')

        _fmt = lambda x: f'{x:{hfill}{alignment}{width}}'

        self.s = tuple(map(_fmt, self.s))

        return self

    def _norm_height(self, min_height):

        valign = self.valign
        vfill = self.vfill
        height = max(self.height, min_height or 0)

        delta = height - self.height

        align = dict(
            top=(0, delta),
            middle=(lambda x, y: (x, x + y))(*divmod(delta, 2)),
            bottom=(delta, 0)
        )

        top, bottom = align.get(valign.lower(), align['top'])

        self.s = (vfill,) * top + self.s + (vfill,) * bottom

        return self

    @property
    def _kwargs(self):
        return {k: v for k, v in self.__dict__.items() if k != 's'}

    @property
    def width(self):
        return max(map(len, self.s))

    @property
    def height(self):
        return len(self.s)

    @property
    def shape(self):
        return self.height, self.width

################################################################################
# Orientation permutations
# there are a total of 8
################################################################################

    @property
    def I(self):
        return self

    @property
    def H(self):
        return type(self)(s[::-1] for s in self.s)

    @property
    def V(self):
        return type(self)(self.s[::-1])

    @property
    def T(self):
        return type(self)(map(''.join, zip(*self.s)))

    @property
    def TV(self):
        return self.T.V

    @property
    def VH(self):
        return self.V.H

    @property
    def VT(self):
        return self.V.T

    @property
    def HVT(self):
        return self.H.V.T

################################################################################
# Other matrix like operations
################################################################################

    def roll(self, n, axis=1):
        if axis == 1:
            n = n % self.width
            r = lambda x: x[n:] + x[:n]
            i = map(r, self.s)
        else:
            n = n % self.height
            i = self.s[n:] + self.s[:n]
        return type(self)(i, **self._kwargs)

    def hroll(self, n):
        return self.roll(n, axis=1)

    def vroll(self, n):
        return self.roll(n, axis=0)

    def shuffle(self, seed=None):
        s = utils.shuffle(''.join(self.s), seed=seed)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)

    def asstr2d(self, other):
        if isinstance(other, type(self)):
            return other
        else:
            return type(self)(other)

################################################################################
# Operations
################################################################################

    def __add__(self, other, side='left'):
        """result will inherit from self"""
        if isinstance(other, str) and len(other) == 1:
            other = self.border_left(other)
        else:
            other = self.asstr2d(other)

        height = max(self.height, other.height)
        a = self.__copy__()._norm_height(min_height=height)._norm_width()
        b = other.__copy__()._norm_height(min_height=height)._norm_width()

        if side.lower() == 'left':
            tup = (a.s, b.s)
        elif side.lower() == 'right':
            tup = (b.s, a.s)
        else:
            raise ValueError(f'side: "{side}" has to be "left" or "right"')

        return type(self)(
            tuple(map(''.join, zip(*tup))),
            **self._kwargs
        )

    def __radd__(self, other):
        return self.__add__(other, side='right')

    def __mul__(self, n):
        if not isinstance(n, int):
            raise ValueError(f'`n` {n} has to be an integer.')
        else:
            add = lambda self, other: self + other
            return reduce(add, (self for _ in range(n)))

    def __rmul__(self, n):
        return self * n

    def __truediv__(self, other, side='left'):
        """result will inherit from self"""
        if isinstance(other, str) and len(other) == 1:
            other = self.border_top(other)
        else:
            other = self.asstr2d(other)

        if side.lower() == 'left':
            tup = self.s + other.s
        elif side.lower() == 'right':
            tup = other.s + self.s
        else:
            raise ValueError(f'side: "{side}" has to be "left" or "right"')

        other = self.asstr2d(other)
        return type(self)(tup, **self._kwargs)

    def __rtruediv__(self, other, side='left'):
        return self.__truediv__(other, side='right')

    def __floordiv__(self, n):
        if not isinstance(n, int):
            raise ValueError(f'`n` {n} has to be an integer.')
        else:
            div = lambda self, other: self / other
            return reduce(div, (self for _ in range(n)))

    def __eq__(self, other):
        if isinstance(other, str):
            return self.__repr__() == other
        elif isinstance(other, tuple):
            return self.__repr__() == '\n'.join(map(str, other))
        else:
            return self.__repr__() == other.__repr__()

    def __ne__(self, other):
        return not self == other

    def add(self, other, sep='', side='left'):
        if sep:
            if isinstance(other, str) and len(other) == 1:
                other = self.border_left(other)
            else:
                other = self.asstr2d(other)

            if side=='left':
                los = [self, other]
            elif side=='right':
                los = [other, self]

            return type(self).hjoin(sep, los)
        else:
            return self.__add__(other)

    def radd(self, other, sep=''):
        return self.add(other, sep, side='right')

    def div(self, other, sep='', side='left'):
        if sep:
            if isinstance(other, str) and len(other) == 1:
                other = self.border_top(other)
            else:
                other = self.asstr2d(other)

            if side == 'left':
                los = [self, other]
            elif side == 'right':
                los = [other, self]

            return type(self).vjoin(sep, los)
        else:
            return self.__truediv__(other)

    def rdiv(self, other, sep=''):
        return self.div(other, sep, side='right')

################################################################################
# dunders
################################################################################

    def __repr__(self):
        return '\n'.join(self.s)

    def __getitem__(self, other):
        if isinstance(other, slice):
            return type(self)(self.s[other], **self._kwargs)
        elif (hasattr(other, '__iter__') and
              isinstance(other[0], slice) and
              len(other) == 1):
            return type(self)((x[other[0]] for x in self.s), **self._kwargs)
        else:
            raise ValueError(f'I don\'t like how you did that!')

    def __copy__(self):
        newone = type(self)(self.s)
        newone.__dict__.update(self.__dict__)
        return newone

################################################################################
# Borders
################################################################################

    def box(self, tb, lr, tl, tr, bl, br):
        t = tl + tb * self.width + tr
        b = bl + tb * self.width + br
        f = lambda x: f'{lr}{x}{lr}'
        tups = (t,) + tuple(map(f, self.s)) + (b,)
        return type(self)(tups, **self._kwargs)

    def buffer(self, char, n=1):
        if n:
            return self.box(*(char,) * 6).buffer(char, n=n - 1)
        else:
            return self

    def _border(self, side, char):
        left_right = {'left', 'right'}
        top_bottom = {'top', 'bottom'}
        if side.lower() in left_right:
            return type(self)((char,) * self.height)
        elif side.lower() in top_bottom:
            return type(self)((char * self.width,))
        else:
            raise ValueError(
                f'side: "{side}" must come from {left_right | top_bottom}')

    def border_left(self, char):
        return self._border('left', char)

    def border_right(self, char):
        return self._border('right', char)

    def border_top(self, char):
        return self._border('top', char)

    def border_bottom(self, char):
        return self._border('bottom', char)

    def box_dbl(self):
        return self.box('═', '║', '╔', '╗', '╚', '╝')

    def box_sgl(self):
        return self.box('─', '│', '┌', '┐', '└', '┘')

################################################################################
# String analogs
################################################################################

    def strip2d(self, *args):
        return type(self)(self.__repr__().strip(*args), **self._kwargs)

    def strip(self, *args):
        def _strip(s):
            return s.strip(*args)

        return type(self)(map(_strip, self.s), **self._kwargs)

    def replace(self, *args, **kwargs):
        def _replace(s):
            return s.replace(*args, **kwargs)

        return type(self)(map(_replace, self.s), **self._kwargs)

    def lower(self, *args, **kwargs):
        def _lower(s):
            return s.lower(*args, **kwargs)

        return type(self)(map(_lower, self.s), **self._kwargs)

    def upper(self, *args, **kwargs):
        def _upper(s):
            return s.upper(*args, **kwargs)

        return type(self)(map(_upper, self.s), **self._kwargs)

    def title(self, *args, **kwargs):
        def _title(s):
            return s.title(*args, **kwargs)

        return type(self)(map(_title, self.s), **self._kwargs)

    def count(self, *args, **kwargs):
        def _count(s):
            return s.count(*args, **kwargs)

        return sum(map(_count, self.s))

    @classmethod
    def _join(cls, char, others, axis=1):
        is_border_char = isinstance(char, str) and char.count('\n') == 0
        others = tuple(others)
        if axis == 1:
            if is_border_char:
                j = max(others, key=lambda s: s.height).border_left(char)
            else:
                j = cls(char)

            return reduce(lambda l, r: l + j + r, others)

        elif axis == 0:
            if is_border_char:
                j = max(others, key=lambda s: s.width).border_top(char)
            else:
                j = cls(char)

            return reduce(lambda l, r: l / j / r, others)

    @classmethod
    def equal_width(cls, others):
        others = list(others)
        width = max(map(lambda s: s.width, others))
        return [cls(s.s, **{**s._kwargs, **{'min_width': width}})
                for s in others]

    @classmethod
    def sum(cls, others):
        f = lambda a, b: a + b
        return reduce(f, others)

    @classmethod
    def hjoin(cls, char, others):
        return cls._join(char, others, 1)

    @classmethod
    def vjoin(cls, char, others):
        return cls._join(char, others, 0)

    def join(self, others):
        return type(self).hjoin(self, others)

################################################################################
# Masking
################################################################################

    def mask(self, msk, char=' ', replace=' '):
        msk = self.asstr2d(msk)

        if msk.shape != self.shape:
            raise ValueError(f'shape of msk {msk.shape} != {self.shape}')

        s = utils.mask(''.join(self.s), ''.join(msk.s), char, replace)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)

    def layer(self, msk, char=' '):
        msk = self.asstr2d(msk)

        if msk.shape != self.shape:
            raise ValueError(f'shape of msk {msk.shape} != {self.shape}')

        s = utils.mask(''.join(self.s), ''.join(msk.s), char, None)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)
