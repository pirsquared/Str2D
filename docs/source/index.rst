Str2D - String Squared
======================

Install
-------

:code:`pip install git+https://github.com/pirsquared/Str2D`

Usage
-----

Simple operations

Addition is intended to adjoin to objects side by side.

.. code-block:: python

    from str2d import Str2D


    letters_3x3 = Str2D('abc\\ndef\\nghi')
    numbers_3x3 = Str2D('012\\n345\\n678')

    letters_3x3 + numbers_3x3

    abc012
    def345
    ghi678

However, you can include a separator in several different ways

.. code-block:: python

   letters_3x3.add(numbers_3x3, sep='|')

   abc|012
   def|345
   ghi|678

Or

.. code-block:: python

   letters_3x3 + '|' + numbers_3x2

   abc|012
   def|345
   ghi|678

Division will stack to objects on top of one another

.. code-block:: python

   letters_3x3 / numbers_3x3

   abc
   def
   ghi
   012
   345
   678

But like with addition, we can add a separator

.. code-block:: python

   letters_3x3.div(numbers_3x3, sep='-')

   abc
   def
   ghi
   ---
   012
   345
   678

Or equivalently

.. code-block:: python

   letters_3x3 / '-' / numbers_3x3

   abc
   def
   ghi
   ---
   012
   345
   678


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Modules <modules>
   Motivation <motivation>
   Purpose <purpose>
   About <about>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
