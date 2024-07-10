"""Manipulate 2D strings in Python."""

from functools import reduce, cached_property, lru_cache
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from textwrap import dedent
import uuid
from typing import List, Tuple, Union, Any, Optional
from pandas import DataFrame, Series
from IPython.display import HTML
import numpy as np
import mpmath as mp


@dataclass
class BoxParts:
    """Organizes box drawing characters.  Provides attribute names that are short and
    descriptive. This makes it easier to work with box drawing characters in code.

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
    """Enumerate different box styles. They can be used to draw boxes around text.  The
    box styles are made up of BoxParts objects that contain the box drawing characters.
    The main purpose of this class is to provide a way to apply box drawing over Str2D
    objects.

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

    ####################################################################
    # Construction methods #############################################
    ####################################################################

    @classmethod
    def validate_fill(
        cls, fill: Optional[Union[str, Tuple[str, int]]] = None
    ) -> Tuple[str, int]:
        """Validate the fill value.  The fill value is a tuple containing the fill
        character and fill alpha value.  The fill character is a single character and
        the fill alpha value is 0 or 1.  This validator will accept a single character
        or a tuple containing a single character and an integer.  If a single character
        is passed, the fill alpha value will be 0.  If a tuple is passed, the fill
        character will be the first element and the fill alpha value will be the second.

        Parameters
        ----------
        fill : Optional[Union[str, Tuple[str, int]]], optional
            The fill value, by default None

        Returns
        -------
        Tuple[str, int]
            A tuple containing the fill character and fill alpha value.

        Raises
        ------
        ValueError
            If the fill value is not a single character or a tuple containing a single
            character and an integer or if the fill alpha value is not 0 or 1.
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
        """Validate the horizontal alignment.  The horizontal alignment can be 'left',
        'center', or 'right'.  It will lower case the input and raise a ValueError if
        the input is not one of the valid options.

        Parameters
        ----------
        halign : str
            The horizontal alignment.

        Returns
        -------
        str
            The validated horizontal alignment.

        Raises
        ------
        ValueError
            If the horizontal alignment is not 'left', 'center', or 'right'.
        """
        halign = halign.lower()
        if halign not in {"left", "center", "right"}:
            raise ValueError("halign must be one of 'left', 'center', or 'right'.")
        return halign

    @classmethod
    def validate_valign(cls, valign: str) -> str:
        """Validate the vertical alignment. The vertical alignment can be 'top',
        'middle', or 'bottom'.  It will lower case the input and raise a ValueError if
        the input is not one of the valid options.

        Parameters
        ----------
        valign : str
            The vertical alignment.

        Returns
        -------
        str
            The validated vertical alignment.

        Raises
        ------
        ValueError
            If the vertical alignment is not 'top', 'middle', or 'bottom'.
        """
        valign = valign.lower()
        if valign not in {"top", "middle", "bottom"}:
            raise ValueError("valign must be one of 'top', 'middle', or 'bottom'.")
        return valign

    @classmethod
    def struct_array_from_string(cls, string: str, **kwargs) -> "Str2D":
        """Create a structured array from a string.  This is likely the most common way
        to create an Str2D object.  The string is split into lines and then each line is
        split into characters.  The structured array is created with fields 'char' and
        'alpha' where the 'char' field contains the characters and the 'alpha' field
        contains 1 for each character.

        Though we aren't returning a Str2D object, we are returning a structured array
        that potentially needs to be padded and therefore we take the same keyword
        arguments as the Str2D constructor.

        Parameters
        ----------
        string : str
            A string to convert to a structured array.

        min_width : int, optional
            The minimum width of the output, by default 0.

        min_height : int, optional
            The minimum height of the output, by default 0.

        halign : str, optional
            The horizontal alignment, by default 'left'.

        valign : str, optional
            The vertical alignment, by default 'top'.

        fill : Tuple[str, int], optional
            The fill value for the 'char' and 'alpha' fields, by default (' ', 0).

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
        """Create a structured array from a character array.  This is useful when you
        have a 2D array of characters and you want to convert it to a structured array
        with fields 'char' and 'alpha'.

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
        """Create a structured array from a boolean array. This is useful when you have
        a boolean array and you want to convert it to a structured array with fields
        'char' and 'alpha'.

        The 'char' field will be filled with the specified character where the boolean
        array is True and ' ' where the boolean array is False.  The 'alpha' field will
        be 1 where the boolean array is True and 0 where the boolean array is False.

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
        """Parse the input data into a structured array.  This is the main method that
        will take the input data and convert it into a structured array with fields
        'char' and 'alpha'.  The input data can be a string, a structured array, a
        boolean array, a DataFrame, a Series, or an iterable.  If the input data is a
        structured array, the keyword arguments will be ignored.

        Parameters
        ----------
        data : Optional[Any], optional
            The input data, by default None.

        kwargs : dict
            Additional keyword arguments to pass to the struct_array_from_string method.
            If the input data is a structured array, these keyword arguments will be
            ignored.

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
        """Create a new Str2D object.  The input data can be a string, a structured
        array, a boolean array, a DataFrame, a Series, or an iterable.  If the input
        data is a structured array, the keyword arguments will be ignored.

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
            If the fill, horizontal alignment, or vertical alignment value is invalid.

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

    ####################################################################
    # Math Operations ##################################################
    ####################################################################

    def __bool__(self) -> bool:
        """Return True if the Str2D object has any characters."""
        return self.shape != (0, 0)

    def __add__(self, other: Union["Str2D", str], right_side=False) -> "Str2D":
        """Adding one Str2D object to another or a string to a Str2D object is the main
        point of this class.  We can add a Str2D object to another Str2D object in order
        to concatenate them horizontally.  Both objects will be expanded to have the
        same height while respecting the alignment parameters.  When adding a string to
        a Str2D object, the string will be wrapped in a Str2D object and treated as
        described above.  In the case of adding another Str2D object, the expansion will
        use the expansion argument `'mode'` set to `'edge'`.  This allows the expansion
        to repeat the string intuitively to the edge of the Str2D object.

        Parameters
        ----------
        other : Union[Str2D, str]
            The Str2D object or string to add.

        right_side : bool, optional
            If True, the Str2D object will be added to the right side of the
            other Str2D object, by default False.

        Returns
        -------
        Str2D
            A new Str2D object with the added data.

        See Also
        --------
        add : Add the data.
        __add__ : Add the data.
        __radd__ : Add the data.
        add : Add the data.

        Examples
        --------
        Let's create several instances of Str2D and assign them to the variables `a`,
        `b`, and `c`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            b = Str2D('1 2 3\\n4 5 6\\n7 8 9')
            c = Str2D('x y z\\nu v w\\nq r s')

        We can add the data horizontally by using the Str2D objects with the `+`
        operator.

        .. testcode::

            a + b + c

        .. testoutput::

            a b c d1 2 3x y z
            e f g  4 5 6u v w
            h i    7 8 9q r s
            j

        We can also add a string to the Str2D object.

        .. testcode::

            a + ' hello ' + c

        .. testoutput::

            a b c d hello x y z
            e f g   hello u v w
            h i     hello q r s
            j       hello

        From the right side.

        .. testcode::

            'hello ' + a

        .. testoutput::

            hello a b c d
            hello e f g
            hello h i
            hello j

        """
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
        """Dunder method handling the right side of the addition operation."""
        return self.__add__(other, right_side=True)

    __radd__.__doc__ += __add__.__doc__

    def add(self, *args, **kwargs) -> "Str2D":
        """Public method for adding the data without the need to use the `+` operator.
        We use the `join_h` method to concatenate the data horizontally with additional
        arguments.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to add.

        kwargs : dict
            Additional keyword arguments to pass to the `join_h` method.

        Returns
        -------
        Str2D
            A new Str2D object with the added data.

        See Also
        --------
        __add__ : Add the data.
        __radd__ : Add the data.
        add : Add the data.

        """
        return Str2D.join_h(self, *args, **kwargs)

    def __mul__(self, other: int) -> "Str2D":
        """It doesn't make sense to multiply a Str2D object by another Str2D object.
        However, we can multiply a Str2D object by an integer.  This will repeat the
        data equal to the integer value.  The direction of the repetition is determined
        by the side of the Str2D object that the integer is on.  If the integer is on
        the left side, the data will be repeated vertically.  If the integer is on the
        right side, the data will be repeated horizontally.

        Parameters
        ----------
        other : int
            The number of times to repeat the data.

        Returns
        -------
        Str2D
            A new Str2D object with the repeated data.

        See Also
        --------
        __rmul__ : Multiply the data.
        __mul__ : Multiply the data.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can multiply the data by multiplying by an integer on the right side.

        .. testcode::

            a * 2

        .. testoutput::

            a b c da b c d
            e f g  e f g
            h i    h i
            j      j

        We can also multiply the data by multiplying by an integer on the left side.

        .. testcode::

            2 * a

        .. testoutput::

            a b c d
            e f g
            h i
            j
            a b c d
            e f g
            h i
            j


        """
        return Str2D(data=np.hstack([self.data] * other), **self.kwargs)

    def __rmul__(self, other: int) -> "Str2D":
        return Str2D(data=np.vstack([self.data] * other), **self.kwargs)

    __rmul__.__doc__ = __mul__.__doc__

    def __truediv__(self, other: Union["Str2D", str], right_side=False) -> "Str2D":
        """Division is the vertical analog of the addition operation.  We can divide a
        Str2D object by another Str2D object in order to concatenate them vertically.
        Both objects will be expanded to have the same width while respecting the
        alignment parameters.  When dividing by str object, the expansion will use the
        expansion argument `'mode'` set to `'edge'`.  This allows the expansion to
        repeat the string intuitively to the edge of the Str2D object.

        Parameters
        ----------
        other : Union[Str2D, str]
            The Str2D object or string to divide.

        right_side : bool, optional
            If True, the Str2D object will be below the other Str2D object, by default
            False.

        Returns
        -------
        Str2D
            A new Str2D object with the divided data.

        See Also
        --------
        __truediv__ : Divide the data.
        __rtruediv__ : Divide the data.
        div : Divide the data.

        Examples
        --------
        Let's create several instances of Str2D and assign them to the variables `a`,
        `b`, and `c`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            b = Str2D('1 2 3\\n4 5 6\\n7 8 9')
            c = Str2D('x y z\\nu v w\\nq r s')

        We can divide the data vertically by using the Str2D objects with the `/`

        .. testcode::

            a / b / c

        .. testoutput::

            a b c d
            e f g
            h i
            j
            1 2 3
            4 5 6
            7 8 9
            x y z
            u v w
            q r s

        We can also divide by a string.

        .. testcode::

            a / '-' / c

        .. testoutput::

            a b c d
            e f g
            h i
            j
            -------
            x y z
            u v w
            q r s

        From the right side.

        .. testcode::

            '-' / a

        .. testoutput::

            -------
            a b c d
            e f g
            h i
            j

        """
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
        return self.__truediv__(other, right_side=True)

    __rtruediv__.__doc__ = __truediv__.__doc__

    def div(self, *args, **kwargs) -> "Str2D":
        """Public method for dividing the data without the need to use the `/` operator.
        We use the `join_v` method to concatenate the data vertically with additional
        arguments.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to divide.

        kwargs : dict
            Additional keyword arguments to pass to the `join_v` method.

        Returns
        -------
        Str2D
            A new Str2D object with the divided data.

        See Also
        --------
        __truediv__ : Divide the data.
        __rtruediv__ : Divide the data.
        div : Divide the data.

        """
        return Str2D.join_v(self, *args, **kwargs)

    ####################################################################
    # Class methods ####################################################
    ####################################################################

    @classmethod
    def struct_pad(cls, array, *args, **kwargs) -> "Str2D":
        """Pads a structured array with fields 'char' and 'alpha'.  The
        method is a wrapper around np.pad that pads the 'char' and 'alpha' fields with
        the fill value specified in the 'fill' keyword argument.

        Parameters
        ----------
        array : np.ndarray
            A structured array with fields 'char' and 'alpha'.

        mode: str, optional
            The padding mode, by default 'constant'.  Other options are documented in
            np.pad but the only other one that makes sense in a character array context
            is 'edge'.

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

        Another thing we can do is to pass a different type of padding mode.  The
        default is 'constant' which will fill the padding elements with the fill value.
        However, we can also use 'edge' which will fill the padding elements with the
        nearest edge value.

        .. testcode::

            Str2D.struct_pad(a.data, 1, mode='edge')

        .. testoutput::

            array([['a', 'a', ' ', 'b', ' ', 'c', ' ', 'd', 'd'],
                   ['a', 'a', ' ', 'b', ' ', 'c', ' ', 'd', 'd'],
                   ['e', 'e', ' ', 'f', ' ', 'g', ' ', ' ', ' '],
                   ['h', 'h', ' ', 'i', ' ', ' ', ' ', ' ', ' '],
                   ['j', 'j', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
                   ['j', 'j', ' ', ' ', ' ', ' ', ' ', ' ', ' ']], dtype='<U1')

        """
        # Using `np.pad` on structured arrays is a bit tricky because it doesn't
        # handle the structured array fields very well.  We need to pad the 'char'
        # and 'alpha' fields separately and then recombine them into a structured
        # array.
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
    def join_h(cls, *args: "Str2D", sep: str = "") -> "Str2D":
        """`join_h` joins any number of Str2D objects horizontally.  The `sep` is the
        separator that will be added between the joined data.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to join horizontally.

        sep : str, optional
            The separator to insert between the joined data, by default ''.

        Returns
        -------
        Str2D
            A new Str2D object with the joined data.

        See Also
        --------
        join_v : Join the data vertically

        Examples
        --------
        Let's create several instances of Str2D and assign them to the variables `a`,
        `b`, and `c`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            b = Str2D('1 2 3\\n4 5 6\\n7 8 9')
            c = Str2D('x y z\\nu v w\\nq r s')

        We can join the data horizontally by passing the Str2D objects to the `join_h`
        method.

        .. testcode::

            Str2D.join_h(a, b, c)

        .. testoutput::

            a b c d1 2 3x y z
            e f g  4 5 6u v w
            h i    7 8 9q r s
            j

        We can also pass a separator

        .. testcode::

            Str2D.join_h(a, b, c, sep='|')

        .. testoutput::

            a b c d|1 2 3|x y z
            e f g  |4 5 6|u v w
            h i    |7 8 9|q r s
            j      |     |

        """
        if sep:
            args = sum(zip([sep] * len(args), args), ())[1:]
        return reduce(lambda x, y: x + y, args)

    @classmethod
    def join_v(cls, *args: "Str2D", sep: str = "") -> "Str2D":
        """`join_v` joins any number of Str2D objects vertically.  The `sep` is the
        separator that will be added between the joined data.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to join vertically.

        sep : str, optional
            The separator to insert between the joined data, by default ''.

        Returns
        -------
        Str2D
            A new Str2D object with the joined data.

        See Also
        --------
        join_h : Join the data horizontally.

        Examples
        --------
        Let's create several instances of Str2D and assign them to the variables `a`,
        `b`, and `c`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            b = Str2D('1 2 3\\n4 5 6\\n7 8 9')
            c = Str2D('x y z\\nu v w\\nq r s')

        We can join the data vertically by passing the Str2D objects to the `join_v`

        .. testcode::

            Str2D.join_v(a, b, c)

        .. testoutput::

            a b c d
            e f g
            h i
            j
            1 2 3
            4 5 6
            7 8 9
            x y z
            u v w
            q r s

        We can also pass a separator

        .. testcode::

            Str2D.join_v(a, b, c, sep='-')

        .. testoutput::

            a b c d
            e f g
            h i
            j
            -------
            1 2 3
            4 5 6
            7 8 9
            -------
            x y z
            u v w
            q r s

        """
        if sep:
            args = sum(zip([sep] * len(args), args), ())[1:]
        if args:
            return reduce(lambda x, y: x / y, args)
        return Str2D()

    @classmethod
    def equal_height(cls, *args: "Str2D") -> List["Str2D"]:
        """Expand each Str2D object to have the same height.  Useful for when you want
        all Str2D objects to have the same height.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to expand.

        Returns
        -------
        List[Str2D]
            A list of Str2D objects with the same height.

        """
        max_height = max(arg.height for arg in args)
        return [arg.expand(y=max_height - arg.height) for arg in args]

    @classmethod
    def equal_width(cls, *args: "Str2D") -> List["Str2D"]:
        """Expand each Str2D object to have the same width.  Useful for when you want
        all Str2D objects to have the same width.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to expand.

        Returns
        -------
        List[Str2D]
            A list of Str2D objects with the same width.

        """
        max_width = max(arg.width for arg in args)
        return [arg.expand(x=max_width - arg.width) for arg in args]

    @classmethod
    def equal_shape(cls, *args: "Str2D") -> List["Str2D"]:
        """Expand each Str2D object to have the same shape.  Useful for when you want
        all Str2D objects to have the same shape.

        Parameters
        ----------
        args : Tuple[Str2D]
            The Str2D objects to expand.

        Returns
        -------
        List[Str2D]
            A list of Str2D objects with the same shape.

        """
        max_height = max(arg.height for arg in args)
        max_width = max(arg.width for arg in args)
        return [
            arg.expand(x=max_width - arg.width, y=max_height - arg.height)
            for arg in args
        ]

    ####################################################################
    # Attribute properties #############################################
    ####################################################################

    @property
    def height(self) -> int:
        """Return the height of the Str2D object.  This is the number of rows in the
        structured array or the number of lines in the string."""
        return self.data.shape[0]

    @property
    def width(self) -> int:
        """Return the width of the Str2D object.  This is the number of columns in the
        structured array or the maximum number of characters in a line in the string."""
        return self.data.shape[1]

    @property
    def shape(self) -> Tuple[int, int]:
        """Return the shape of the Str2D object.  This is a tuple containing the height
        and width of the structured array."""
        return self.data.shape

    @property
    def char(self) -> np.ndarray:
        """Return the character data.  Alternatively, you can access the 'char' field
        directly by using the 'data' attribute and the 'char' key.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can access the 'char' field directly by using the 'data' attribute and the

        .. testcode::

            a.data['char']

        .. testoutput::

            array([['a', ' ', 'b', ' ', 'c', ' ', 'd'],
                   ['e', ' ', 'f', ' ', 'g', ' ', ' '],
                   ['h', ' ', 'i', ' ', ' ', ' ', ' '],
                   ['j', ' ', ' ', ' ', ' ', ' ', ' ']], dtype='<U1')

        This property is a shortcut to the above.

        .. testcode::

            a.char

        .. testoutput::

            array([['a', ' ', 'b', ' ', 'c', ' ', 'd'],
                   ['e', ' ', 'f', ' ', 'g', ' ', ' '],
                   ['h', ' ', 'i', ' ', ' ', ' ', ' '],
                   ['j', ' ', ' ', ' ', ' ', ' ', ' ']], dtype='<U1')

        """
        return self.data["char"]

    @property
    def alpha(self) -> np.ndarray:
        """Return the alpha data.  Alternatively, you can access the 'alpha' field
        directly by using the 'data' attribute and the 'alpha' key.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can access the 'alpha' field directly by using the 'data' attribute and the

        .. testcode::

            a.data['alpha']

        .. testoutput::

            array([[1, 1, 1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1, 0, 0],
                   [1, 1, 1, 0, 0, 0, 0],
                   [1, 0, 0, 0, 0, 0, 0]], dtype=int8)

        This property is a shortcut to the above.

        .. testcode::

            a.alpha

        .. testoutput::

            array([[1, 1, 1, 1, 1, 1, 1],
                   [1, 1, 1, 1, 1, 0, 0],
                   [1, 1, 1, 0, 0, 0, 0],
                   [1, 0, 0, 0, 0, 0, 0]], dtype=int8)

        """
        return self.data["alpha"]

    @property
    def kwargs(self) -> dict:
        """Return the keyword arguments used to create the Str2D object.  This is a
        dictionary containing the 'halign', 'valign', and 'fill' values.

        The purpose of this property is to make it easier to recreate the Str2D object
        with the same settings, helping persist the state of the object as it
        transforms.
        """
        return {
            "halign": self.halign,
            "valign": self.valign,
            "fill": self.fill,
        }

    ####################################################################
    # Transformations ##################################################
    ####################################################################

    TRANSFORMATIONS_DOCSTRING = """

        This is one of 5 transformations that can be done to the Str2D object.

        - `i` is the identity transformation of the data.
        - `t` is the transpose of the data.
        - `h` is the horizontal flip of the data.
        - `v` is the vertical flip of the data.
        - `r` is the 90 degree clockwise rotation of the data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('ab\\ncd')
            a

        .. testoutput::

            ab
            cd

        Notice that this is a 2x2 array.  We'll show each of the transformations and 
        intentionally expand and box them to show how the transformations affect the
        alignment.
    
        .. testcode::

            a.transormation_palette()

        .. testoutput::

               i    |    t    |    h     |     v     |    r     |    r2     |    r3    
            ╭────╮  | ╭────╮  |  ╭────╮  |  ╭────╮   |  ╭────╮  |  ╭────╮   |  ╭────╮  
            │ab  │  | │ac  │  |  │  ba│  |  │    │   |  │  ca│  |  │    │   |  │    │  
            │cd  │  | │bd  │  |  │  dc│  |  │    │   |  │  db│  |  │    │   |  │    │  
            │    │  | │    │  |  │    │  |  │cd  │   |  │    │  |  │  dc│   |  │bd  │  
            │    │  | │    │  |  │    │  |  │ab  │   |  │    │  |  │  ba│   |  │ac  │  
            ╰────╯  | ╰────╯  |  ╰────╯  |  ╰────╯   |  ╰────╯  |  ╰────╯   |  ╰────╯  
            ------- | ------- | -------- | --------- | -------- | --------- | ---------
            v: top  | v: top  | v: top   | v: bottom | v: top   | v: bottom | v: bottom
            h: left | h: left | h: right | h: left   | h: right | h: right  | h: left  

        Lastly, we can chain the transformations together.

        .. testcode::

            a.thirvt

        .. testoutput::

            bd
            ac        

    """

    @cached_property
    def t(self) -> "Str2D":
        """Return the transpose of the Str2D object."""
        return Str2D(
            data=self.data.T,
            halign=self._align_transpose[self.valign],
            valign=self._align_transpose[self.halign],
            fill=self.fill,
        )

    t.__doc__ += TRANSFORMATIONS_DOCSTRING

    @cached_property
    def i(self) -> "Str2D":
        """This is the identity transformation.  It returns the Str2D object as is."""
        return self

    i.__doc__ += TRANSFORMATIONS_DOCSTRING

    @cached_property
    def h(self) -> "Str2D":
        """Return the horizontal flip of the data."""
        return Str2D(
            data=np.fliplr(self.data),
            halign=self._align_horizontal[self.halign],
            valign=self.valign,
            fill=self.fill,
        )

    h.__doc__ += TRANSFORMATIONS_DOCSTRING

    @cached_property
    def v(self) -> "Str2D":
        """Return the vertical flip of the data."""
        return Str2D(
            data=np.flipud(self.data),
            halign=self.halign,
            valign=self._align_vertical[self.valign],
            fill=self.fill,
        )

    v.__doc__ += TRANSFORMATIONS_DOCSTRING

    @cached_property
    def r(self) -> "Str2D":
        """Return the 90 degree rotation of the data."""
        return self.t.h

    r.__doc__ += TRANSFORMATIONS_DOCSTRING

    def __getattr__(self, name: str) -> Any:
        """Enables convenient access to the transpose, horizontal flip, vertical flip,
        and rotation methods in a concatenated manner.
        """
        if (p := name[0].lower()) in ["h", "v", "t", "r", "i"]:
            this = getattr(self, p)
            if len(name) == 1:
                return this
            return getattr(getattr(self, p), name[1:])
        raise AttributeError(f"'{Str2D.__name__}' object has no attribute '{name}'")

    __getattr__.__doc__ += TRANSFORMATIONS_DOCSTRING

    ####################################################################
    # Information/Documentation ########################################
    ####################################################################

    def reshape(self, shape: Tuple[int, int]) -> "Str2D":
        """Reshape the Str2D object.  This is a wrapper around the `reshape` method of
        the structured array.

        Parameters
        ----------
        shape : Tuple[int, int]
            The new shape of the Str2D object.

        Returns
        -------
        Str2D
            A new Str2D object with the reshaped data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')
            a

        .. testoutput::

            a b c d
            e f g
            h i
            j

        We can reshape the Str2D object to have a shape of (2, 8).

        .. testcode::

            a.reshape((1, -1))

        .. testoutput::

            a b c de f g  h i    j

        """
        return Str2D(data=self.data.reshape(shape), **self.kwargs)

    def show_with_alignment(self, expand=2, box=True) -> "Str2D":
        """Show the alignment parameters with object.
        This is useful for debugging and understanding how the alignment parameters
        affect the output.

        Parameters
        ----------
        expand : int, optional
            The amount to expand the Str2D object, by default 2.

        box : bool, optional
            Whether to box the Str2D object, by default True.

        Returns
        -------
        Str2D
            A new Str2D object with the alignment parameters displayed as text.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can show the alignment parameters as part of a new Str2D object.

        .. testcode::

            a.show_with_alignment()

        .. testoutput::

            ╭─────────╮
            │a b c d  │
            │e f g    │
            │h i      │
            │j        │
            │         │
            │         │
            ╰─────────╯
            -----------
            v: top
            h: left

        """
        footer = Str2D(f"v: {self.valign}\nh: {self.halign}")
        body = self
        if expand:
            body = body.expand(expand, expand)
        if box:
            body = body.box().view

        body = Str2D(body, valign="middle", halign="center")

        sep = Str2D("-" * max(body.width, footer.width))
        return body / sep / footer

    def transormation_palette(self, sep=" | ", expand=2, box=True) -> "Str2D":
        """Show the transformation palette.  This is a visual representation of the
        identity, transpose, horizontal flip, vertical flip, and 90 degree rotation of
        the data.  The transformations are shown with alignment parameters and can be
        expanded and boxed.

        Parameters
        ----------
        sep : str, optional
            The separator between the transformations, by default ' | '.

        expand : int, optional
            The amount to expand the Str2D object, by default 2.

        box : bool, optional
            Whether to box the Str2D object, by default True.

        See Also
        --------
        show_with_alignment : Show the alignment parameters as part of a new Str2D
            object.

        Returns
        -------
        Str2D
            A new Str2D object with the transformations displayed.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('ab\\ncd')

        We can show the transformation palette.

        .. testcode::

            a.transormation_palette()

        .. testoutput::

               i    |    t    |    h     |     v     |    r     |    r2     |    r3
            ╭────╮  | ╭────╮  |  ╭────╮  |  ╭────╮   |  ╭────╮  |  ╭────╮   |  ╭────╮
            │ab  │  | │ac  │  |  │  ba│  |  │    │   |  │  ca│  |  │    │   |  │    │
            │cd  │  | │bd  │  |  │  dc│  |  │    │   |  │  db│  |  │    │   |  │    │
            │    │  | │    │  |  │    │  |  │cd  │   |  │    │  |  │  dc│   |  │bd  │
            │    │  | │    │  |  │    │  |  │ab  │   |  │    │  |  │  ba│   |  │ac  │
            ╰────╯  | ╰────╯  |  ╰────╯  |  ╰────╯   |  ╰────╯  |  ╰────╯   |  ╰────╯
            ------- | ------- | -------- | --------- | -------- | --------- | ---------
            v: top  | v: top  | v: top   | v: bottom | v: top   | v: bottom | v: bottom
            h: left | h: left | h: right | h: left   | h: right | h: right  | h: left

        """

        i = self.i.show_with_alignment(expand=expand, box=box)
        t = self.t.show_with_alignment(expand=expand, box=box)
        h = self.h.show_with_alignment(expand=expand, box=box)
        v = self.v.show_with_alignment(expand=expand, box=box)
        r = self.r.show_with_alignment(expand=expand, box=box)
        rr = self.rr.show_with_alignment(expand=expand, box=box)
        rrr = self.rrr.show_with_alignment(expand=expand, box=box)

        return self.join_h(
            Str2D("i", halign="center") / i,
            Str2D("t", halign="center") / t,
            Str2D("h", halign="center") / h,
            Str2D("v", halign="center") / v,
            Str2D("r", halign="center") / r,
            Str2D("r2", halign="center") / rr,
            Str2D("r3", halign="center") / rrr,
            sep=sep,
        )

    def pre(self, **kwargs) -> HTML:
        """Return HTML prefformatted text.  This is useful for displaying the Str2D
        with different style settings in Jupyter notebooks.

        Parameters
        ----------
        font_size : int, optional
            The font size, by default 1.

        Returns
        -------
        HTML
            The HTML preformatted text.
        """
        return pre(self, **kwargs)

    ####################################################################
    # Methods ##########################################################
    ####################################################################

    def roll(self, x: int, axis: int) -> "Str2D":
        """Roll the data along an axis.  Analogous and wrapper to np.roll.

        Parameters
        ----------
        x : int
            The number of positions to roll.
        axis : int
            The axis to roll along.

        Returns
        -------

        Str2D

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can roll the data horizontally by passing the number of positions to roll and
        the axis equal to 1.

        .. testcode::

            a.roll(1, axis=1)

        .. testoutput::

            da b c
             e f g
             h i
             j

        We can roll the data vertically by passing the number of positions to roll and
        the axis equal to 0.

        .. testcode::

            a.roll(1, axis=0)

        .. testoutput::

            j
            a b c d
            e f g
            h i

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
        Str2D

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can roll the data horizontally by passing the number of positions to roll.

        .. testcode::

            a.roll_h(1)

        .. testoutput::

            da b c
             e f g
             h i
             j

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
        Str2D

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can roll the data vertically by passing the number of positions to roll.

        .. testcode::

            a.roll_v(1)

        .. testoutput::

            j
            a b c d
            e f g
            h i

        """
        return self.roll(x, axis=0)

    def pad(self, *args, **kwargs) -> "Str2D":
        """`pad` pads the data with the fill value specified in the 'fill' keyword and
        is a wrapper around the class method `struct_pad` which in turn is a wrapper
        around np.pad.

        Parameters
        ----------
        fill : Tuple[str, int], optional
            The fill value for the 'char' and 'alpha' fields, by default (' ', 0)

        mode: str, optional
            The padding mode, by default 'constant'.  Other options are documented in
            np.pad but the only other one that makes sense in a character array context
            is 'edge'.

        args : tuple
            Positional arguments to np.pad.

        kwargs : dict
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

        Another thing we can do is to pass a different type of padding mode.  The
        default is 'constant' which will fill the padding elements with the fill value.
        However, we can also use 'edge' which will fill the padding elements with the
        nearest edge value.

        .. testcode::

            a.pad(1, mode='edge')

        .. testoutput::

            aa b c dd
            aa b c dd
            ee f g
            hh i
            jj
            jj

        """
        kwargs.setdefault("fill", self.fill)
        padded_data = self.struct_pad(self.data, *args, **kwargs)

        return Str2D(data=padded_data, **self.kwargs)

    def expand(self, x: int = 0, y: int = 0, **kwargs) -> "Str2D":
        """The `expand` method expands the data by adding padding to the top, bottom,
        left, and right of the data.  This is a wrapper around the `pad` method where
        we take into account the alignment parameters and adjust the padding
        accordingly.

        Parameters
        ----------
        x : int, optional
            The number of columns to expand, by default 0.

        y : int, optional
            The number of rows to expand, by default 0.

        kwargs : dict
            Additional keyword arguments to pass to the pad method.


        Returns
        -------
        Str2D
            A new Str2D object with the expanded data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then
        expand it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('a b c d\\ne f g\\nh i\\nj')

        We can expand the data by passing the number of columns and rows to expand.  In
        order to see the expansion, we'll use a fill value of '.'.

        .. testcode::

            a.expand(1, 1, fill='.')

        .. testoutput::

            a b c d.
            e f g  .
            h i    .
            j      .
            ........

        Let's see what happens when the alignment is set to 'center' and 'middle'.  We
        use an `x` value of 4 and a `y` value of 2 to add 4 columns and 2 rows.

        .. testcode::

            a = Str2D(
                'a b c d\\ne f g  \\nh i    \\nj      ',
                valign='middle', halign='center'
            )

            a.expand(4, 2, fill='.')

            ...........
            ..a b c d..
            ..e f g  ..
            ..h i    ..
            ..j      ..
            ...........

        """
        kwargs["fill"] = self.validate_fill(kwargs.get("fill", self.fill))
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

    def split(self, indices_or_sections, axis=0) -> List["Str2D"]:
        """`split` is analogous to np.split and splits the data along an axis.  It'll
        return a list of Str2D objects split along the specified axis at the specified
        indices.

        The `ary` being passed to `np.split` is the structured array data.

        Parameters
        ----------
        indices_or_sections : int or 1-D array
            If `indices_or_sections` is an integer, N, the array will be divided
            into N equal arrays along `axis`.  If such a split is not possible,
            an error is raised.

            If `indices_or_sections` is a 1-D array of sorted integers, the entries
            indicate where along `axis` the array is split.  For example,
            ``[2, 3]`` would, for ``axis=0``, result in

            - ary[:2]
            - ary[2:3]
            - ary[3:]

            If an index exceeds the dimension of the array along `axis`,
            an empty sub-array is returned correspondingly.

        axis : int, optional
            The axis along which to split, default is 0.

        Returns
        -------
        List[Str2D]
            A list of Str2D applied to the split data.

        Raises
        ------
        ValueError
            If `indices_or_sections` is given as an integer, but
            a split does not result in equal division.

        See Also
        --------
        insert : Insert a separator between the split data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then
        split it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        We can split the data into 3 equal parts along the vertical axis.  We'll use the
        complementary `insert` method to join the split data back together to help
        visualize the split.

        Two equal parts along the vertical axis.
        .. testcode::

            a.split(2)

        .. testoutput::

            [abcdef
            ghijkl,
            mnopqr
            stuvwx]

        Using the `insert` method to join the split data back together.

        .. testcode::

            a.insert(2)

        .. testoutput::

            abcdef
            ghijkl

            mnopqr
            stuvwx

        3 equal parts along the horizontal axis.
        Remember that we're using the `insert` method to show the data.  Use the `split`
        method to get the split data as a list.

        .. testcode::

            a.insert(3, axis=1)

        .. testoutput::

            ab cd ef
            gh ij kl
            mn op qr
            st uv wx

        Split the data at first and fifth columns.

        .. testcode::

            a.insert([1, 5], axis=1)

        .. testoutput::

            a bcde f
            g hijk l
            m nopq r
            s tuvw x

        """
        return [
            Str2D(data=divided, **self.kwargs)
            for divided in np.split(self.data, indices_or_sections, axis)
        ]

    def insert(self, indices_or_sections, axis=0, sep=" "):
        """`insert` is a wrapper around the `split` method and is used to visually
        insert a separator between the split data.  The `sep` is the separator that will
        be added between the split data.

        If the `sep` is not an empty string, it will be added between the concatenated
        data. If the `sep` is an empty string, the data will be concatenated without any
        separation and wll resemble the original data.  This would be silly to do but
        it's a good way to indicate that the method is doing what it's supposed to do.

        The actual intention is to use a separator to visually separate the data.

        The `ary` being passed to `np.split` is the structured array data.

        Parameters
        ----------
        indices_or_sections : int or 1-D array
            If `indices_or_sections` is an integer, N, the array will be divided
            into N equal arrays along `axis`.  If such a split is not possible,
            an error is raised.

            If `indices_or_sections` is a 1-D array of sorted integers, the entries
            indicate where along `axis` the array is split.  For example,
            ``[2, 3]`` would, for ``axis=0``, result in

            - ary[:2]
            - ary[2:3]
            - ary[3:]

            If an index exceeds the dimension of the array along `axis`,
            an empty sub-array is returned correspondingly.

        axis : int, optional
            The axis along which to split, default is 0.

        sep : str, optional
            The separator to insert between the split data, by default ' '.

        Returns
        -------
        Str2D
            A new Str2D object with the split data and separator.

        See Also
        --------
        split : Split the data along an axis.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        Let's `insert` 4 equal parts along the vertical axis with a separator of '-'
        followed by an `insert` of 3 equal parts along the horizontal axis with a
        separator of '|'.

        .. testcode::

            a.insert(4, sep='-').insert(3, axis=1, sep='|')

        .. testoutput::

            ab|cd|ef
            --|--|--
            gh|ij|kl
            --|--|--
            mn|op|qr
            --|--|--
            st|uv|wx

        """
        if axis == 0:
            return Str2D.join_v(*self.split(indices_or_sections, axis=axis), sep=sep)
        return Str2D.join_h(*self.split(indices_or_sections, axis=axis), sep=sep)

    def __getitem__(
        self,
        key: Union[int, slice, Tuple[Union[int, slice], ...], List[Union[int, slice]]],
    ) -> "Str2D":
        """Passing on the indexing to the structured array data.  This is a wrapper
        around the structured array data's __getitem__ method and returns a new Str2D
        object with the sliced data.

        Parameters
        ----------
        key : Union[int, slice, Tuple[Union[int, slice], ...], List[Union[int, slice]]
            The index or slice to pass to the structured array data.

        Returns
        -------
        Str2D
            A new Str2D object with the sliced data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a`.

        .. testcode::

            from str2d import Str2D

            a = Str2D('''\\
            012345
            123450
            234501
            345012
            ''')
            a
        .. testoutput::

            012345
            123450
            234501
            345012

        We can slice the data by passing a tuple of slices.  The first slice is for the
        rows and the second slice is for the columns.

        .. testcode::

            a[:-2, 1:]

        .. testoutput::

            12345
            23450
        
        """
        if isinstance(key, tuple):
            new_key = tuple(([k] if np.isscalar(k) else k) for k in key)
        elif np.isscalar(key):
            new_key = [key]
        else:
            new_key = key

        return Str2D(data=self.data[new_key], **self.kwargs)

    def circle(self, radius: float, char: str = "*") -> "Str3D":
        """Create a circle over object. This is a wrapper around the `circle` function
        and returns a new Str3D object with the circle over the data.

        Parameters
        ----------
        radius : float
            The radius of the circle.  The minimum of the height and width of the data
            is used as a reference for the radius equal to 1.

        char : str, optional
            The character to use for the circle, by default '*'.

        Returns
        -------
        Str3D
            A new Str3D object with the circle over the data.

        See Also
        --------
        hole : Create a hole over the data.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then

        .. testcode::

            from str2d import Str2D

            a = 3 * Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx') * 4
            a

        .. testoutput::

            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx
            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx
            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx

        We can create a circle over the data.

        .. testcode::

            a.circle(1, char=' ')

        .. testoutput::

            abcde              bcdef
            ghi   ghijklghijkl   jkl
            m   qrmnopqrmnopqrmn   r
              uvwxstuvwxstuvwxstuv
             bcdefabcdefabcdefabcde
             hijklghijklghijklghijk
             nopqrmnopqrmnopqrmnopq
             tuvwxstuvwxstuvwxstuvw
              cdefabcdefabcdefabcd
            g   klghijklghijklgh   l
            mno   mnopqrmnopqr   pqr
            stuvw              tuvwx


        """
        c = circle(radius, self.height, self.width, char)
        return Str3D([c, self])

    def hole(self, radius, char="*"):
        """
        Create a hole over the object. This is a wrapper around the `hole` function and
        returns a new Str3D object with the hole over the data.  This effectively hides
        the surrounding data and only shows the hole.

        Parameters
        ----------
        radius : float
            The radius of the hole.  The minimum of the height and width of the data is
            used as a reference for the radius equal to 1.

        char : str, optional
            The character to use for the hole, by default '*'.

        Returns
        -------
        Str3D
            A new Str3D object with the hole over the data.

        See Also
        --------
        circle : Create a circle over the data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then
        create a hole over it.

        .. testcode::

            from str2d import Str2D

            a = 3 * Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx') * 4

        .. testoutput::

            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx
            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx
            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx

        .. testcode::

            a.hole(1, char=' ')

        .. testoutput::

                   bcdefabcde
                klghijklghijklgh
              opqrmnopqrmnopqrmnop
             tuvwxstuvwxstuvwxstuvw
            abcdefabcdefabcdefabcdef
            ghijklghijklghijklghijkl
            mnopqrmnopqrmnopqrmnopqr
            stuvwxstuvwxstuvwxstuvwx
             bcdefabcdefabcdefabcde
              ijklghijklghijklghij
                qrmnopqrmnopqrmn
                   tuvwxstuvw


        """
        c = hole(radius, self.height, self.width, char)
        return Str3D([c, self])

    def box_over(self, style: Union[BoxStyle, str] = BoxStyle.SINGLE_ROUND) -> "Str3D":
        """Create a box over the data.  The difference between this and `box_around` is
        that this method creates a box over the data and the other method creates a box
        around the data.  The box that is created will cover the edges of the data.
        This is useful when preserving the size is important.

        Parameters
        ----------
        style : Union[BoxStyle, str], optional
            The style of the box, by default BoxStyle.single_round.

        Returns
        -------
        Str3D
            A new Str3D object with the box over the data.

        See Also
        --------
        box_around : Create a box around the data.
        box : Create a box around the data.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then
        create a box over it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.box_over()

        .. testoutput::

            ╭────╮
            │hijk│
            │nopq│
            ╰────╯

        """
        box = Box([self.height - 2], [self.width - 2], style)
        return Str3D([box, self])

    def box_around(
        self, style: Union[BoxStyle, str] = BoxStyle.SINGLE_ROUND
    ) -> "Str3D":
        """Create a box around the data.  The difference between this and `box_over` is
        that this method creates a box around the data and the other method creates a
        box over the data.  The box that is created will surround the data.  This is
        useful when preserving the content is important.

        Parameters
        ----------
        style : Union[BoxStyle, str], optional
            The style of the box, by default BoxStyle.single_round.

        Returns
        -------
        Str3D
            A new Str3D object with the box around the data.

        See Also
        --------
        box_over : Create a box over the data.
        box : Create a box around the data.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then
        create a box around it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.box_around()

        .. testoutput::

            ╭──────╮
            │abcdef│
            │ghijkl│
            │mnopqr│
            │stuvwx│
            ╰──────╯

        """
        s = self.pad(((1, 1), (1, 1)))
        box = Box([self.height], [self.width], style)
        return Str3D([box, s])

    def box(
        self, style: Union[BoxStyle, str] = BoxStyle.SINGLE_ROUND, around: bool = True
    ) -> "Str3D":
        """Wrapper around `box_over` and `box_around` methods.  This method will create
        a box around or over the data.

        Parameters
        ----------
        style : str, optional
            The style of the box, by default "single_round".

        around : bool, optional
            Whether to create a box around the data or over the data, by default True.

        Returns
        -------
        Str3D
            A new Str3D object with the box around or over the data.

        See Also
        --------
        box_over : Create a box over the data.
        box_around : Create a box around the data.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then
        create a box around it.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.box()

        .. testoutput::

            ╭──────╮
            │abcdef│
            │ghijkl│
            │mnopqr│
            │stuvwx│
            ╰──────╯

        We can also create a box over the data.

        .. testcode::

            a.box(around=False)

        .. testoutput::

            ╭────╮
            │hijk│
            │nopq│
            ╰────╯

        """
        if around:
            return self.box_around(style)
        return self.box_over(style)

    def pi(self):
        """Replace the data with digits of pi.  This is a wrapper around the `pi`
        function and returns a new Str2D object with the data replaced with the digits

        Returns
        -------
        Str2D
            A new Str2D object with the data replaced with the digits of pi.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.pi()

        .. testoutput::

            3.1415
            926535
            897932
            384626

        """
        data = self.data.copy()
        i, j = data["alpha"].nonzero()
        old_dps = mp.mp.dps
        n = len(i)
        mp.mp.dps = n
        data["char"][i, j] = [*str(mp.pi)][:n]
        mp.mp.dps = old_dps
        return Str2D(data=data, **self.kwargs)

    def e(self):
        """Replace the data with digits of e.  This is a wrapper around the `e`
        function and returns a new Str2D object with the data replaced with the digits

        Returns
        -------
        Str2D
            A new Str2D object with the data replaced with the digits of e.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.e()

        .. testoutput::

            2.7182
            818284
            590452
            353602

        """
        data = self.data.copy()
        i, j = data["alpha"].nonzero()
        old_dps = mp.mp.dps
        n = len(i)
        mp.mp.dps = n
        data["char"][i, j] = [*str(mp.e)][:n]
        mp.mp.dps = old_dps
        return Str2D(data=data, **self.kwargs)

    def phi(self):
        """Replace the data with digits of phi.  This is a wrapper around the `phi`
        function and returns a new Str2D object with the data replaced with the digits

        Returns
        -------
        Str2D
            A new Str2D object with the data replaced with the digits of phi.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx

        .. testcode::

            a.phi()

        .. testoutput::

            1.6180
            339887
            498948
            482045

        """
        data = self.data.copy()
        i, j = data["alpha"].nonzero()
        old_dps = mp.mp.dps
        n = len(i)
        mp.mp.dps = n
        data["char"][i, j] = [*str(mp.phi)][:n]
        mp.mp.dps = old_dps
        return Str2D(data=data, **self.kwargs)

    def hide(self, char=" "):
        """Hide where character array is char.  This sets the alpha array to 0 where the
        character array is equal to char.

        Parameters
        ----------
        char : str, optional
            The character to hide, by default ' '.

        Returns
        -------
        Str2D
            A new Str2D object with the data hidden.

        Examples
        --------
        Let's create an instance of Str2D and assign it to the variable `a` and then
        hide the data.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdef\\nghijkl\\nmnopqr\\nstuvwx')
            a

        .. testoutput::

            abcdef
            ghijkl
            mnopqr
            stuvwx


        The hiddent data doesn't replace the character with a space but sets the alpha
        array to 0 where the character array is equal to the character to hide.  So, in
        a singular context, we can still see the character and must fill the 0s with a
        character to hide the data.

        .. testcode::

            a.hide(char='m').fill_with(char=' ')

        .. testoutput::

            abcdef
            ghijkl
            mno qr
            stuvwx

        """
        data = self.data.copy()
        i, j = (data["char"] == char).nonzero()
        data["alpha"][i, j] = 0
        return Str2D(data=data, **self.kwargs)

    def fill_with(self, char=" ") -> "Str2D":
        """Fill the data with the character.  This is a wrapper around the `fill` method
        from the structured array data.

        Parameters
        ----------
        char : str, optional
            The character to fill with, by default ' '.

        Returns
        -------
        Str2D
            A new Str2D object with the data filled with the character.

        See Also
        --------
        hide : Hide the data.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then
        fill.

        .. testcode::

            from str2d import Str2D

            a = Str2D('abcdefg\\nhijklm\\nnopqr\\nstuv\\nwxy\\nz')
            a

        .. testoutput::

            abcdefg
            hijklm
            nopqr
            stuv
            wxy
            z

        We can fill the data with a character.

        .. testcode::

            a.fill_with(char='.')

            abcdefg
            hijklm.
            nopqr..
            stuv...
            wxy....
            z......

        """
        kwargs = self.kwargs
        kwargs["fill"] = (char, 0)
        data = np.where(self.data["alpha"], self.data["char"], char)
        return Str2D(data=data, **kwargs)

    def __str__(self) -> str:
        """Return the string representation of the data."""
        return "\n".join(["".join(row["char"]) for row in self.data])

    def __repr__(self) -> str:
        """Return the string representation of the data."""
        return str(self)

    ####################################################################
    # String operations whose result is a new Str2D ####################
    ####################################################################
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

    def replace(self, old: str, new: str) -> "Str2D":
        """Replace the data.

        Parameters
        ----------
        old : str
            The string to replace.

        new : str
            The string to replace with.

        Returns
        -------
        Str2D
            A new Str2D object with the data replaced.

        Raises
        ------
        ValueError
            If the length of the old and new strings are not the same.
        """
        if len(old) != len(new):
            raise ValueError("old and new must have the same length.")
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
        """Strip line by line.  Return the stripped version of the data.  This is a
        wrapper around the `strip` method from the str class."""
        data = self.data.copy()
        char = ["".join(row).strip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    def lstrip(self, *args, **kwargs) -> "Str2D":
        """Left strip line by line.  Return the left stripped version of the data.  This
        is a wrapper around the `lstrip` method from the str class."""
        data = self.data.copy()
        char = ["".join(row).lstrip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    def rstrip(self, *args, **kwargs) -> "Str2D":
        """Right strip line by line.  Return the right stripped version of the data.
        This is a wrapper around the `rstrip` method from the str class."""
        data = self.data.copy()
        char = ["".join(row).rstrip(*args, **kwargs) for row in data["char"]]
        return Str2D(data=char, **self.kwargs)

    ####################################################################
    # String operations whose result is a new boolean array ############
    ####################################################################
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
        """Strip the data 2-dimensionally.  This method checks how much it can trim from
        each side of the data before it reaches a non-matching character.  It then trims
        the data accordingly.
        
        Parameters
        ----------
        char : str, optional
            The character to strip, by default ' '.  This is the character that will be
            trimmed from the data.

        Returns
        -------
        Str2D
            A new Str2D object with the data stripped.

        Examples
        --------

        Let's create an instance of Str2D and assign it to the variable `a` and then
        strip the data.

        .. testcode::

            from str2d import Str2D

            a = Str2D('''\\
            ............
            ...xxxxxxx..
            ...xxxxxxx..
            ...xxxxxxx..
            ............
            ............
            ''')

        Striping '.' from the data will leave just the core of 'x's.

        .. testoutput::

            a.strip2d(char='.')

        .. testoutput::

            xxxxxxx
            xxxxxxx
            xxxxxxx

        """
        mask = self != char
        x0, x1 = np.flatnonzero(mask.any(axis=1))[[0, -1]]
        y0, y1 = np.flatnonzero(mask.any(axis=0))[[0, -1]]
        return self[x0 : x1 + 1, y0 : y1 + 1]


class Box(Str2D):
    """Subclass of Str2D that is a Box or Window.
    I wanted to be able to make window pains with arbitrary number of rows and columns.

    I had to override the transformation methods `i`, `t`, `h`, `v`, and `r` because I
    wanted to preserve the box characters orientation.

    Parameters
    ----------
    spec_v : List[int], optional
        The vertical specification, by default None.  This is a list of integers that
        represent the height of the rows.

    spec_h : List[int], optional
        The horizontal specification, by default None.  This is a list of integers that
        represent the width of the columns.

    style : Union[BoxStyle, str], optional
        The style of the box, by default BoxStyle.SINGLE_ROUND.

    Examples
    --------

    Let's create a box with a single round style.

    .. testcode::

        from str2d import Box

        Box(spec_v=[1, 2, 3], spec_h=[1, 2, 3])

    .. testoutput::

        ╭─┬──┬───╮
        │ │  │   │
        ├─┼──┼───┤
        │ │  │   │
        │ │  │   │
        ├─┼──┼───┤
        │ │  │   │
        │ │  │   │
        │ │  │   │
        ╰─┴──┴───╯


    """

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
        style: Union[BoxStyle, str] = BoxStyle.SINGLE_ROUND,
    ) -> "Box":
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


def space(mn: float, mx: float, w: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return left, center, and right points of a space.
    Imagine an integer number of cells.  I want to assign the left side of the left most
    cell to be `mn` and the right side of the right most cell to be `mx`.  This function
    returns 3 arrays.  The first array consists of the left side of each cell.  The
    second array consists of the center of each cell.  The third array consists of the
    right side of each cell.

    Let's imagine `w=5` and `mn=0` and `mx=1`.  The space is divided into 5 cells.

    .. testoutput::

                 mn=0         0.2         0.4         0.6         0.8         mx=1
                   │           │           │           │           │           │
                   ╭───────────┬───────────┬───────────┬───────────┬───────────╮
                   │           │           │           │           │           │
                   │           │           │           │           │           │
                   │           │           │           │           │           │
                   │           │           │           │           │           │
                   │           │           │           │           │           │
                   ├─────┬─────┼─────┬─────┼─────┬─────┼─────┬─────┼─────┬─────┤
        left      0.0    │    0.2    │    0.4    │    0.6    │    0.8    │     │
        center          0.1    │    0.3    │    0.5    │    0.7    │    0.9    │
        right                 0.2         0.4         0.6         0.8         1.0

    We can use these arrays to more accurately model x, y coordinates for ascii plots.

    Parameters
    ----------
    mn : float
        The minimum value of the space.

    mx : float
        The maximum value of the space.

    w : int
        The number of cells.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray, np.ndarray]
        The left, center, and right points of the space.

    Raises
    ------
    ValueError
        If `w` is less than 1.
    """
    if w < 1:
        raise ValueError(f"{w=} must be >= 1")

    a = np.linspace(mn, mx, w + 1)
    return a[:-1], (a[:-1] + a[1:]) / 2, a[1:]


def region(func, height, width, x_range, y_range):
    """Create a mask where func is True.
    Imagine a 2D space that is subdivided into `height` rows and `width` columns.  The
    edges of the space are defined by `x_range` and `y_range`.  This function returns a
    mask where `func` is True for the center of each cell.

    Parameters
    ----------
    func : Callable[[np.ndarray, np.ndarray], np.ndarray]
        The function that returns True if the point is in the region.

    height : int
        The number of rows.

    width : int
        The number of columns.

    x_range : Tuple[float, float]
        The range of the x values.

    y_range : Tuple[float, float]
        The range of the y values.

    Returns
    -------
    np.ndarray
        A mask where `func` is True for the center of each cell.

    See Also
    --------
    boundary : Create a mask where func is True and False.


    Examples
    --------

    Let's imagine `height=10` and `width=20` and `x_range=[0, 1]` and `y_range=[0, 1]`.

    Now we'll assume a simple function that returns True if the 1 less the x coordinate
    is less than the y coordinate.

    ... testinput::

        height = 10
        width = 20
        x_range = [0, 1]
        y_range = [0, 1]

        def func(x, y):
            return 1 - x < y

        mask = region(func, height, width, x_range, y_range)

        Str2D(mask, char='*')

    .. testoutput::

        *******************
          *****************
            ***************
              *************
                ***********
                  *********
                    *******
                      *****
                        ***
                          *


    """
    _, center, _ = space(*x_range, width)
    _, middle, _ = space(*y_range[::-1], height)
    return func(center.reshape(1, -1), middle.reshape(-1, 1))


def boundary(func, height, width, x_range, y_range):
    """Create a mask where func is True and False.
    Imagine a 2D space that is subdivided into `height` rows and `width` columns.  The
    edges of the space are defined by `x_range` and `y_range`.  The mask being returned
    is a proxy for each of the cells.  The truth of each cell is determined by whether
    `func` is True for at least one of the corners of the cell while also being False
    for at least one of the corners of the cell.  That implies that the function crosses
    from being True to False or False to True within the cell and thus a boundary.

    Parameters
    ----------
    func : Callable[[np.ndarray, np.ndarray], np.ndarray]
        The function that returns True if the point is in the region.

    height : int
        The number of rows.

    width : int
        The number of columns.

    x_range : Tuple[float, float]
        The range of the x values.

    y_range : Tuple[float, float]
        The range of the y values.

    Returns
    -------
    np.ndarray
        A mask where `func` is True for the center of each cell.

    See Also
    --------
    region : Create a mask where func is True.

    Examples
    --------

    Let's imagine `height=10` and `width=20` and `x_range=[0, 1]` and `y_range=[0, 1]`.

    Now we'll assume a simple function that returns True if the 1 less the x coordinate
    is less than the y coordinate.

    ... testinput::

        height = 10
        width = 20
        x_range = [0, 1]
        y_range = [0, 1]

        def func(x, y):
            return 1 - x < y

        mask = boundary(func, height, width, x_range, y_range)

        Str2D(mask, char='*')

    .. testoutput::

        ***
          ***
            ***
              ***
                ***
                  ***
                    ***
                      ***
                        ***
                          **

    """
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
    """Create a circle.
    This is a special application of the `boundary` function.  The function that
    determines the circle is `lambda x, y: x**2 + y**2 < radius**2`.

    Parameters
    ----------
    radius : float
        The radius of the circle.

    height : int
        The number of rows.

    width : int
        The number of columns.

    char : str, optional
        The character to use, by default '*'.

    Returns
    -------
    Str2D
        A new Str2D object with the circle.

    See Also
    --------
    boundary : Create a mask where func is True and False.
    Str2D.circle : Create a circle.

    """
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
    """Create a hole.
    This is a special application of the `region` function.  The function that
    determines the hole is `lambda x, y: x**2 + y**2 <= radius**2`.

    Parameters
    ----------
    radius : float
        The radius of the hole.

    height : int
        The number of rows.

    width : int
        The number of columns.

    char : str, optional
        The character to use, by default '*'.

    Returns
    -------
    Str2D
        A new Str2D object with the hole.

    See Also
    --------
    region : Create a mask where func is True.
    Str2D.hole : Create a hole.

    """
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


def is_in_mandelbrot(
    x: float, y: float, max_iterations: int = 25
) -> Union[bool, np.ndarray]:
    """
    Determines if the point (x, y) is in the Mandelbrot set.

    Parameters
    ----------
    x : float
        The x-coordinate of the point.

    y : float
        The y-coordinate of the point.

    max_iterations : int, optional
        The maximum number of iterations, by default 25.


    Returns
    -------
    Union[bool, np.ndarray]
        True if the point is in the Mandelbrot set, False otherwise.

    """

    if np.isscalar(x):
        x = np.array([x])
    if np.isscalar(y):
        y = np.array([y])

    n = len(y.ravel())
    m = len(x.ravel())

    c = np.empty((n, m), dtype=np.complex128)
    c.real = x.reshape(1, -1)
    c.imag = y.reshape(-1, 1)

    z = np.zeros((n, m), dtype=np.complex128)
    absz = abs(z)
    thresh = 10

    for _ in range(max_iterations):
        z = np.where(absz < thresh, z * z + c, thresh)
        absz = abs(z)
    return absz < 2


def mandelbrot(height, width, x_range, y_range, char="*"):
    """Create a Mandelbrot set.
    Visualize the Mandelbrot set.  The Mandelbrot set as a Str2d object.

    Parameters
    ----------
    height : int
        The number of rows.

    width : int
        The number of columns.

    x_range : Tuple[float, float]
        The range of the x values.

    y_range : Tuple[float, float]
        The range of the y values.

    char : str, optional
        The character to use, by default '*'.

    Returns
    -------
    Str2D
        A new Str2D object with the Mandelbrot set.

    See Also
    --------
    is_in_mandelbrot : Determines if the point is in the Mandelbrot set.

    Examples
    --------

    Let's create a Mandelbrot set.

    .. testcode::

        str2d.mandelbrot(
            44, 88,
            (-2, .5),
            (-1.25, 1.25),
            '*'
        ).strip2d().box()

    .. testoutput::

        ╭───────────────────────────────────────────────────────────────╮
        │                                           ****                │
        │                                        * ***** *              │
        │                                       *********               │
        │                                        ********               │
        │                           ***     * * * *******  *  *         │
        │                            **** ********************      * * │
        │                             *******************************   │
        │                            *******************************    │
        │                        *************************************  │
        │            *            **************************************│
        │                        ***************************************│
        │       *** *******     *************************************** │
        │       *************   ****************************************│
        │     **************** *****************************************│
        │    ********************************************************** │
        │************************************************************   │
        │************************************************************   │
        │    ********************************************************** │
        │     **************** *****************************************│
        │       *************   ****************************************│
        │       *** *******     *************************************** │
        │                        ***************************************│
        │            *            **************************************│
        │                        *************************************  │
        │                            *******************************    │
        │                             *******************************   │
        │                            **** ********************      * * │
        │                           ***     * * * *******  *  *         │
        │                                        ********               │
        │                                       *********               │
        │                                        * ***** *              │
        │                                           ****                │
        ╰───────────────────────────────────────────────────────────────╯


    """
    mask = region(is_in_mandelbrot, height, width, x_range, y_range)
    return Str2D(mask, char=char)


def pre(
    s: Str2D, font_size: int = 1, bg: Optional[str] = None, fg: Optional[str] = None
) -> HTML:
    """Create a preformatted HTML object."""
    this_id = str(uuid.uuid4())
    bg = bg or "rgba(0, 0, 0, 0)"
    fg = fg or "rgba(255, 255, 255, 1)"
    return HTML(
        dedent(
            f"""\
        <meta charset="UTF-8">
        <style>
            #_{this_id} {{
                font-family: monospace;
                font-size: {font_size}px;
                background-color: {bg};
                color: {fg};
                width: fit-content;
                height: fit-content;
            }}
        </style>
        <pre id="_{this_id}">{s!s}</pre>
    """
        )
    )


def traverse_path(path, box_style, depth=0):
    """Traverse a path and return a string representation of the path.
    This function is a recursive function that traverses a path and returns a string

    Parameters
    ----------
    path : Path
        The path to traverse.

    box_style : BoxStyle
        The style connecting lines.

    depth : int, optional
        The depth to traverse, by default 0.

    Returns
    -------
    str
        The string representation of the path.

    """
    if depth > 0:
        ls = list(path.iterdir())
        k = len(ls)
        to_be_joined = []
        for i, p in enumerate(ls):
            last = i == k - 1
            char = box_style.value.ll if last else box_style.value.l
            char += box_style.value.h
            buff = (" " if last else box_style.value.v) + " "
            pstr = Str2D(p.name)

            if p.is_file():
                to_be_joined.append(char + pstr)

            elif p.is_dir():
                head = char + pstr
                tail = traverse_path(p, box_style, depth - 1)
                if tail:
                    to_be_joined.append(head / (buff + tail))
                else:
                    to_be_joined.append(head)
        return Str2D.join_v(*to_be_joined)
    return ""
