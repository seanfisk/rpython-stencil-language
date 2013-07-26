.. -*- coding: utf-8; -*-

======================================
 RPython Stencil Language Interpreter
======================================

.. image:: https://travis-ci.org/seanfisk/rpython-stencil-language.png
   :target: https://travis-ci.org/seanfisk/rpython-stencil-language

A simple experimental programming language implementing `finite difference`_ using stencils_.

.. _finite difference: http://en.wikipedia.org/wiki/Finite_difference
.. _stencils: http://en.wikipedia.org/wiki/Stencil_(numerical_analysis)

It is written in RPython_ and uses RPLY_ for lexing and parsing.

.. _RPython: http://doc.pypy.org/en/latest/coding-guide.html
.. _RPLY: https://github.com/alex/rply

Compatibility
=============

PyPy ≥ 2.0-beta2

Inspiration
===========

The following tutorial blog posts by Andrew Brown helped immensely in starting this project:

* `Tutorial: Writing an Interpreter with PyPy, Part 1 <http://morepypy.blogspot.com/2011/04/tutorial-writing-interpreter-with-pypy.html>`_
* `Tutorial Part 2: Adding a JIT <http://morepypy.blogspot.com/2011/04/tutorial-part-2-adding-jit.html>`_

In addition, Alex Gaynor's Topaz_ project, a Ruby implementation written in RPython, has been especially helpful as a reference for using RPython and RPLY.

.. _Topaz: https://github.com/topazproject/topaz

Credits
=======

* Written by Sean Fisk
* Advised by Davide Del Vento
* Developed as part of the SIParCS_ internship program at the `National Center for Atmospheric Research`_ (NCAR)

.. _SIParCS: http://www2.cisl.ucar.edu/siparcs
.. _National Center for Atmospheric Research: http://ncar.ucar.edu/
