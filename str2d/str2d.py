from functools import reduce
from str2d import utils
from pandas import DataFrame, Series
from numpy import ndarray


class Str2D(object):
    def __init__(
        self,
        inp: object,
        min_width: int = None,
        halign: str = "left",
        hfill: str = "",
        min_height: int = None,
        valign: str = "top",
        vfill: str = "",
    ):
        """Str2D is a simple class to embody a two dimensional string.  You can
        add them to place them in a horizontal alignment.  You can divide them
        to place one over another.  You can flip them, roll them, or shuffle.

        When instantiating a Str2D, you can accept the defaults or provide your
        own.  These parameter play a role when the string normalization takes
        place to make sure all lines have the same length and to ensure two
        Str2D objects have the same number of lines when adding.  When combining
        two objects, the first's attributes will be inherited.

        :param inp: Primary input.
            If string, gets split on newline `\n`.
            If DataFrame or ndarray, will supply `__repr__` output and
                split on newline.
            If anything else that is an iterable, will assume each iteration
                is a separate line and take the `str(x)` as the source of that
                line.
            If it is an instance of Str2D, will assume it's data.
            Otherwise, will use `__repr__`.
        :param min_width: We can specify the minimum width that all lines must
            take.
        :param halign: The behavior that defines how the text will align itself
            if ever asked to.  It can take 3 types.
            - 'left'
            - 'center'
            - 'right'
        :param hfill: By default, when the alignment parameter is needed, the
        space is filled up wiht `' '`.  You can change that behavior with this.
        :param min_height: We can specify the minimum height or number of lines.
        :param valign: The behavior that defines how the lines will align itself
            if ever asked to.  It can take 3 types.
            - 'top'
            - 'middle'
            - 'bottom'
        :param vfill: By default, when the alignment parameter is needed, the
        space is filled up wiht `' '`.  You can change that behavior with this.

        Examples
        >>> from str2d import Str2D
        ... s = Str2D('12\\n43')
        ... print(s)
        ... print(s + s)
        ... print((s * 5) / (s.V * 3))
        12
        43
        1212
        4343
        1212121212
        4343434343
        434343
        121212

        """
        self.halign = halign
        self.valign = valign
        self.hfill = hfill
        self.vfill = vfill

        if isinstance(inp, str):
            self.s = tuple(inp.split("\n"))
        elif isinstance(inp, (DataFrame, Series, ndarray)):
            self.s = tuple(inp.__str__().split("\n"))
        elif hasattr(inp, "__iter__"):
            self.s = tuple(map(str, inp))
        elif isinstance(inp, type(self)):
            self.s = inp.s
        else:
            self.s = tuple(inp.__repr__().split("\n"))

        self._norm_height(min_height)
        self._norm_width(min_width)

    ################################################################################
    # Internals
    ################################################################################

    def _norm_width(self, min_width: int = None) -> "Str2D":
        """Internal method that handles making width of all rows the same.  It
        will respect the alignment and fill preferences specified when the
        instance was created.

        :param min_width: This is not preserved as an instance attribute.  Must
            be passed as a parameter.  It controls the minimum width of rows.
        :return: Str2D
        """
        halign = self.halign
        hfill = self.hfill
        width = max(self.width, min_width or 0)

        align_dict = dict(right=">", left="<", center="^")
        alignment = align_dict.get(halign.lower(), "<")

        _fmt = lambda x: f"{x:{hfill}{alignment}{width}}"

        self.s = tuple(map(_fmt, self.s))

        return self

    def _norm_height(self, min_height: int) -> "Str2D":
        """Internal method that handles making number of lines the same as other
        Str2D instances that are being combined.  It will respect the alignment
        and fill preferences specified when the instance was created.

        :param min_height: This is not preserved as an instance attribute.  Must
            be passed as a parameter.  It controls the minimum number of lines.
        :return: Str2D
        """
        valign = self.valign
        vfill = self.vfill
        height = max(self.height, min_height or 0)

        delta = height - self.height

        align = dict(
            top=(0, delta),
            middle=(lambda x, y: (x, x + y))(*divmod(delta, 2)),
            bottom=(delta, 0),
        )

        top, bottom = align.get(valign.lower(), align["top"])

        self.s = (vfill,) * top + self.s + (vfill,) * bottom

        return self

    @property
    def _kwargs(self) -> dict:
        """Dictionary of attributes necessary for creating a new Str2D instance
        with the same properties.

        :return: dict
        """
        return {k: v for k, v in self.__dict__.items() if k != "s"}

    @property
    def width(self) -> int:
        return max(map(len, self.s))

    @property
    def height(self) -> int:
        return len(self.s)

    @property
    def shape(self) -> (int, int):
        return self.height, self.width

    ################################################################################
    # Orientation permutations
    # there are a total of 8
    ################################################################################

    @property
    def I(self) -> "Str2D":
        """Identity method.  It exists mostly to make myself feel better about
        having a complete set of 8 transformations.  See below for the others.

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.I
        abc|abc
        def|def
        ghi|ghi
        """
        return self

    @property
    def H(self) -> "Str2D":
        """Horizontal flip or "mirror" method.

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.H
        abc|cba
        def|fed
        ghi|ihg
        """
        return type(self)(s[::-1] for s in self.s)

    @property
    def V(self) -> "Str2D":
        """Vertical flip.

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s.V
        abc|ghi
        def|def
        ghi|abc
        """
        return type(self)(self.s[::-1])

    @property
    def T(self) -> "Str2D":
        """Transpose

        :return: Str2C

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.T
        abc|adg
        def|beh
        ghi|cfi
        """
        return type(self)(map("".join, zip(*self.s)))

    @property
    def TV(self) -> "Str2D":
        """Transpose followed by a Vertical flip results in π/2 counter
        clockwise rotation.

        Synonyms: Horizontal flip followed by a Transpose HT

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.TV
        abc|cfi
        def|beh
        ghi|adg
        """
        return self.T.V

    HT = TV

    @property
    def VH(self) -> "Str2D":
        """Vertical flip followed by a Horizontal flip results in a π rotation
        (either direction).

        Synonyms: Horizontal flip followed by a Vertical flip.

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.VH
        abc|ihg
        def|fed
        ghi|cba
        """
        return self.V.H

    HV = VH

    @property
    def VT(self) -> "Str2D":
        """Vertical flip followed by a Transpose results in a π/2 clockwise
        rotation.

        Synonyms: Transpose followed by a Horizontal flip

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.VT
        abc|gda
        def|heb
        ghi|ifc
        """
        return self.V.T

    TH = VT

    @property
    def HVT(self) -> "Str2D":
        """Horizontal flip followed by a Vertical flip followed by a Transpoose
        results in a Transpose along secondary diagonal.

        Synonyms: VHT

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.HVT
        abc|ifc
        def|heb
        ghi|gda
        """
        return self.H.V.T

    VHT = HVT

    ################################################################################
    # Other matrix like operations
    ################################################################################

    def roll(self, n: int, axis: int = 1) -> "Str2D":
        """Shift columns or rows by `n` amount.  Columns or rows at the front
        will roll over to the back.

        :param n: Number of columns or rows to shift.
        :param axis: 1 is for columns, 0 is for rows
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... Str2D.hjoin(
        ...     '|', [s, s.roll(n=1, axis=0), s.roll(n=1, axis=1)])
        abc|def|bca
        def|ghi|efd
        ghi|abc|hig
        """
        if axis == 1:
            n = n % self.width
            r = lambda x: x[n:] + x[:n]
            i = map(r, self.s)
        else:
            n = n % self.height
            i = self.s[n:] + self.s[:n]
        return type(self)(i, **self._kwargs)

    def hroll(self, n: int) -> "Str2D":
        """Shift columns by `n` amount.  Columns at the front roll over to the
        back.  Leverages `roll` method

        :param n: Number of columns to shift.
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.hroll(2)
        abc|cab
        def|fde
        ghi|igh
        """
        return self.roll(n, axis=1)

    def vroll(self, n: int) -> "Str2D":
        """Shift rows by `n` amount.  Rows at the front roll over to the back.
        Leverages `roll` method

        :param n: Number of rows to shift.
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.vroll(2)
        abc|ghi
        def|abc
        ghi|def
        """
        return self.roll(n, axis=0)

    def shuffle(self, seed: object = None) -> "Str2D":
        """Randomly shuffles characters throughout the Str2D.

        :param seed: seed for `random` module if you want to target a specific
            randomization.  seed takes anything that is hashable.
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + '|' + s.shuffle(seed=3.14)
        abc|cfa
        def|hbe
        ghi|gid
        """
        s = utils.shuffle("".join(self.s), seed=seed)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)

    def asstr2d(self, other: object) -> "Str2D":
        """If `other` is already a `Str2D` it returns the same thing.  Otherwise
        it will construct a new `Str2D` from whatever `other` is.

        :param other: Either a `Str2D` or `object`
        :return: Str2D
        """
        if isinstance(other, type(self)):
            return other
        else:
            return type(self)(other)

    ################################################################################
    # Operations
    ################################################################################

    def __add__(self, other: object, side: str = "left") -> "Str2D":
        """This method shouldn't typically be accessed directly but rather
        through the `+` operator.

        :param other: Thing to be added
        :param side: add to the `'left'` or `'right'` side
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s + s.H
        abccba
        deffed
        ghiihg
        """
        if isinstance(other, str) and len(other) == 1:
            other = self.border_left(other)
        else:
            other = self.asstr2d(other)

        height = max(self.height, other.height)
        a = self.__copy__()._norm_height(min_height=height)._norm_width()
        b = other.__copy__()._norm_height(min_height=height)._norm_width()

        if side.lower() == "left":
            tup = (a.s, b.s)
        elif side.lower() == "right":
            tup = (b.s, a.s)
        else:
            raise ValueError(f'side: "{side}" has to be "left" or "right"')

        return type(self)(tuple(map("".join, zip(*tup))), **self._kwargs)

    def __radd__(self, other: object) -> "Str2D":
        """If you add a non Str2D object on the left side the other object's
        __add__ method will likely send it here.  As with `__add__`, you are not
        supposed to access this method directly.

        :param other: Thing to be added
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... 'hello\\nworld' + s
        helloabc
        worlddef
             ghi
        """
        return self.__add__(other, side="right")

    def __mul__(self, n: int) -> "Str2D":
        """This method shoudln't typically be accessed directly but rather
        through the `*` operator.

        :param n: number of times to repeat `self`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s * 3
        abcabcabc
        defdefdef
        ghighighi
        """
        if not isinstance(n, int):
            raise ValueError(f"`n` {n} has to be an integer.")
        else:
            add = lambda self, other: self + other
            return reduce(add, (self for _ in range(n)))

    def __rmul__(self, n: int) -> "Str2D":
        """This method shoudln't typically be accessed directly but rather
        through the `*` operator.

        :param n: number of times to repeat `self`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... 3 * s
        abcabcabc
        defdefdef
        ghighighi
        """
        return self * n

    def __truediv__(self, other: object, side: str = "left") -> "Str2D":
        """This method shouldn't typically be accessed directly but rather
        through the `/` operator.

        :param other: Thing to be placed below or above
        :param side: place to the `'left'` (above) or `'right'` (below)
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... s / s.V
        abc
        def
        ghi
        ghi
        def
        abc
        """
        if isinstance(other, str) and len(other) == 1:
            other = self.border_top(other)
        else:
            other = self.asstr2d(other)

        if side.lower() == "left":
            tup = self.s + other.s
        elif side.lower() == "right":
            tup = other.s + self.s
        else:
            raise ValueError(f'side: "{side}" has to be "left" or "right"')

        other = self.asstr2d(other)
        return type(self)(tup, **self._kwargs)

    def __rtruediv__(self, other: object) -> "Str2D":
        """This method shouldn't typically be accessed directly but rather
        through the `/` operator.

        :param other: Thing to be placed above
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... 'hello\\nworld' / s
        hello
        world
        abc
        def
        ghi
        """
        return self.__truediv__(other, side="right")

    def __floordiv__(self, n: int) -> "Str2D":
        """This method shoudln't typically be accessed directly but rather
        through the `//` operator.

        :param n: number of times to repeat `self`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abcdefghij')
        ... s // 3
        abcdefghij
        abcdefghij
        abcdefghij
        """
        if not isinstance(n, int):
            raise ValueError(f"`n` {n} has to be an integer.")
        else:
            div = lambda self, other: self / other
            return reduce(div, (self for _ in range(n)))

    def __rfloordiv__(self, n: int) -> "Str2D":
        """This method shoudln't typically be accessed directly but rather
        through the `//` operator.

        :param n: number of times to repeat `self`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abcdefghij')
        ... 3 // s
        abcdefghij
        abcdefghij
        abcdefghij
        """
        return self // n

    def __eq__(self, other: object) -> bool:
        """Will check if `self`'s string representation is the same as
        what is being compared against.

        :param other: Thing to be compared
        :return: bool

        >>> from str2d import Str2D
        ... s = Str2D('abcdefghij')
        ... s == 'abcdefghij'
        True
        """
        if isinstance(other, str):
            return self.__repr__() == other
        elif isinstance(other, tuple):
            return self.__repr__() == "\n".join(map(str, other))
        else:
            return self.__repr__() == other.__repr__()

    def __ne__(self, other: object) -> bool:
        """Will check if `self`'s string representation is not the same as
        what is being compared against.

        :param other: Thing to be compared
        :return: bool

        >>> from str2d import Str2D
        ... s = Str2D('abcdefghij')
        ... s != 'abcdefghij'
        False
        """
        return not self == other

    def add(self, other: object, sep: object = "", side: str = "left") -> "Str2D":
        """This is the public access method to `+`.  The difference being that
        you can specify a `sep` parameter to place between operands.

        :param other: Thing to be added
        :param sep: Thing that separates operands
        :param side: Left or Right side
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... t = Str2D('123\\n456\\n789')
        ... s.add(t, sep='|')
        abc|123
        def|456
        ghi|789
        """
        if sep:
            if isinstance(other, str) and len(other) == 1:
                other = self.border_left(other)
            else:
                other = self.asstr2d(other)

            if side == "left":
                los = [self, other]
            elif side == "right":
                los = [other, self]

            return type(self).hjoin(sep, los)
        else:
            return self.__add__(other)

    def radd(self, other: object, sep: object = "") -> "Str2D":
        """This is the public access method to `+`.  The difference being that
        you can specify a `sep` parameter to place between operands.

        :param other: Thing to be added
        :param sep: Thing that separates operands
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... t = Str2D('123\\n456\\n789')
        ... s.radd(t, sep='|')
        123|abc
        456|def
        789|ghi
        """
        return self.add(other, sep, side="right")

    def div(self, other: object, sep: object = "", side: str = "left") -> "Str2D":
        """This is the public access method to `/`.  The difference being that
        you can specify a `sep` parameter to place between operands.

        :param other: Thing to be placed above or below
        :param sep: Thing that separates operands
        :param side: Left (above) or Right (below)
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... t = Str2D('123\\n456\\n789')
        ... s.div(t, sep='=')
        abc
        def
        ghi
        ===
        123
        456
        789
        """
        if sep:
            if isinstance(other, str) and len(other) == 1:
                other = self.border_top(other)
            else:
                other = self.asstr2d(other)

            if side == "left":
                los = [self, other]
            elif side == "right":
                los = [other, self]

            return type(self).vjoin(sep, los)
        else:
            return self.__truediv__(other)

    def rdiv(self, other: object, sep: object = "") -> "Str2D":
        """This is the public access method to `/`.  The difference being that
        you can specify a `sep` parameter to place between operands.

        :param other: Thing to be placed above
        :param side: Left (above) or Right (below)
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\ndef\\nghi')
        ... t = Str2D('123\\n456\\n789')
        ... s.rdiv(t, sep='=')
        123
        456
        789
        ===
        abc
        def
        ghi
        """
        return self.div(other, sep, side="right")

    ################################################################################
    # dunders
    ################################################################################

    def __repr__(self):
        return "\n".join(self.s)

    def __getitem__(self, other):
        if isinstance(other, slice):
            return type(self)(self.s[other], **self._kwargs)
        elif isinstance(other, int):
            return self.s[other]
        elif all(map(lambda x: isinstance(x, slice), other)):
            return type(self)(
                map(lambda s: s.__getitem__(other[1]), self.s.__getitem__(other[0]))
            )
        else:
            raise ValueError(f'"{other}" must be slices')

    def __copy__(self):
        newone = type(self)(self.s)
        newone.__dict__.update(self.__dict__)
        return newone

    def __iter__(self):
        return iter(self.s)

    ################################################################################
    # Borders
    ################################################################################

    def box(self, tb: str, lr: str, tl: str, tr: str, bl: str, br: str) -> "Str2D":
        """Use parameters to encompass `self` with a box

        :param tb: Top and bottom edge
        :param lr: Left and right edge
        :param tl: Top left corner
        :param tr: Top right corner
        :param bl: Bottom left corner
        :param br: Bottom right corner
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a')
        ... s.box('═', '║', '╔', '╗', '╚', '╝')
        ╔═╗
        ║a║
        ╚═╝
        """
        t = tl + tb * self.width + tr
        b = bl + tb * self.width + br
        f = lambda x: f"{lr}{x}{lr}"
        tups = (t,) + tuple(map(f, self.s)) + (b,)
        return type(self)(tups, **self._kwargs)

    def buffer(self, char: str, n: int = 1) -> "Str2D":
        """Similar to `Str2D.box` but only uses one character for all corners
        and edges.  Further, we specify how many iterations we want with the
        `n` parameter.

        :param char: Character to use as buffer
        :param n: Number of buffer layers
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a')
        ... s.buffer('*', 2)
        *****
        *****
        **a**
        *****
        *****
        """
        if n:
            return self.box(*(char,) * 6).buffer(char, n=n - 1)
        else:
            return self

    def _border(self, side: str, char: str) -> "Str2D":
        """Single side border. Can be used to separate between two Str2Ds.
        Note that this returns an object with unit width or height.  It is
        not added to the calling instance for your.

        :param side: 'top', 'bottom', 'left', or 'right'
        :param char: Character to use as border
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a\\nb\\nc')
        ... s._border('right', '|')
        |
        |
        |
        """
        left_right = {"left", "right"}
        top_bottom = {"top", "bottom"}
        if side.lower() in left_right:
            return type(self)((char,) * self.height)
        elif side.lower() in top_bottom:
            return type(self)((char * self.width,))
        else:
            raise ValueError(f'side: "{side}" must come from {left_right | top_bottom}')

    def border_left(self, char: str) -> "Str2D":
        """Creates a Str2D object that can act as a border.

        :param char: Character to use for border
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a\\nb\\nc')
        ... s.border_left('|')
        |
        |
        |
        """
        return self._border("left", char)

    def border_right(self, char: str) -> "Str2D":
        """Creates a Str2D object that can act as a border.

        :param char: Character to use for border
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a\\nb\\nc')
        ... s.border_right('|')
        |
        |
        |
        """
        return self._border("right", char)

    def border_top(self, char: str) -> "Str2D":
        """Creates a Str2D object that can act as a border.

        :param char: Character to use for border
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc')
        ... s.border_top('-')
        ---
        """
        return self._border("top", char)

    def border_bottom(self, char: str) -> "Str2D":
        """Creates a Str2D object that can act as a border.

        :param char: Character to use for border
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc')
        ... s.border_bottom('-')
        ---
        """
        return self._border("bottom", char)

    def box_dbl(self) -> "Str2D":
        """Convenience method to perform what can be done with Str2D.box

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a')
        ... s.box_dbl()
        ╔═╗
        ║a║
        ╚═╝
        """
        return self.box("═", "║", "╔", "╗", "╚", "╝")

    def box_sgl(self) -> "Str2D":
        """Convenience method to perform what can be done with Str2D.box

        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('a')
        ... s.box_sgl()
        ┌─┐
        │a│
        └─┘
        """
        return self.box("─", "│", "┌", "┐", "└", "┘")

    def fill(self, char: str = " ") -> "Str2D":
        """Fills entire space of calling object with passed character.

        :param char: Character to fill with
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abcde\\nfghij\\nklmno\\npqrst\\nuvwxy')
        ... s + '|' + s.fill('.')
        abcde|.....
        fghij|.....
        klmno|.....
        pqrst|.....
        uvwxy|.....
        """
        return type(self)("\n".join([char * self.width] * self.height), **self._kwargs)

    ################################################################################
    # String analogs
    ################################################################################

    def strip2d(self, *args) -> "Str2D":
        """Perform something similar to `str.strip` but apply it on the top and
        bottom of Str2D as well as left and right.  It will readjust to respect
        alignment and fill preferences.

        :param args: arguments passed to `str.strip`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('     \\nfghi \\n lmno\\n ')
        ... s.strip2d()
        fghi
        lmno
        """
        return type(self)(self.__repr__().strip(*args), **self._kwargs).strip(*args)

    def strip(self, *args) -> "Str2D":
        """Apply `str.strip` to each row.

        :param args: arguments passed to `str.strip`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('fghi   \\n   lmno')
        ... s.strip()
        fghi
        lmno
        """

        def _strip(s):
            return s.strip(*args)

        return type(self)(map(_strip, self.s), **self._kwargs)

    def replace(self, *args, **kwargs) -> "Str2D":
        """Apply `str.replace` to each row.

        :param args: arguments passed to `str.replace`
        :param kwargs: arguments passed to `str.replace`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('1-2-3-4\\n5-6-7-8')
        ... s.replace('-', '*')
        1*2*3*4
        5*6*7*8
        """

        def _replace(s):
            return s.replace(*args, **kwargs)

        return type(self)(map(_replace, self.s), **self._kwargs)

    def lower(self, *args, **kwargs) -> "Str2D":
        """Apply `str.lower` to each row.

        :param args: arguments passed to `str.lower`
        :param kwargs: arguments passed to `str.lower`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('ABC\\n1D3')
        ... s.lower()
        abc
        1d3
        """

        def _lower(s):
            return s.lower(*args, **kwargs)

        return type(self)(map(_lower, self.s), **self._kwargs)

    def upper(self, *args, **kwargs) -> "Str2D":
        """Apply `str.upper` to each row.

        :param args: arguments passed to `str.upper`
        :param kwargs: arguments passed to `str.upper`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\n1d3')
        ... s.upper()
        ABC
        1D3
        """

        def _upper(s):
            return s.upper(*args, **kwargs)

        return type(self)(map(_upper, self.s), **self._kwargs)

    def title(self, *args, **kwargs) -> "Str2D":
        """Apply `str.title` to each row.

        :param args: arguments passed to `str.title`
        :param kwargs: arguments passed to `str.title`
        :return: Str2D

        >>> from str2d import Str2D
        ... s = Str2D('abc\\n1d3')
        ... s.title()
        Abc
        1D3
        """

        def _title(s):
            return s.title(*args, **kwargs)

        return type(self)(map(_title, self.s), **self._kwargs)

    def count(self, *args, **kwargs) -> int:
        """Apply `str.count` to each row.

        :param args: arguments passed to `str.count`
        :param kwargs: arguments passed to `str.count`
        :return: int

        >>> from str2d import Str2D
        ... s = Str2D('a-b-c-d\\n1-2-3-4')
        ... s.count('-')
        6
        """

        def _count(s):
            return s.count(*args, **kwargs)

        return sum(map(_count, self.s))

    @classmethod
    def _join(cls, char: str, others: tuple, axis: int = 1) -> "Str2D":
        """Will join Str2D objects either horizontally or vertically.

        :param char: Character that will be used to join with.
        :param others: Collection of objects that will be joined
        :param axis: Either 0 or 1 representing rows or columns respectively.
        :return: Str2D

        >>> from str2d import Str2D
        >>> s = Str2D('ab\\ncd')
        ... Str2D._join(' | ', [s] * 3)
        ab | ab | ab
        cd | cd | cd

        >>> from str2d import Str2D
        >>> s = Str2D('ab\\ncd')
        ... Str2D._join('-', [s] * 3, axis=0)
        ab
        cd
        --
        ab
        cd
        --
        ab
        cd
        """
        is_border_char = isinstance(char, str) and char.count("\n") == 0
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
    def equal_width(cls, others: list) -> list:
        """Helps to normalize across multiple Str2D objects to be the same
        width

        :param others: list of objects to for which to determine width
        :return: list

        >>> from str2d import Str2D
        >>> s1 = Str2D('a', hfill='*')
        >>> s2 = Str2D('bbbbb')
        >>> s1, s2 = Str2D.equal_width([s1, s2])
        >>> s1 / s2
        a****
        bbbbb
        """
        others = list(others)
        width = max(map(lambda s: s.width, others))
        return [cls(s.s, **{**s._kwargs, **{"min_width": width}}) for s in others]

    @classmethod
    def sum(cls, others: list) -> "Str2D":
        """Iteratively adds all items in the list together

        :param others: list of objects to be added together
        :return: Str2D

        >>> from str2d import Str2D
        >>> s = Str2D('a')
        >>> Str2D.sum([s] * 10)
        aaaaaaaaaa
        """

        def f(a, b):
            return a + b

        return reduce(f, others)

    @classmethod
    def hjoin(cls, char: str, others: list) -> "Str2D":
        """Join others horizontally

        :param char: Character to join on
        :param others: list of objects to join
        :return: Str2D

        >>> from str2d import Str2D
        >>> s = Str2D('a')
        >>> Str2D.hjoin('-', [s] * 10)
        a-a-a-a-a-a-a-a-a-a
        """
        return cls._join(char, others, 1)

    @classmethod
    def vjoin(cls, char: str, others: list) -> "Str2D":
        """Joint others vertically

        :param char: Character to join on
        :param others: list of objects to join
        :return: Str2D

        >>> from str2d import Str2D
        >>> s = Str2D('abc')
        >>> Str2D.vjoin('-', [s] * 3)
        abc
        ---
        abc
        ---
        abc
        """
        return cls._join(char, others, 0)

    def join(self, others: list) -> "Str2D":
        """Join others horizontally separated with `self`

        :param others: list of objects to join
        :return: Str2D

        >>> from str2d import Str2D
        >>> s = Str2D('a\\nb\\nc')
        >>> s.join([(s * 2).fill('#')] * 4)
        ##a##a##a##
        ##b##b##b##
        ##c##c##c##
        """
        return type(self).hjoin(self, others)

    ################################################################################
    # Masking
    ################################################################################

    def mask(self, msk: "Str2D", char: str = " ", replace: str = " ") -> "Str2D":
        """Use another Str2D object to mask.

        :param msk: Str2D object that will act as mask
        :param char: Character to look for
        :param replace: What to replace found character with
        :return: Str2D
        """
        msk = self.asstr2d(msk)

        if msk.shape != self.shape:
            raise ValueError(f"shape of msk {msk.shape} != {self.shape}")

        s = utils.apply_mask("".join(self.s), "".join(msk.s), char, replace)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)

    def layer(self, msk: "Str2D", char: str = " ") -> "Str2D":
        """Instead of masking, we can stack objects.

        :param msk: Str2D object that will act as mask
        :param char: Character to look for
        :return: Str2D
        """
        msk = self.asstr2d(msk)

        if msk.shape != self.shape:
            raise ValueError(f"shape of msk {msk.shape} != {self.shape}")

        s = utils.apply_mask("".join(self.s), "".join(msk.s), char, None)
        i = utils.chunk(s, self.width)
        return type(self)(i, **self._kwargs)


if __name__ == "__main__":

    print("running str2D")
