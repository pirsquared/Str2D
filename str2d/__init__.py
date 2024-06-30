"""Manipulate 2D strings in Python."""

from functools import reduce, cached_property, lru_cache
from dataclasses import dataclass
from textwrap import indent
from enum import Enum
from typing import List, Tuple, Union, Any, Optional
from pandas import DataFrame, Series
import numpy as np
import mpmath as mp


@dataclass
class BoxParts:
    """Box parts organizes box drawing characters into attribute names that are short
    and descriptive. This makes it easier to work with box drawing characters in code.

    The tables below show the attribute names, examples, and descriptions of the parts.

    .. _box-parts-doc-table-1:

    +-------------+-----------+-------------------------------------------+
    | Attribute   | Example   | Description                               |
    | Name        | Value     |                                           |
    +====+===+====+===+===+===+==============+============+===============+
    | ul | t | ur | ┌ | ┬ | ┐ | | Upper-left | | Top T    | | Upper-right |
    |    |   |    |   |   |   | | corner     | | cross    | | corner      |
    +----+---+----+---+---+---+--------------+------------+---------------+
    | l  | c | r  | ├ | ┼ | ┤ | | Left T     | | Center   | | Right T     |
    |    |   |    |   |   |   | | cross      | | cross    | | cross       |
    +----+---+----+---+---+---+--------------+------------+---------------+
    | ll | b | lr | └ | ┴ | ┘ | | Lower-left | | Bottom T | | Lower-right |
    |    |   |    |   |   |   | | corner     | | cross    | | corner      |
    +----+---+----+---+---+---+--------------+------------+---------------+


    .. _box-parts-doc-table-2:

    +--------------------+----------+------------+
    | **Attribute Name** | v        | h          |
    +--------------------+----------+------------+
    | **Example Value**  | │        | ─          |
    +--------------------+----------+------------+
    | **Description**    | Vertical | Horizontal |
    +--------------------+----------+------------+

    You can pass any unicode characters to the BoxParts class and it will categorize
    them accordingly. But the expectation would be something like the example above.

    .. testcode::

        from str2d import BoxParts

        BoxParts(
            v='│', h='─', ul='┌', ur='┐', lr='┘', ll='└',
            l='├', r='┤', t='┬', b='┴', c='┼'
        )

    .. testoutput::

        ┌─┬─┐
        │ │ │
        ├─┼─┤
        │ │ │
        └─┴─┘

    Or you can pass the any characters you want to the BoxParts class and it will
    categorize them accordingly.  In this example we use the unicode character for
    a full block to be all the box parts.

    .. testcode::

        BoxParts(*"█"*11)

    .. testoutput::

        █████
        █ █ █
        █████
        █ █ █
        █████

    """

    v: str  # Vertical line
    h: str  # Horizontal line
    ul: str  # Upper-left corner
    ur: str  # Upper-right corner
    lr: str  # Lower-right corner
    ll: str  # Lower-left corner
    l: str  # Left T (cross)
    r: str  # Right T (cross)
    t: str  # Top T (cross)
    b: str  # Bottom T (cross)
    c: str  # Center cross

    def __str__(self):
        """Return the box parts as a string to illustrate what the box looks like."""
        return "\n".join(
            [
                f"{self.ul}{self.h}{self.t}{self.h}{self.ur}",
                f"{self.v} {self.v} {self.v}",
                f"{self.l}{self.h}{self.c}{self.h}{self.r}",
                f"{self.v} {self.v} {self.v}",
                f"{self.ll}{self.h}{self.b}{self.h}{self.lr}",
            ]
        )

    def __repr__(self):
        """Return the box parts as a string to illustrate what the box looks like."""
        return str(self)

    def to_str2d(self):
        """Convert the box parts to a Str2D object."""
        return Str2D(data=str(self), halign="left", valign="bottom")


class BoxStyle(Enum):
    """BoxStyle is an enumeration of different box styles that can be used to draw
    boxes around text.  The box styles are made up of BoxParts objects that contain
    the box drawing characters.  The main purpose of this class is to provide a way
    to apply box drawing over Str2D objects.

    You can see all the box styles by calling the swatches method.

    .. testcode::

        from str2d import BoxStyle

        BoxStyle.swatches()

    .. testoutput::

                                                        DASHED      DASHED
                                            DASHED      DOUBLE      DOUBLE
                    SINGLE      DASHED      DOUBLE      LIGHT       HEAVY
        SINGLE      HEAVY       DOUBLE      HEAVY       HEAVY       LIGHT
        ┌─┬─┐       ┏━┳━┓       ┌╌┬╌┐       ┏╍┳╍┓       ┍╍┯╍┑       ┎╌┰╌┒
        │ │ │       ┃ ┃ ┃       ╎ ╎ ╎       ╏ ╏ ╏       ╎ ╎ ╎       ╏ ╏ ╏
        ├─┼─┤       ┣━╋━┫       ├╌┼╌┤       ┣╍╋╍┫       ┝╍┿╍┥       ┠╌╂╌┨
        │ │ │       ┃ ┃ ┃       ╎ ╎ ╎       ╏ ╏ ╏       ╎ ╎ ╎       ╏ ╏ ╏
        └─┴─┘       ┗━┻━┛       └╌┴╌┘       ┗╍┻╍┛       ┕╍┷╍┙       ┖╌┸╌┚

                                DASHED      DASHED
                    DASHED      TRIPLE      TRIPLE                  DASHED
        DASHED      TRIPLE      LIGHT       HEAVY       DASHED      QUADRUPLE
        TRIPLE      HEAVY       HEAVY       LIGHT       QUADRUPLE   HEAVY
        ┌┄┬┄┐       ┏┅┳┅┓       ┍┅┯┅┑       ┎┄┰┄┒       ┌┈┬┈┐       ┏┉┳┉┓
        ┆ ┆ ┆       ┇ ┇ ┇       ┆ ┆ ┆       ┇ ┇ ┇       ┊ ┊ ┊       ┋ ┋ ┋
        ├┄┼┄┤       ┣┅╋┅┫       ┝┅┿┅┥       ┠┄╂┄┨       ├┈┼┈┤       ┣┉╋┉┫
        ┆ ┆ ┆       ┇ ┇ ┇       ┆ ┆ ┆       ┇ ┇ ┇       ┊ ┊ ┊       ┋ ┋ ┋
        └┄┴┄┘       ┗┅┻┅┛       ┕┅┷┅┙       ┖┄┸┄┚       └┈┴┈┘       ┗┉┻┉┛

        DASHED      DASHED
        QUADRUPLE   QUADRUPLE               DASHED      DASHED      DASHED
        LIGHT       HEAVY       SINGLE      DOUBLE      TRIPLE      QUADRUPLE
        HEAVY       LIGHT       ROUND       ROUND       ROUND       ROUND
        ┍┉┯┉┑       ┎┈┰┈┒       ╭─┬─╮       ╭╌┬╌╮       ╭┄┬┄╮       ╭┈┬┈╮
        ┊ ┊ ┊       ┋ ┋ ┋       │ │ │       ╎ ╎ ╎       ┆ ┆ ┆       ┊ ┊ ┊
        ┝┉┿┉┥       ┠┈╂┈┨       ├─┼─┤       ├╌┼╌┤       ├┄┼┄┤       ├┈┼┈┤
        ┊ ┊ ┊       ┋ ┋ ┋       │ │ │       ╎ ╎ ╎       ┆ ┆ ┆       ┊ ┊ ┊
        ┕┉┷┉┙       ┖┈┸┈┚       ╰─┴─╯       ╰╌┴╌╯       ╰┄┴┄╯       ╰┈┴┈╯

                    DOUBLE      SINGLE      LIGHT       HEAVY
        DOUBLE      SINGLE      DOUBLE      HEAVY       LIGHT
        ╔═╦═╗       ╓─╥─╖       ╒═╤═╕       ┎─┰─┒       ┍━┯━┑
        ║ ║ ║       ║ ║ ║       │ │ │       ┃ ┃ ┃       │ │ │
        ╠═╬═╣       ╟─╫─╢       ╞═╪═╡       ┠─╂─┨       ┝━┿━┥
        ║ ║ ║       ║ ║ ║       │ │ │       ┃ ┃ ┃       │ │ │
        ╚═╩═╝       ╙─╨─╜       ╘═╧═╛       ┖─┸─┚       ┕━┷━┙

    """

    SINGLE = BoxParts(*"│─┌┐┘└├┤┬┴┼")
    SINGLE_HEAVY = BoxParts(*"┃━┏┓┛┗┣┫┳┻╋")
    DASHED_DOUBLE = BoxParts(*"╎╌┌┐┘└├┤┬┴┼")
    DASHED_DOUBLE_HEAVY = BoxParts(*"╏╍┏┓┛┗┣┫┳┻╋")
    DASHED_DOUBLE_LIGHT_HEAVY = BoxParts(*"╎╍┍┑┙┕┝┥┯┷┿")
    DASHED_DOUBLE_HEAVY_LIGHT = BoxParts(*"╏╌┎┒┚┖┠┨┰┸╂")
    DASHED_TRIPLE = BoxParts(*"┆┄┌┐┘└├┤┬┴┼")
    DASHED_TRIPLE_HEAVY = BoxParts(*"┇┅┏┓┛┗┣┫┳┻╋")
    DASHED_TRIPLE_LIGHT_HEAVY = BoxParts(*"┆┅┍┑┙┕┝┥┯┷┿")
    DASHED_TRIPLE_HEAVY_LIGHT = BoxParts(*"┇┄┎┒┚┖┠┨┰┸╂")
    DASHED_QUADRUPLE = BoxParts(*"┊┈┌┐┘└├┤┬┴┼")
    DASHED_QUADRUPLE_HEAVY = BoxParts(*"┋┉┏┓┛┗┣┫┳┻╋")
    DASHED_QUADRUPLE_LIGHT_HEAVY = BoxParts(*"┊┉┍┑┙┕┝┥┯┷┿")
    DASHED_QUADRUPLE_HEAVY_LIGHT = BoxParts(*"┋┈┎┒┚┖┠┨┰┸╂")
    SINGLE_ROUND = BoxParts(*"│─╭╮╯╰├┤┬┴┼")
    DASHED_DOUBLE_ROUND = BoxParts(*"╎╌╭╮╯╰├┤┬┴┼")
    DASHED_TRIPLE_ROUND = BoxParts(*"┆┄╭╮╯╰├┤┬┴┼")
    DASHED_QUADRUPLE_ROUND = BoxParts(*"┊┈╭╮╯╰├┤┬┴┼")
    DOUBLE = BoxParts(*"║═╔╗╝╚╠╣╦╩╬")
    DOUBLE_SINGLE = BoxParts(*"║─╓╖╜╙╟╢╥╨╫")
    SINGLE_DOUBLE = BoxParts(*"│═╒╕╛╘╞╡╤╧╪")
    LIGHT_HEAVY = BoxParts(*"┃─┎┒┚┖┠┨┰┸╂")
    HEAVY_LIGHT = BoxParts(*"│━┍┑┙┕┝┥┯┷┿")

    def to_str2d(self):
        """Convert the box style to a Str2D object."""
        return "\n".join(self.name.split("_")) / self.value.to_str2d()

    def __str__(self):
        """Return the box style as a string to illustrate what the box looks like."""
        return str(self.to_str2d())

    def __repr__(self):
        """Return the box style as a string to illustrate what the box looks like."""
        return str(self)

    @classmethod
    def swatches(cls):
        """Return a Str2D object with the box style swatches."""

        master_box_list = Str2D.equal_width(
            *[value.to_str2d() for value in cls.__members__.values()]
        )

        master_matrix = []
        row = None
        for i, value in enumerate(master_box_list):
            if i % 6 == 0:
                row = []
                master_matrix.append(row)
            row.append(value)

        result = Str2D.join_v(
            *[Str2D.join_h(*row, sep="   ") for row in master_matrix], sep=Str2D(" ")
        )

        return result


class Str2D:
    """Str2D is a class that allows you to manipulate 2D strings in Python.  I had found
    myself wanting to paste blocks of text inline with other blocks of text.  If you've
    ever tried to do this in a text editor, you'll know that it can be a bit of a pain.
    vi and vim have a feature called visual block mode that makes this easier.  But I
    wanted more flexibility and control.  So I created Str2D.
    
    Given a multi-line string, Str2D will convert it into something functionally
    equivalent where each line separated by a newline character will have the same
    number of characters.  These are filled in with whatever character is specified but
    by default it is a space.  This takes care of making sure that each row is the same
    width and is primed for manipulation.

    The simplest example is to show how to create a Str2D object from a multi-line
    string and add it to another Str2D object.

    Let's start by constructing a new instance of Str2D and assinging it to the variable
    `a`.

    .. testcode::

        from str2d import Str2D

        a = Str2D('a b c d\\ne f g\\nh i\\nj')
        a

    .. testoutput::

        a b c d
        e f g  
        h i    
        j      

    It might not be clear but the 2nd, 3rd, and 4th lines are padded with spaces to make
    each line the same width.  We can see this more clearly surrounding the object with
    a box.

    .. testcode::

        a.box()

    .. testoutput::

        ╭───────╮
        │a b c d│
        │e f g  │
        │h i    │
        │j      │
        ╰───────╯

    The padded characters are not just spaces.  The Str2D object is a structured array
    with two fields: 'char' and 'alpha'.  The 'char' field is the character array and
    the 'alpha' field is a boolean array with a of 1 or 0 for every character in the
    character array.  The 'alpha' field is used to determine if a character will mask a
    second Str2D object when layered on top of it.  It is analogous to the alpha channel
    in an image where when layered on top of another image, the alpha channel will
    indicate which pixels will be visible and which will be transparent.  The 'alpha'
    field is used in the same way.  A value of 1 means the character will be visible and
    a value of 0 means the character will be transparent.  The padded characters are all
    given an 'alpha' value of 0.

    If we use the Str3D object to layer another Str2D object below it, we'll see that
    the padded characters will be transparent and the characters from the second Str2D
    object will be visible.

    .. testcode::

        from str2d import Str3D

        b = Str2D('''\\
        .......
        .......
        .......
        .......
        ''')

        Str3D([a, b])

    .. testoutput::

        a b c d
        e f g..
        h i....
        j......

    We can accomplish the same thing by using the `fill_with` method. This method will
    fill the padded characters with the specified character.  More accurately, it will
    replace the characters in the 'char' field where the 'alpha' field is 0 with the
    specified character.

    .. testcode::

        a.fill_with('.')

    .. testoutput::

        a b c d
        e f g..
        h i....
        j......

    If we wanted to make all spaces transparent, we could use the `hide` method.  This
    will set the 'alpha' field to 0 for all locations where the `char` field matches the
    specified character, which defaults to a space.

    .. testcode::

        a.hide().fill_with('.')

    .. testoutput::

        a.b.c.d
        e.f.g..
        h.i....
        j......

    Let's create a new Str2D object and assign it to the variable `c`.  This time we'll
    set the `halign` parameter to 'right' which controls how lines with fewer characters
    than the maximum width are aligned.  By default, it is set to 'left' which will
    align the lines to the left as we've seen in the previous example with the variable
    `a`.

    .. testcode::

        c = Str2D('0\\n1 2\\n3 4 5\\n6 7 8 9', halign='right')
        c

    .. testoutput::

              0
            1 2
          3 4 5
        6 7 8 9

    We can now see our simple example of adding two Str2D objects together.

    .. testcode::
    
            a + c

    .. testoutput::

        a b c d      0
        e f g      1 2
        h i      3 4 5
        j      6 7 8 9

    All of the transparent characters are preserved and we can fill the result as you'd
    expect.

    .. testcode::

        (a + c).fill_with('.')

    .. testoutput::

        a b c d......0
        e f g......1 2
        h i......3 4 5
        j......6 7 8 9

    We'll save the rest for the documentation of the individual methods.

    """

    # Structured array data type for Str2D objects
    # the 'char' field is the little-endian unicode single character
    # the 'alpha' field is an int8 that is trying its best to be a boolean
    _dtype = np.dtype([("char", "<U1"), ("alpha", "int8")])

    # when doing a transpose, horizontal, or vertical transformations
    # shift the alignments to something that makes sense
    _align_transpose = {
        "top": "left",
        "middle": "center",
        "bottom": "right",
        "left": "top",
        "center": "middle",
        "right": "bottom",
    }
    _align_horizontal = {"left": "right", "center": "center", "right": "left"}
    _align_vertical = {"top": "bottom", "middle": "middle", "bottom": "top"}

    @classmethod
    def struct_pad(cls, array, *args, **kwargs) -> "Str2D":
        """`struct_pad` pads a structured array with fields 'char' and 'alpha'.  The
        method is a wrapper around np.pad that pads the 'char' and 'alpha' fields with
        the fill value specified in the 'fill' keyword argument.

        Parameters
        ----------
        array : np.ndarray
            A structured array with fields 'char' and 'alpha'.

        fill : Tuple[str, int], optional
            The fill value for the 'char' and 'alpha' fields, by default (' ', 0)

        *args : tuple
            Positional arguments to np.pad.

        **kwargs : dict
            Keyword arguments to np.pad.

        Returns
        -------
        np.ndarray
            A structured array with fields 'char' and 'alpha' padded with the fill value
            specified in the 'fill' keyword argument.

        Examples
        --------

        Let's use `Str2D` to create a structured array from a string and then pad it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            a.char

        .. testoutput::

            array([['a', ' ', 'b', ' ', 'c', ' ', 'd'],
                   ['e', ' ', 'f', ' ', 'g', ' ', ' '],
                   ['h', ' ', 'i', ' ', ' ', ' ', ' '],
                   ['j', ' ', ' ', ' ', ' ', ' ', ' ']], dtype='<U1')

        Now let's pad the structured array with the fill value '.'.  The first argument
        is the data.  The next argument is the number of padding elements to add to the
        beginning and end of each axis.

        .. testcode::

            Str2D.struct_pad(a.data, 1, fill=('.', 0))

        .. testoutput::

            array([['.', '.', '.', '.', '.', '.', '.'],
                    ['.', 'a', ' ', 'b', ' ', 'c', 'd'],
                    ['.', 'e', ' ', 'f', ' ', 'g', ' '],
                    ['.', 'h', ' ', 'i', ' ', ' ', ' '],
                    ['.', 'j', ' ', ' ', ' ', ' ', ' '],
                    ['.', '.', '.', '.', '.', '.', '.']], dtype='<U1')

        If we want to control the padding on each side of the array, we can pass a tuple
        of integers to the second argument.  The first integer is the number of padding
        elements to add to the beginning of each axis and the second integer is the
        number of padding elements to add to the end of each axis.

        .. testcode::

            Str2D.struct_pad(a.data, (1, 2), fill=('.', 0))

        .. testoutput::

            array([['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                   ['.', 'a', ' ', 'b', ' ', 'c', ' ', 'd', '.', '.'],
                   ['.', 'e', ' ', 'f', ' ', 'g', ' ', ' ', '.', '.'],
                   ['.', 'h', ' ', 'i', ' ', ' ', ' ', ' ', '.', '.'],
                   ['.', 'j', ' ', ' ', ' ', ' ', ' ', ' ', '.', '.'],
                   ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                   ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.']], dtype='<U1')

        However, you can also control the padding on each side of the array by passing
        the number of padding elements to add to the beginning and end of each axis as
        as tuple of tuples. The first tuple is the number of padding elements to add to
        the beginning and end of the first axis and the second tuple is the number of
        padding elements to add to the beginning and end of the second axis.

        .. testcode::

            Str2D.struct_pad(a.data, ((1, 3), (2, 1)), fill=('.', 0))

        .. testoutput::

            array([['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                   ['.', '.', 'a', ' ', 'b', ' ', 'c', ' ', 'd', '.'],
                   ['.', '.', 'e', ' ', 'f', ' ', 'g', ' ', ' ', '.'],
                   ['.', '.', 'h', ' ', 'i', ' ', ' ', ' ', ' ', '.'],
                   ['.', '.', 'j', ' ', ' ', ' ', ' ', ' ', ' ', '.'],
                   ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                   ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
                   ['.', '.', '.', '.', '.', '.', '.', '.', '.', '.']], dtype='<U1')

        """
        fill = kwargs.pop("fill", (" ", 0))
        char_fill, alpha_fill = fill

        char_kwargs = kwargs.copy()
        char_mode = char_kwargs.setdefault("mode", "constant")
        if char_mode == "constant":
            char_kwargs["constant_values"] = char_fill

        alpha_kwargs = kwargs.copy()
        alpha_mode = alpha_kwargs.setdefault("mode", "constant")
        if alpha_mode == "constant":
            alpha_kwargs["constant_values"] = alpha_fill

        char_pad = np.pad(array["char"], *args, **char_kwargs)
        alpha_pad = np.pad(array["alpha"], *args, **alpha_kwargs)
        padded_data = np.empty(char_pad.shape, dtype=cls._dtype)
        padded_data["char"] = char_pad
        padded_data["alpha"] = alpha_pad

        return padded_data

    @classmethod
    def validate_fill(
        cls, fill: Optional[Union[str, Tuple[str, int]]] = None
    ) -> Tuple[str, int]:
        """Validate the fill value.

        Parameters
        ----------
        fill : Optional[Union[str, Tuple[str, int]]], optional
            The fill value, by default None

        Returns
        -------
        Tuple[str, int]
            A tuple containing the fill character and fill alpha value.
        """
        if fill is None:
            return " ", 0

        if isinstance(fill, str):
            fill_char = fill
            fill_alpha = 0
        elif isinstance(fill, (tuple, list)):
            fill_char, fill_alpha = fill
        else:
            raise ValueError("fill must be a str or tuple.")

        if len(fill_char) != 1:
            raise ValueError("fill_char must be a single character.")

        if not fill_alpha in {0, 1}:
            raise ValueError("fill_alpha must be 0 or 1.")

        return fill_char, fill_alpha

    @classmethod
    def validate_halign(cls, halign: str) -> str:
        """Validate the horizontal alignment.

        Parameters
        ----------
        halign : str
            The horizontal alignment.

        Returns
        -------
        str
            The validated horizontal alignment.
        """
        halign = halign.lower()
        if halign not in {"left", "center", "right"}:
            raise ValueError("halign must be one of 'left', 'center', or 'right'.")
        return halign

    @classmethod
    def validate_valign(cls, valign: str) -> str:
        """Validate the vertical alignment.

        Parameters
        ----------
        valign : str
            The vertical alignment.

        Returns
        -------
        str
            The validated vertical alignment.
        """
        valign = valign.lower()
        if valign not in {"top", "middle", "bottom"}:
            raise ValueError("valign must be one of 'top', 'middle', or 'bottom'.")
        return valign

    @classmethod
    def struct_array_from_string(cls, string: str, **kwargs) -> "Str2D":
        """Create a structured array from a string.

        Parameters
        ----------
        string : str
            A string to convert to a structured array.

        Returns
        -------
        np.ndarray
            A structured array with fields 'char' and 'alpha' created from the input
              string.
        """
        pre_data = [list(row) for row in string.splitlines()]
        # needed to use `pop or 0` as opposed to `pop(key, 0)`
        # because `None` may have been explicitly passed
        min_width = kwargs.pop("min_width", 0) or 0
        min_height = kwargs.pop("min_height", 0) or 0
        data_width = max(map(len, pre_data), default=0)
        data_height = len(pre_data)
        width = max(data_width, min_width)
        height = max(data_height, min_height)

        data = np.empty((height, width), dtype=cls._dtype)
        fill = kwargs.pop("fill", (" ", 0))
        data.fill(fill)

        halign = kwargs.pop("halign", "left")
        valign = kwargs.pop("valign", "top")

        start_v = 0
        if valign == "middle":
            start_v = (height - data_height) // 2
        elif valign == "bottom":
            start_v = height - data_height

        for i, row in enumerate(pre_data, start_v):
            this_width = len(row)
            start = 0
            if halign == "center":
                start = (width - this_width) // 2
            elif halign == "right":
                start = width - this_width
            for j, char in enumerate(row, start):
                data[i, j] = (char, 1)

        return data

    @classmethod
    def struct_array_from_char_array(cls, array: np.ndarray) -> "Str2D":
        """Create a structured array from a character array.

        Parameters
        ----------
        array : np.ndarray
            A 2D character array.

        Returns
        -------
        np.ndarray
            A structured array with fields 'char' and 'alpha' created from the input
              character array.
        """
        data = np.empty(array.shape, dtype=cls._dtype)
        data["char"] = array
        data["alpha"] = 1
        return data

    @classmethod
    def struct_array_from_bool_array(cls, array: np.ndarray, char: str) -> "Str2D":
        """Create a structured array from a boolean array.

        Parameters
        ----------
        array : np.ndarray
            A 2D boolean array.
        char : str
            The character to use when the boolean array is True.

        Returns
        -------
        np.ndarray
            A structured array with fields 'char' and 'alpha' created from the input
              boolean array.
        """
        data = np.empty(array.shape, dtype=cls._dtype)
        data["char"] = np.where(array, char, " ")
        data["alpha"] = np.where(array, 1, 0)
        return data

    @classmethod
    def parse(cls, data: Optional[Any] = None, **kwargs) -> "Str2D":
        """Parse the input data into a structured array.

        Parameters
        ----------
        data : Optional[Any], optional
            The input data, by default None.
        **kwargs : dict
            Additional keyword arguments to pass to the Str2

        Returns
        -------
        np.ndarray
            A structured array with fields 'char' and 'alpha' created from the input
              data.

        """
        if isinstance(data, Str2D):
            data = data.data

        elif isinstance(data, np.ndarray):
            if data.dtype == bool:
                char = kwargs.pop("char", "█")
                data = cls.struct_array_from_bool_array(data, char)
            elif data.dtype != cls._dtype:
                data = cls.struct_array_from_char_array(data)
            else:
                data = data.copy()

        elif isinstance(data, str):
            data = cls.struct_array_from_string(data, **kwargs)

        elif isinstance(data, (DataFrame, Series)):
            data = cls.struct_array_from_string(data.to_string(), **kwargs)

        elif hasattr(data, "__iter__") and not isinstance(data, str):
            data = cls.struct_array_from_string("\n".join(map(str, data)), **kwargs)

        elif data is not None:
            data = cls.struct_array_from_string(str(data), **kwargs)

        else:
            data = cls.struct_array_from_string("", **kwargs)

        return data

    def __init__(
        self,
        data: Optional[Any] = None,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        halign: Optional[str] = "left",
        valign: Optional[str] = "top",
        fill: Optional[Union[str, Tuple[str, int]]] = None,
        **kwargs,
    ) -> None:
        """Create a Str2D object.

        Parameters
        ----------
        data : Optional[Any], optional
            The input data, by default None.
        min_width : Optional[int], optional
            The minimum width of the output, by default None.
        min_height : Optional[int], optional
            The minimum height of the output, by default None.
        halign : Optional[str], optional
            The horizontal alignment, by default 'left'.
        valign : Optional[str], optional
            The vertical alignment, by default 'top'.
        fill : Optional[Union[str, Tuple[str, int]]], optional
            The fill value, by default None.
        **kwargs : dict
            Additional keyword arguments to pass to the parse method.

        Raises
        ------
        ValueError
            If the fill value is invalid.
        ValueError
            If the horizontal alignment is invalid.
        ValueError
            If the vertical alignment is invalid.

        """

        fill = self.validate_fill(fill)
        halign = self.validate_halign(halign)
        valign = self.validate_valign(valign)

        my_kwargs = {
            "min_width": min_width,
            "min_height": min_height,
            "halign": halign,
            "valign": valign,
            "fill": fill,
        }
        data = self.parse(data, **my_kwargs, **kwargs)

        height_input, width_input = data.shape

        height_data = max(height_input, min_height or 0)
        width_data = max(width_input, min_width or 0)

        left = 0
        right = width_data - width_input
        if halign == "center":
            left = (width_data - width_input) // 2
            right = width_data - width_input - left
        elif halign == "right":
            left = width_data - width_input
            right = 0

        top = 0
        bottom = height_data - height_input
        if valign == "middle":
            top = (height_data - height_input) // 2
            bottom = height_data - height_input - top
        elif valign == "bottom":
            top = height_data - height_input
            bottom = 0

        data = self.struct_pad(data, ((top, bottom), (left, right)), fill=fill)

        self.data = data
        self.halign = halign
        self.valign = valign
        self.fill = fill

    @property
    def height(self) -> int:
        """Return the height of the data."""
        return self.data.shape[0]

    @property
    def width(self) -> int:
        """Return the width of the data."""
        return self.data.shape[1]

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the data."""
        return self.data.shape

    @property
    def char(self) -> np.ndarray:
        """Return the character data."""
        return self.data["char"]

    @property
    def alpha(self) -> np.ndarray:
        """Return the alpha data."""
        return self.data["alpha"]

    @property
    def kwargs(self) -> dict:
        """Return the keyword arguments used to create the object."""
        return {
            "halign": self.halign,
            "valign": self.valign,
            "fill": self.fill,
        }

    @cached_property
    def t(self) -> "Str2D":
        """Return the transpose of the data."""
        return Str2D(
            data=self.data.T,
            halign=self._align_transpose[self.valign],
            valign=self._align_transpose[self.halign],
            fill=self.fill,
        )

    @cached_property
    def h(self) -> "Str2D":
        """Return the horizontal flip of the data."""
        return Str2D(
            data=np.fliplr(self.data),
            halign=self._align_horizontal[self.halign],
            valign=self.valign,
            fill=self.fill,
        )

    @cached_property
    def v(self) -> "Str2D":
        """Return the vertical flip of the data."""
        return Str2D(
            data=np.flipud(self.data),
            halign=self.halign,
            valign=self._align_vertical[self.valign],
            fill=self.fill,
        )

    @cached_property
    def r(self) -> "Str2D":
        """Return the 90 degree rotation of the data."""
        return self.t.h

    @lru_cache
    def roll(self, x: int, axis: int) -> "Str2D":
        """Roll the data along an axis.

        Parameters
        ----------
        x : int
            The number of positions to roll.
        axis : int
            The axis to roll along.

        Returns
        -------
        np.ndarray
            The rolled data.
        """
        return Str2D(
            data=np.roll(self.data, x, axis=axis),
            halign=self.halign,
            valign=self.valign,
            fill=self.fill,
        )

    @lru_cache
    def roll_h(self, x: int) -> "Str2D":
        """Roll the data horizontally.

        Parameters
        ----------
        x : int
            The number of positions to roll.

        Returns
        -------
        np.ndarray
            The rolled data.
        """
        return self.roll(x, axis=1)

    @lru_cache
    def roll_v(self, x: int) -> "Str2D":
        """Roll the data vertically.

        Parameters
        ----------
        x : int
            The number of positions to roll.

        Returns
        -------
        np.ndarray
            The rolled data.
        """
        return self.roll(x, axis=0)

    def __getattr__(self, name: str) -> Any:
        """Enables convenient access to the transpose, horizontal flip, vertical flip,
        and rotation methods in a concatenated manner.

        Examples
        --------
        >>> s = Str2D(data='abc\ndef\nghi')
        >>> s.thrvt

        """
        if (p := name[0].lower()) in ["h", "v", "t", "r"]:
            this = getattr(self, p)
            if len(name) == 1:
                return this
            return getattr(getattr(self, p), name[1:])
        raise AttributeError(f"'{Str2D.__name__}' object has no attribute '{name}'")

    def pad(self, *args, **kwargs) -> "Str2D":
        """`pad` pads the data with the fill value specified in the 'fill' keyword and
        is a wrapper around the class method `struct_pad` which in turn is a wrapper
        around np.pad.

        Parameters
        ----------
        fill : Tuple[str, int], optional
            The fill value for the 'char' and 'alpha' fields, by default (' ', 0)

        *args : tuple
            Positional arguments to np.pad.

        **kwargs : dict
            Keyword arguments to np.pad.

        Returns
        -------
        Str2D
            A new Str2D object with the padded data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then pad
        it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            a

        .. testoutput::

            a b c d
            e f g
            h i
            j

        Now let's pad the structured array with the fill value '.'.  The first argument
        is the number of padding elements to add to the beginning and end of each axis.

        .. testcode::

            a.pad(1, fill=('.', 0))

        .. testoutput::

            .........
            .a b c d.
            .e f g  .
            .h i    .
            .j      .
            .........

        If we want to control the padding on each side, we can pass a tuple of integers
        to the first argument.  The first integer is the number of padding elements to
        add to the beginning of each axis and the second integer is the number of
        padding elements to add to the end of each axis.

        .. testcode::

            a.pad((1, 2), fill=('.', 0))

        .. testoutput::

            ..........
            .a b c d..
            .e f g  ..
            .h i    ..
            .j      ..
            ..........
            ..........

        However, you can also control the padding on each side of the array by passing
        the number of padding elements to add to the beginning and end of each axis as
        as tuple of tuples. The first tuple is the number of padding elements to add to
        the beginning and end of the first axis and the second tuple is the number of
        padding elements to add to the beginning and end of the second axis.

        .. testcode::

            a.pad(((1, 3), (2, 1)), fill=('.', 0))

        .. testoutput::

            ..........
            ..a b c d.
            ..e f g  .
            ..h i    .
            ..j      .
            ..........
            ..........
            ..........

        """
        kwargs.setdefault("fill", self.fill)
        padded_data = self.struct_pad(self.data, *args, **kwargs)

        return Str2D(data=padded_data, **self.kwargs)

    def expand(self, x: int = 0, y: int = 0, **kwargs) -> "Str2D":
        """Expand the data.

        Parameters
        ----------
        x : int, optional
            The number of columns to expand, by default 0.
        y : int, optional
            The number of rows to expand, by default 0.
        **kwargs : dict
            Additional keyword arguments to pass to the pad method.

        Returns
        -------
        np.ndarray
            The expanded data.
        """
        top = 0
        left = 0
        if self.halign == "center":
            left = x // 2
        elif self.halign == "right":
            left = x
        if self.valign == "middle":
            top = y // 2
        elif self.valign == "bottom":
            top = y
        right = x - left
        bottom = y - top
        return self.pad(((top, bottom), (left, right)), **kwargs)

    def split(self, axis: int, *args: int) -> List["Str2D"]:
        """Split the data along an axis.

        Parameters
        ----------
        axis : int
            The axis to split along.
        *args : int
            The indices to pass to np.split.

        Returns
        -------
        List[Str2D]
            A list of the split data.

        """
        indices_or_sections, *args = args
        return [
            Str2D(data=split, **self.kwargs)
            for split in np.split(self.data, indices_or_sections, *args, axis=axis)
        ]

    def __getitem__(
        self,
        key: Union[int, slice, Tuple[Union[int, slice], ...], List[Union[int, slice]]],
    ) -> "Str2D":
        """Get the data at the specified indices."""
        if isinstance(key, tuple):
            new_key = tuple(([k] if np.isscalar(k) else k) for k in key)
        elif np.isscalar(key):
            new_key = [key]
        else:
            new_key = key

        return Str2D(data=self.data[new_key], **self.kwargs)

    @classmethod
    def join_h(cls, *args: "Str2D", sep: str = "") -> "Str2D":
        """Join the data horizontally."""
        if sep:
            args = sum(zip([sep] * len(args), args), ())[1:]
        return reduce(lambda x, y: x + y, args)

    @classmethod
    def join_v(cls, *args: "Str2D", sep: str = "") -> "Str2D":
        """Join the data vertically."""
        if sep:
            args = sum(zip([sep] * len(args), args), ())[1:]
        return reduce(lambda x, y: x / y, args)

    @classmethod
    def equal_height(cls, *args: "Str2D") -> "Str2D":
        """Make the data have equal height."""
        max_height = max(arg.height for arg in args)
        return [arg.expand(y=max_height - arg.height) for arg in args]

    @classmethod
    def equal_width(cls, *args: "Str2D") -> "Str2D":
        """Make the data have equal width."""
        max_width = max(arg.width for arg in args)
        return [arg.expand(x=max_width - arg.width) for arg in args]

    @classmethod
    def equal_shape(cls, *args: "Str2D") -> "Str2D":
        """Make the data have equal shape."""
        max_height = max(arg.height for arg in args)
        max_width = max(arg.width for arg in args)
        return [
            arg.expand(x=max_width - arg.width, y=max_height - arg.height)
            for arg in args
        ]

    # math operations
    def __add__(self, other: "Str2D", right_side=False) -> "Str2D":
        """Add the data."""
        other_expand_kwargs = {}
        if isinstance(other, str):
            other_expand_kwargs["mode"] = "edge"
            if other == "":
                other_expand_kwargs["mode"] = "constant"
            other = Str2D(data=other)

        height = max(self.height, other.height)
        left = self.expand(y=height - self.height)
        right = other.expand(y=height - other.height, **other_expand_kwargs)
        if right_side:
            left, right = right, left
        return Str2D(data=np.hstack((left.data, right.data)), **self.kwargs)

    def __radd__(self, other: "Str2D") -> "Str2D":
        """Add the data."""
        return self.__add__(other, right_side=True)

    def add(self, *args, **kwargs) -> "Str2D":
        """Add the data."""
        return Str2D.join_h(self, *args, **kwargs)

    def __mul__(self, other: int) -> "Str2D":
        """Multiply the data."""
        return Str2D(data=np.hstack([self.data] * other), **self.kwargs)

    def __rmul__(self, other: int) -> "Str2D":
        """Multiply the data."""
        return Str2D(data=np.vstack([self.data] * other), **self.kwargs)

    def __truediv__(self, other: "Str2D", right_side=False) -> "Str2D":
        """Divide the data."""
        other_expand_kwargs = {}
        if isinstance(other, str):
            other_expand_kwargs["mode"] = "edge"
            if other == "":
                other_expand_kwargs["mode"] = "constant"
            other = Str2D(data=other)

        width = max(self.width, other.width)
        left = self.expand(x=width - self.width)
        right = other.expand(x=width - other.width, **other_expand_kwargs)
        if right_side:
            left, right = right, left
        return Str2D(data=np.vstack((left.data, right.data)), **self.kwargs)

    def __rtruediv__(self, other: "Str2D") -> "Str2D":
        """Divide the data."""
        return self.__truediv__(other, right_side=True)

    def circle(self, radius, char="*"):
        """Create a circle."""
        c = circle(radius, self.height, self.width, char)
        return Str3D([c, self])

    def hole(self, radius, char="*"):
        """Create a hole."""
        c = hole(radius, self.height, self.width, char)
        return Str3D([c, self])

    def box_over(self, style):
        """Create a box over the data."""
        box = Box([self.height - 2], [self.width - 2], style)
        return Str3D([box, self])

    def box_around(self, style):
        """Create a box around the data."""
        s = self.pad(((1, 1), (1, 1)))
        box = Box([self.height], [self.width], style)
        return Str3D([box, s])

    def box(self, style="single_round", around=True):
        """Create a box around the data."""
        if around:
            return self.box_around(style)
        return self.box_over(style)

    def pi(self):
        """Replace the data with pi."""
        i, j = self.data["alpha"].nonzero()
        old_dps = mp.mp.dps
        n = len(i)
        mp.mp.dps = n
        self.data["char"][i, j] = [*str(mp.pi)][:n]
        mp.mp.dps = old_dps
        return self

    def hide(self, char=" "):
        """Hide the data."""
        data = self.data.copy()
        i, j = (data["char"] == char).nonzero()
        data["alpha"][i, j] = 0
        return Str2D(data=data, **self.kwargs)

    def div(self, *args, **kwargs) -> "Str2D":
        """Divide the data."""
        return Str2D.join_v(self, *args, **kwargs)

    def __str__(self) -> str:
        """Return the string representation of the data."""
        return "\n".join(["".join(row["char"]) for row in self.data])

    def __repr__(self) -> str:
        """Return the string representation of the data."""
        return str(self)

    # string operation methods that return a new Str2D object
    # ... and whose result is a new character array
    def lower(self) -> "Str2D":
        """Return the lowercase version of the data."""
        data = self.data.copy()
        data["char"] = np.char.lower(data["char"])
        return Str2D(data=data, **self.kwargs)

    def upper(self) -> "Str2D":
        """Return the uppercase version of the data."""
        data = self.data.copy()
        data["char"] = np.char.upper(data["char"])
        return Str2D(data=data, **self.kwargs)

    def replace(self, old, new) -> "Str2D":
        """Replace the data."""
        data = self.data.copy()
        data["char"] = np.char.replace(data["char"], old, new)
        return Str2D(data=data, **self.kwargs)

    def title(self) -> "Str2D":
        """Return the title version of the data."""
        data = self.data.copy()
        char = "".join(data["char"].ravel()).title()
        data["char"] = np.array(list(char)).reshape(data["char"].shape)
        return Str2D(data=data, **self.kwargs)

    def strip(self, *args, **kwargs) -> "Str2D":
        """Return the stripped version of the data."""
        data = self.data.copy()
        char = ["".join(row).strip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    def lstrip(self, *args, **kwargs) -> "Str2D":
        """Return the left stripped version of the data."""
        data = self.data.copy()
        char = ["".join(row).lstrip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    def rstrip(self, *args, **kwargs) -> "Str2D":
        """Return the right stripped version of the data."""
        data = self.data.copy()
        char = ["".join(row).rstrip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    # string operation methods that return a new Str2D object
    # ... and whose result is a new boolean array
    def isdigit(self) -> "Str2D":
        """Return whether the data is a digit."""
        data = self.data.copy()
        data["alpha"] = np.char.isdigit(data["char"]).astype("int8")
        return Str2D(data=data, **self.kwargs)

    def __eq__(self, other: Any) -> "Str2D":
        """Return whether the data is equal to the other data."""
        if isinstance(other, str):
            if len(other) == 1:
                return self.data["char"] == other
            return str(self) == other
        if isinstance(other, Str2D):
            return self.data["char"] == other.data["char"]
        raise ValueError("other must be a Str2D object or a scalar.")

    def __ne__(self, other: Any) -> "Str2D":
        """Return whether the data is not equal to the other data."""
        eq = self == other
        if isinstance(eq, bool):
            return not eq
        return ~eq

    def strip2d(self, char=" ") -> "Str2D":
        """Strip the data."""
        mask = self != char
        x0, x1 = np.flatnonzero(mask.any(axis=1))[[0, -1]]
        y0, y1 = np.flatnonzero(mask.any(axis=0))[[0, -1]]
        return self[x0 : x1 + 1, y0 : y1 + 1]

    def fill_with(self, char=" ") -> "Str2D":
        """Fill the data with a character."""
        kwargs = self.kwargs
        kwargs["fill"] = (char, 0)
        data = np.where(self.data["alpha"], self.data["char"], char)
        return Str2D(data=data, **kwargs)


class Box(Str2D):
    """Create a box around the data."""

    @staticmethod
    def spec_to_positions(spec):
        """Convert a specification to positions."""
        n = len(spec)
        a = np.arange(n) + 1
        b = np.add.accumulate(spec)
        return np.concatenate(([0], a + b))

    @staticmethod
    def spec_to_len(spec):
        """Convert a specification to length."""
        return sum(spec) + len(spec) + 1

    def __init__(
        self,
        spec_v: Optional[List[int]] = None,
        spec_h: Optional[List[int]] = None,
        style: Union[BoxStyle, str] = BoxStyle.SINGLE,
    ) -> Str2D:
        """Create a box around the data."""

        spec_v = [0] if spec_v is None else spec_v
        spec_h = [0] if spec_h is None else spec_h
        pos_v = self.spec_to_positions(spec_v)
        pos_h = self.spec_to_positions(spec_h)
        height = self.spec_to_len(spec_v)
        width = self.spec_to_len(spec_h)
        if isinstance(style, str):
            style = BoxStyle[style.upper()]
        chars = style.value

        self.spec_v = spec_v
        self.spec_h = spec_h
        self.style = style
        self.pos_v = pos_v
        self.pos_h = pos_h
        self.chars = chars

        data = np.empty((height, width), dtype=Str2D._dtype)
        data.fill((" ", 0))

        super().__init__(data)

        self.assign_box_char()

    def assign_box_char(self):
        """Assign the box characters."""

        data = self.data
        pos_v = self.pos_v
        pos_h = self.pos_h
        chars = self.chars

        data[:, pos_h] = (chars.v, 1)
        data[pos_v, :] = (chars.h, 1)

        data[0, pos_h] = (chars.t, 1)
        data[-1, pos_h] = (chars.b, 1)

        data[pos_v, 0] = (chars.l, 1)
        data[pos_v, -1] = (chars.r, 1)

        data[np.ix_(pos_v[1:-1], pos_h[1:-1])] = (chars.c, 1)

        pos_v_corners = [[0, 0], [-1, -1]]
        pos_h_corners = [[0, -1], [0, -1]]
        corners = [[(chars.ul, 1), (chars.ur, 1)], [(chars.ll, 1), (chars.lr, 1)]]
        data[pos_v_corners, pos_h_corners] = corners

        return self

    @cached_property
    def t(self):
        """Return the transpose of the data."""
        return Box(spec_v=self.spec_h, spec_h=self.spec_v, style=self.style)

    @cached_property
    def h(self):
        """Return the horizontal flip of the data."""
        return Box(spec_v=self.spec_v, spec_h=self.spec_h[::-1], style=self.style)

    @cached_property
    def v(self):
        """Return the vertical flip of the data."""
        return Box(spec_v=self.spec_v[::-1], spec_h=self.spec_h, style=self.style)

    @cached_property
    def r(self):
        """Return the 90 degree rotation of the data."""
        return self.t.h


class Str3D:
    """Manipulate 3D strings in Python."""

    def __init__(self, data):
        """Create a Str3D object."""
        self.source = data
        self.data = np.stack([datum.data for datum in data])

    def update(self):
        """Update the data."""
        self.data = np.stack([datum.data for datum in self.source])

    def __str__(self):
        """Return the string representation of the data."""
        return str(self.view)

    def __repr__(self):
        """Return the string representation of the data."""
        return str(self)

    @cached_property
    def t(self):
        """Return the transpose of the data."""
        return Str3D([datum.t for datum in self.source])

    @cached_property
    def h(self):
        """Return the horizontal flip of the data."""
        return Str3D([datum.h for datum in self.source])

    @cached_property
    def v(self):
        """Return the vertical flip of the data."""
        return Str3D([datum.v for datum in self.source])

    @cached_property
    def r(self):
        """Return the 90 degree rotation of the data."""
        return self.t.h

    @lru_cache
    def roll(self, *args, **kwargs) -> "Str3D":
        """Roll the data along an axis."""

        layer = kwargs.pop("layer", None)

        if layer is None:
            return Str3D([datum.roll(*args, **kwargs) for datum in self.source])

        if np.isscalar(layer):
            layer = [layer]

        return Str3D(
            [
                datum if i not in layer else datum.roll(*args, **kwargs)
                for i, datum in enumerate(self.source)
            ]
        )

    @property
    def view(self):
        """Return the view of the data."""
        argmax = self.data["alpha"].argmax(axis=0)
        _, height, width = self.data.shape
        y_indices, x_indices = np.ogrid[:height, :width]
        result = self.data[argmax, y_indices, x_indices]
        return Str2D(result)

    def __getattr__(self, name: str) -> Any:
        """Enables convenient access to the transpose, horizontal flip, vertical flip,
        and rotation methods in a concatenated manner.
        """
        if hasattr(self.view, name):
            return getattr(self.view, name)
        raise AttributeError(f"'{Str3D.__name__}' object has no attribute '{name}'")


def space(mn, mx, w):
    """Create a space."""
    if w < 1:
        raise ValueError(f"{w=} must be >= 1")

    a = np.linspace(mn, mx, w + 1)
    return a[:-1], (a[:-1] + a[1:]) / 2, a[1:]


def region(func, height, width, x_range, y_range):
    """Create a region."""
    _, center, _ = space(*x_range, width)
    _, middle, _ = space(*y_range[::-1], height)
    return func(center.reshape(1, -1), middle.reshape(-1, 1))


def boundary(func, height, width, x_range, y_range):
    """Create a boundary."""
    left, _, right = space(*x_range, width)
    bottom, _, top = space(*y_range[::-1], height)
    mask = np.stack(
        [
            func(left[None, :], top[:, None]),
            func(right[None, :], top[:, None]),
            func(right[None, :], bottom[:, None]),
            func(left[None, :], bottom[:, None]),
        ]
    )
    return mask.any(axis=0) & ~mask.all(axis=0)


def circle(radius, height, width, char="*"):
    """Create a circle."""
    height_limited = True
    if width < height * 2:
        height_limited = False

    if height_limited:
        y_range = np.array([-1, 1])
        x_range = width / height / 2 * y_range
    else:
        x_range = np.array([-1, 1])
        y_range = height * 2 / width * x_range

    mask = boundary(
        lambda x, y: x**2 + y**2 < radius**2, height, width, x_range, y_range
    )

    return Str2D(mask, char=char)


def hole(radius, height, width, char="*"):
    """Create a hole."""
    height_limited = True
    if width < height * 2:
        height_limited = False

    if height_limited:
        y_range = np.array([-1, 1])
        x_range = width / height / 2 * y_range
    else:
        x_range = np.array([-1, 1])
        y_range = height * 2 / width * x_range

    mask = region(
        lambda x, y: x**2 + y**2 <= radius**2, height, width, x_range, y_range
    )

    return Str2D(~mask, char=char)
