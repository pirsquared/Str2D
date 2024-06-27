Motivation
==========

I wanted a clean way to stitch together multi-lined strings,
side by side.

Tree
----
I was motivated while trying to represent the tree structure
of a heap.

.. testsetup::

    from functools import partial
    from str2d import Str2D

.. testcode::

    def children(i):
        k = 2 * i + 1
        return (k, k + 1)

    def show_node(i, tree):
        n = len(tree)
        left, right = children(i)
        s2d = partial(
            Str2D,
            min_width=4, halign='center',
            min_height=2, valign='middle'
        )

        if i >= n:
            return Str2D('')
        else:
            return (
                s2d(tree[i]) /
                (show_node(left, tree) + show_node(right, tree))
            )

    nodes = list(range(15))

    show_node(0, nodes).box('double')

.. testoutput::

    ╔════════════════════════════════╗
    ║               0                ║
    ║                                ║
    ║       1               2        ║
    ║                                ║
    ║   3       4       5       6    ║
    ║                                ║
    ║ 7   8   9   10  11  12  13  14 ║
    ║                                ║
    ╚════════════════════════════════╝
