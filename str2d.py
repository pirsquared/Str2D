from functools import reduce


def _normalize(data, width, halign='^'):
    return tuple(
        map(
            lambda datum: f'{datum:{halign}{width}}',
            data
        )
    )


def _is_str(s):
    return isinstance(s, str)


class Str2d(object):
    def __init__(self, str_, width=0, height=0):
        """Creates a 2-D string thing that can be concatenated
        vertically and horizontally

        :param str_: Can be a newline delimited list of strings.
          Or another Str2d object, or a iterable of strings.

        Example:
        >>> s1 = Str2d('Hello\nWorld\nmy\nname\nis')
        ... s2 = Str2d('How\nAre\nYou?')
        ... s3 = Str2d('### My Cool 2D String ###')
        ...
        ... s3 / (s1 + s2)
        ### My Cool 2D String ###
               Hello How
               World Are
                my   You?
               name
                is
        """

        if isinstance(str_, str):
            splits = str_.splitlines()
            width = max(width, max(map(len, splits)))
            self.data = _normalize(splits, width)
        elif isinstance(str_, type(self)):
            self.data = _normalize(str_.data, max(width, str_.width))
        else:
            if hasattr(str_, '__iter__') and not isinstance(str_, str):
                data = tuple(str_)
                if all(map(_is_str, data)) and bool(data):
                    width = max(width, max(map(len, data)))
                    self.data = _normalize(data, width)
            else:
                print(str_)

        if self.height < height:
            up_buf, lo_buf = self._get_vbuffer(height - self.height, 'c')
            empty = ('',)
            self.data = _normalize(empty * up_buf + self.data + empty * lo_buf, self.width)

    @property
    def width(self):
        return max(map(len, self.data))

    @property
    def height(self):
        return len(self.data)

    @property
    def shape(self):
        return self.height, self.width

    @staticmethod
    def _get_vbuffer(buffer_size, valign):
        upper_buffer = (
            0 if valign == 'u' else
            (buffer_size + 1) // 2 if valign == 'c' else
            buffer_size
        )
        lower_buffer = buffer_size - upper_buffer
        return upper_buffer, lower_buffer

    def __repr__(self):
        return '\n'.join(self.data)

    def __add__(self, other, valign='c'):

        t = type(self)
        s, o = self, t(other)

        sh, oh = s.height, o.height
        height = max(sh, oh)
        empty = ('',)

        if sh < height:
            up_buf, lo_buf = self._get_vbuffer(height - sh, valign)
            s = t(empty * up_buf + s.data + empty * lo_buf)

        elif oh < height:
            up_buf, lo_buf = self._get_vbuffer(height - oh, valign)
            o = t(empty * up_buf + o.data + empty * lo_buf)

        return t(map(
            ' '.join,
            zip(s.data, o.data)
        ))

    def __radd__(self, other):
        return type(self)(other) + self

    def __truediv__(self, other):
        other = type(self)(other)
        return type(self)(self.data + other.data)

    def __mul__(self, n):
        add = lambda self, other: self + other
        return reduce(add, [self] * n)

    def __floordiv__(self, n):
        div = lambda self, other: self / other
        return reduce(div, [self] * n)
