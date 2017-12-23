import str2d
from str2d import Str2D


class TestStr2D(object):
    def test_constuction_one(self):
        s0_0 = 'a\nbc\ndef'
        s0_l = 'a  \nbc \ndef'
        s0_c = ' a \nbc \ndef'
        s0_r = '  a\n bc\ndef'
        s0_w0 = s0_l
        s0_w4 = 'a   \nbc  \ndef '
        s0_h0 = s0_l
        s0_h6_t = 'a  \nbc \ndef\n   \n   \n   '
        s0_h6_m = '   \na  \nbc \ndef\n   \n   '
        s0_h6_b = '   \n   \n   \na  \nbc \ndef'
        s0_hf = 'a..\nbc.\ndef'
        s0_vf = 'a  \nbc \ndef\n+  \n+  \n+  '
        s0_ev = '..+...\n..a...\n..bc..\n.def..\n..+...\n..+...'

        assert Str2D(s0_0) == s0_l
        assert Str2D(Str2D(s0_0)) == s0_l
        assert Str2D(Str2D(s0_0).s) == s0_l
        assert Str2D(s0_0, halign='leFt') == s0_l
        assert Str2D(s0_0, halign='center') == s0_c
        assert Str2D(s0_0, halign='right') == s0_r
        assert Str2D(s0_0, min_width=0) == s0_l
        assert Str2D(s0_0, min_width=4) == s0_w4
        assert Str2D(s0_0, min_height=0) == s0_l
        assert Str2D(s0_0, min_height=6) == s0_h6_t
        assert Str2D(s0_0, min_height=6, valign='top') == s0_h6_t
        assert Str2D(s0_0, min_height=6, valign='middLe') == s0_h6_m
        assert Str2D(s0_0, min_height=6, valign='bottom') == s0_h6_b
        assert Str2D(s0_0, hfill='.') == s0_hf
        assert Str2D(s0_0, min_height=6, vfill='+') == s0_vf
        assert Str2D(s0_0, 6, 'center', '.', 6, 'middle', '+') == s0_ev

    def test_height(self):
        assert Str2D('1\n2\n3').height == 3
        assert Str2D('\n' * 5).height == 6

    def test_width(self):
        assert Str2D('1\n2\n3').width == 1
        assert Str2D('\n' * 5).width == 0
        assert Str2D('1234').width == 4
        assert Str2D('123\n 5  \n').width == 4

    def test_construction_two(self):
        s = Str2D('1\n23')
        assert hasattr(s, 'hfill')
        assert hasattr(s, 'vfill')
        assert hasattr(s, 'halign')
        assert hasattr(s, 'valign')


