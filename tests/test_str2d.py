"""Tests for str2d.py."""

from str2d import Str2D


def test_str_in():
    s = Str2D("a\nbc")
    assert s == "a \nbc"


def test_str_in_minwidth_00():
    s = Str2D("a\nbc", min_width=5)
    assert s == "a    \nbc   "


def test_str_in_minwidth_01():
    s = Str2D("a\nbc", min_width=5, fill="x")
    assert s == "axxxx\nbcxxx"


def test_str_in_minwidth_02():
    s = Str2D("a\nbc", min_width=5, halign="left")
    assert s == "a    \nbc   "


def test_str_in_minwidth_03():
    s = Str2D("a\nbc", min_width=5, fill="x", halign="left")
    assert s == "axxxx\nbcxxx"


def test_str_in_minwidth_04():
    s = Str2D("a\nbc", min_width=5, halign="center")
    assert s == "  a  \n bc  "


def test_str_in_minwidth_05():
    s = Str2D("a\nbc", min_width=5, fill="x", halign="center")
    assert s == "xxaxx\nxbcxx"


def test_str_in_minwidth_06():
    s = Str2D("a\nbc", min_width=5, halign="right")
    assert s == "    a\n   bc"


def test_str_in_minwidth_07():
    s = Str2D("a\nbc", min_width=5, fill="x", halign="right")
    assert s == "xxxxa\nxxxbc"


def test_str_in_minheight_00():
    s = Str2D("a\nbc", min_height=5)
    assert s == "a \nbc\n  \n  \n  "


def test_str_in_minheight_01():
    s = Str2D("a\nbc", min_height=5, fill="x")
    assert s == "ax\nbc\nxx\nxx\nxx"


def test_str_in_minheight_02():
    s = Str2D("a\nbc", min_height=5, valign="top")
    assert s == "a \nbc\n  \n  \n  "


def test_str_in_minheight_03():
    s = Str2D("a\nbc", min_height=5, fill="x", valign="top")
    assert s == "ax\nbc\nxx\nxx\nxx"


def test_str_in_minheight_04():
    s = Str2D("a\nbc", min_height=5, valign="middle")
    assert s == "  \na \nbc\n  \n  "


def test_str_in_minheight_05():
    s = Str2D("a\nbc", min_height=5, fill="x", valign="middle")
    assert s == "xx\nax\nbc\nxx\nxx"


def test_str_in_minheight_06():
    s = Str2D("a\nbc", min_height=5, valign="bottom")
    assert s == "  \n  \n  \na \nbc"


def test_str_in_minheight_07():
    s = Str2D("a\nbc", min_height=5, fill="x", valign="bottom")
    assert s == "xx\nxx\nxx\nax\nbc"


def test_str_in_minwidth_minheight_00():
    s = Str2D("a\nbc", min_width=5, min_height=5)
    assert s == "a    \nbc   \n     \n     \n     "


def test_str_in_minwidth_minheight_01():
    s = Str2D("a\nbc", min_width=5, min_height=5, fill="x")
    assert s == "axxxx\nbcxxx\nxxxxx\nxxxxx\nxxxxx"


def test_str_in_minwidth_minheight_02():
    s = Str2D("a\nbc", min_width=5, min_height=5, halign="left", valign="top")
    assert s == "a    \nbc   \n     \n     \n     "


def test_str_in_minwidth_minheight_03():
    s = Str2D("a\nbc", min_width=5, min_height=5, fill="x", halign="left", valign="top")
    assert s == "axxxx\nbcxxx\nxxxxx\nxxxxx\nxxxxx"


def test_str_in_minwidth_minheight_04():
    s = Str2D("a\nbc", min_width=5, min_height=5, halign="center", valign="middle")
    assert s == "     \n  a  \n bc  \n     \n     "


def test_str_in_minwidth_minheight_05():
    s = Str2D(
        "a\nbc", min_width=5, min_height=5, fill="x", halign="center", valign="middle"
    )
    assert s == "xxxxx\nxxaxx\nxbcxx\nxxxxx\nxxxxx"


def test_str_in_minwidth_minheight_06():
    s = Str2D("a\nbc", min_width=5, min_height=5, halign="right", valign="bottom")
    assert s == "     \n     \n     \n    a\n   bc"


def test_str_in_minwidth_minheight_07():
    s = Str2D(
        "a\nbc", min_width=5, min_height=5, fill="x", halign="right", valign="bottom"
    )
    assert s == "xxxxx\nxxxxx\nxxxxx\nxxxxa\nxxxbc"


def test_str_box_00():
    s = Str2D("a\nbc").box().view
    assert s == "╭──╮\n│a │\n│bc│\n╰──╯"


def test_str_box_01():
    s = Str2D("a\nbcd", min_height=4, min_width=5, valign="middle", halign="center")
    s = s.box(style="DOUBLE").view
    assert s == "╔═════╗\n║     ║\n║  a  ║\n║ bcd ║\n║     ║\n╚═════╝"


def test_add_00():
    a = Str2D("a", fill="-", valign="middle", halign="center")
    b = Str2D("b", fill=".", valign="bottom", halign="right")
    s = a.expand(2, 2) + b
    assert s == "---.\n-a-.\n---b"


def test_add_01():
    a = Str2D("a", fill="-", valign="middle", halign="center")
    b = Str2D("b", fill=".", valign="bottom", halign="right")
    s = a.expand(2, 2) / b
    assert s == "---\n-a-\n---\n..b"


def test_h_00():
    a = Str2D("a")
    s = a.box().view.h
    assert s == "╮─╭\n│a│\n╯─╰"


def test_h_01():
    a = Str2D("a").box().view
    s = a.hh
    assert s == str(a)


def test_v_00():
    a = Str2D("a").box().view
    s = a.v
    assert s == "╰─╯\n│a│\n╭─╮"


def test_v_01():
    a = Str2D("a").box().view
    s = a.vv
    assert s == str(a)


def test_t_00():
    a = Str2D("a").box().view
    s = a.tt
    assert s == str(a)
