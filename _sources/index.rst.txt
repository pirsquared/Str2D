Str2D - String Squared
======================

Install
-------

:code:`pip install str2d`


.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Module Documentation <str2d>
   Motivation <motivation>
   About <about>


Usage
-----

Simple operations

Addition is intended to adjoin to objects side by side.

.. testsetup::

    from str2d import Str2D

.. testcode::

    letters_3x3 = Str2D('abc\ndef\nghi')
    numbers_3x3 = Str2D('012\n345\n678')

    letters_3x3 + numbers_3x3

.. testoutput::

    abc012
    def345
    ghi678

However, you can include a separator in several different ways

.. testcode::

   letters_3x3.add(numbers_3x3, sep='|')

.. testoutput::

   abc|012
   def|345
   ghi|678

Or

.. testcode::

   letters_3x3 + '|' + numbers_3x2

.. testoutput::

   abc|012
   def|345
   ghi|678

Division will stack to objects on top of one another

.. testcode::

   letters_3x3 / numbers_3x3

.. testoutput::

   abc
   def
   ghi
   012
   345
   678

But like with addition, we can add a separator

.. testcode::

   letters_3x3.div(numbers_3x3, sep='-')

.. testoutput::

   abc
   def
   ghi
   ---
   012
   345
   678

Or equivalently

.. testcode::

   letters_3x3 / '-' / numbers_3x3

.. testoutput::

   abc
   def
   ghi
   ---
   012
   345
   678

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

