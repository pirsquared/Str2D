String Squared - Str2D
======================

I wanted a clean way to stitch together multi-lined strings,
side by side.

Tree
----
I was motivated while trying to represent the tree structure
of a heap.

.. code-block:: python

    from functools import partial
    from str2d import Str2D


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
            return s2d('')
        else:
            return s2d(tree[i]) / (show_node(left, tree) + show_node(right, tree))

    nodes = list(range(15))

    show_node(0, nodes)

                                   0

                   1                               2

           3               4               5               6

       7       8       9       10      11      12      13      14


Side by Side
------------

I'm often using the Pandas library and want to show two dataframes side by side.

.. code-block:: python

    from str2d import Str2D
    import pandas as pd

    df1 = pd.DataFrame([[1, 2]], ['A'], ['X', 'Y'])
    df2 = -df1 * 37

    Str2D(df1).box_dbl() + Str2D(df2).box_sgl()

    ╔═══════╗┌─────────┐
    ║   X  Y║│    X   Y│
    ║A  1  2║│A -37 -74│
    ╚═══════╝└─────────┘

Winter Card
-----------

You can even get creative with it.

.. code-block:: python

    from str2d import Str2D
    from str2d import utils

    from string import (
        ascii_letters,
        digits
    )
    from functools import partial
    from IPython.display import clear_output
    import pandas as pd


    _tree_ = r"""
             ^
            /#\
           /###\
          /#####\
         /#######\
        /#########\
       /###########\
         #########
    """

    t = Str2D(_tree_)

    chars = ascii_letters + digits
    s = Str2D(utils.chunk((chars * 6)[:180], 18))

    los = [a for _ in range(3) for a in [s.shuffle(3.1415).mask(t), t]]


    card = Str2D.vjoin(' ', map(
        partial(Str2D.hjoin, ' '),
        zip(*[los[i::3] for i in range(3)])
    )).buffer(' ', 1)[1:-1].box_dbl()

    ╔══════════════════════════════════════════════════════════╗
    ║ nxMPRtNc3vXXTIubLI                    nxMPRtNc3vXXTIubLI ║
    ║ UBdeCWVCs TzdkKl2w          ^         UBdeCWVCs TzdkKl2w ║
    ║ 5CEoGpYI   kOcfcOB         /#\        5CEoGpYI   kOcfcOB ║
    ║ 2JH36oS     hDaFAQ        /###\       2JH36oS     hDaFAQ ║
    ║ iRz9wg       Ap8gm       /#####\      iRz9wg       Ap8gm ║
    ║ gn0Hl         kEj7      /#######\     gn0Hl         kEj7 ║
    ║ yy5Z           aQl     /#########\    yy5Z           aQl ║
    ║ 4ON             ed    /###########\   4ON             ed ║
    ║ tpbFE         TPMo      #########     tpbFE         TPMo ║
    ║ srjXFmWhWuhuqNqHvj                    srjXFmWhWuhuqNqHvj ║
    ║                                                          ║
    ║                    nxMPRtNc3vXXTIubLI                    ║
    ║          ^         UBdeCWVCs TzdkKl2w          ^         ║
    ║         /#\        5CEoGpYI   kOcfcOB         /#\        ║
    ║        /###\       2JH36oS     hDaFAQ        /###\       ║
    ║       /#####\      iRz9wg       Ap8gm       /#####\      ║
    ║      /#######\     gn0Hl         kEj7      /#######\     ║
    ║     /#########\    yy5Z           aQl     /#########\    ║
    ║    /###########\   4ON             ed    /###########\   ║
    ║      #########     tpbFE         TPMo      #########     ║
    ║                    srjXFmWhWuhuqNqHvj                    ║
    ╚══════════════════════════════════════════════════════════╝