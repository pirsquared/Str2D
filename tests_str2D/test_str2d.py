import str2d
from str2d import Str2D
from str2d import utils
from string import ascii_letters, digits
from functools import partial


class TestStr2D(object):
    def test_constuction_one(self):
        s0_0 = "a\nbc\ndef"
        s0_l = "a  \nbc \ndef"
        s0_c = " a \nbc \ndef"
        s0_r = "  a\n bc\ndef"
        s0_w0 = s0_l
        s0_w4 = "a   \nbc  \ndef "
        s0_h0 = s0_l
        s0_h6_t = "a  \nbc \ndef\n   \n   \n   "
        s0_h6_m = "   \na  \nbc \ndef\n   \n   "
        s0_h6_b = "   \n   \n   \na  \nbc \ndef"
        s0_hf = "a..\nbc.\ndef"
        s0_vf = "a  \nbc \ndef\n+  \n+  \n+  "
        s0_ev = "..+...\n..a...\n..bc..\n.def..\n..+...\n..+..."

        assert Str2D(s0_0) == s0_l
        assert Str2D(Str2D(s0_0)) == s0_l
        assert Str2D(Str2D(s0_0).s) == s0_l
        assert Str2D(s0_0, halign="leFt") == s0_l
        assert Str2D(s0_0, halign="center") == s0_c
        assert Str2D(s0_0, halign="right") == s0_r
        assert Str2D(s0_0, min_width=0) == s0_l
        assert Str2D(s0_0, min_width=4) == s0_w4
        assert Str2D(s0_0, min_height=0) == s0_l
        assert Str2D(s0_0, min_height=6) == s0_h6_t
        assert Str2D(s0_0, min_height=6, valign="top") == s0_h6_t
        assert Str2D(s0_0, min_height=6, valign="middLe") == s0_h6_m
        assert Str2D(s0_0, min_height=6, valign="bottom") == s0_h6_b
        assert Str2D(s0_0, hfill=".") == s0_hf
        assert Str2D(s0_0, min_height=6, vfill="+") == s0_vf
        assert Str2D(s0_0, 6, "center", ".", 6, "middle", "+") == s0_ev

    def test_height(self):
        assert Str2D("1\n2\n3").height == 3
        assert Str2D("\n" * 5).height == 6

    def test_width(self):
        assert Str2D("1\n2\n3").width == 1
        assert Str2D("\n" * 5).width == 0
        assert Str2D("1234").width == 4
        assert Str2D("123\n 5  \n").width == 4

    def test_shape(self):
        assert Str2D("1\n2\n3").shape == (3, 1)
        assert Str2D("\n" * 5).shape == (6, 0)
        assert Str2D("1234").shape == (1, 4)
        assert Str2D("123\n 5  \n").shape == (3, 4)

    def test_construction_two(self):
        s = Str2D("1\n23")
        assert hasattr(s, "hfill")
        assert hasattr(s, "vfill")
        assert hasattr(s, "halign")
        assert hasattr(s, "valign")

    def test_kwargs(self):
        s = Str2D("1\n23", halign="center", vfill="^")

        assert s._kwargs == dict(halign="center", hfill="", valign="top", vfill="^")

    def test_transformations(self):
        s = Str2D("12\n43")
        assert s.I == "12\n43"
        assert s.H == "21\n34"
        assert s.V == "43\n12"
        assert s.T == "14\n23"
        assert s.TV == "23\n14"
        assert s.VH == "34\n21"
        assert s.VT == "41\n32"
        assert s.HVT == "32\n41"

    def test_roll(self):
        s = Str2D("123\n654")
        assert s.roll(1) == "231\n546"
        assert s.roll(50) == "312\n465"
        assert s.roll(0) == "123\n654"
        assert s.roll(1, 0) == "654\n123"
        assert s.roll(1, 0).roll(-2) == "546\n231"
        assert s.T.roll(1, 0) == "25\n34\n16"

    def test_shuffle(self):
        s = Str2D("abcde\nfghij")
        assert s.shuffle(3.1415) == "gdjhf\ncebia"

    def test_asstr2d(self):
        s = Str2D("12\n43")
        assert s is s.asstr2d(s)
        assert type(s.asstr2d("12\n43")) == type(s)
        assert s.asstr2d(s.__repr__()) is not s
        assert s.asstr2d(s) == s

    def test_add(self):
        s = Str2D("12\n43", valign="bottom")
        t = Str2D("abc\nde\nf", halign="right")

        assert s + t == "  abc\n12 de\n43  f"
        assert s.add(t) == "  abc\n12 de\n43  f"
        assert s.add(t, " | ") == "   | abc\n12 |  de\n43 |   f"

    def test_radd(self):
        s = Str2D("12\n43")
        assert "a" + s == "a12\na43"
        assert "a\n12\n+-x" + s == "a  12\n12 43\n+-x  "

    def test_div(self):
        s = Str2D("12\n43", valign="bottom")
        t = Str2D("abc\nde\nf", halign="right")

        assert s / t == "12 \n43 \nabc\n de\n  f"
        assert s.div(t) == "12 \n43 \nabc\n de\n  f"
        assert s.div(t, "-") == "12 \n43 \n---\nabc\n de\n  f"

    def test_mul(self):
        s = Str2D("12\n43")
        assert s * 2 == "1212\n4343"

    def test_rmul(self):
        s = Str2D("12\n43")
        assert 2 * s == "1212\n4343"

    def test_floordiv(self):
        s = Str2D("12\n43")
        assert s // 2 == "12\n43\n12\n43"

    def test_rfloordiv(self):
        s = Str2D("12\n43")
        assert 2 // s == "12\n43\n12\n43"

    def test_eq(self):
        s = Str2D("12\n43")
        t = s.V
        assert s == s
        assert not (s == t)

    def test_ne(self):
        s = Str2D("12\n43")
        t = s.V
        assert not (s != s)
        assert s != t

    def test_getitem(self):
        s = Str2D("12\n43")
        assert s[:1] / s[1:] == s
        assert s[:, :1] + s[:, 1:] == s
        assert s[::-1] == s.V
        assert s[:, ::-1] == s.H
        assert s[0] == "12"
        assert s[1][1] == "3"

    def test_copy(self):
        s = Str2D("12\n43")
        assert s == s.__copy__()
        assert s is not s.__copy__()

    def test_box(self):
        s = Str2D("12\n43")
        assert s.box_dbl() == "╔══╗\n║12║\n║43║\n╚══╝"
        assert s.box_sgl() == "┌──┐\n│12│\n│43│\n└──┘"
        assert s.buffer("#") == "####\n#12#\n#43#\n####"

    def test_fill(self):
        s = Str2D("123\n654\nabc\nfed")
        assert s.fill(".") == "...\n...\n...\n..."

    def test_strip2d(self):
        s = Str2D("12\n43")
        assert s.buffer(" ").strip2d() == s

    def test_strip(self):
        s = Str2D("12\n43")
        assert s.buffer(" ").strip() == "  \n12\n43\n  "

    def test_replace(self):
        s = Str2D("12\n43")
        assert s.replace("2", "5") == "15\n43"

    def test_lower(self):
        s = Str2D("Ab\nCD")
        assert s.lower() == "ab\ncd"

    def test_upper(self):
        s = Str2D("Ab\nCD")
        assert s.upper() == "AB\nCD"

    def test_title(self):
        s = Str2D("Ab\nCD")
        assert s.title() == "Ab\nCd"

    def test_count(self):
        s = Str2D("tttt\nd\ntthh")
        assert s.count("t") == 6

    def test_join(self):
        s = Str2D("12\n43")
        assert s._join("|", [s] * 3) == s + "|" + s + "|" + s
        assert s._join("-", [s] * 3, axis=0) == s / "-" / s / "-" / s

    def test_equal_width(self):
        s = Str2D("12\n43")
        assert all(
            map(lambda s: s.width == 6, s.equal_width([s, s.buffer(" "), s * 3]))
        )

    def test_sum(self):
        s = Str2D("12\n43")
        assert s.sum([s] * 4) == s * 4

    def test_join2d(self):
        s = Str2D("12\n43")
        assert s.join([s] * 3) == s * 5

    def test_mask(self):
        s = Str2D("12\n43")
        assert s.mask(" *\n* ") == "1 \n 3"

    def test_layer(self):
        s = Str2D("12\n43")
        assert Str2D("@@\n@@").layer(s.mask(" *\n* ")) == "1@\n@3"

    def test_iter(self):
        s = Str2D("12\n43")
        assert tuple(s.__iter__()) == s.s
