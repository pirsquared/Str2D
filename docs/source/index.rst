Str2D - String Squared
======================

Install
-------

:code:`pip install git+https://github.com/pirsquared/Str2D`

Usage
-----

Simple operations

Addition

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

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   Modules <modules>
   Motivation <motivation>
   Purpose <purpose>
   About <about>


   `Repository <https://github.com/pirsquared/Str2D/tree/master>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
