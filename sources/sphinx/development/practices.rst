.. vim: set fileencoding=utf-8:
.. -*- coding: utf-8 -*-
.. +--------------------------------------------------------------------------+
   |                                                                          |
   | Licensed under the Apache License, Version 2.0 (the "License");          |
   | you may not use this file except in compliance with the License.         |
   | You may obtain a copy of the License at                                  |
   |                                                                          |
   |     http://www.apache.org/licenses/LICENSE-2.0                           |
   |                                                                          |
   | Unless required by applicable law or agreed to in writing, software      |
   | distributed under the License is distributed on an "AS IS" BASIS,        |
   | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. |
   | See the License for the specific language governing permissions and      |
   | limitations under the License.                                           |
   |                                                                          |
   +--------------------------------------------------------------------------+

.. include:: <isopub.txt>

.. _EditorConfig: https://editorconfig.org

*******************************************************************************
Recommended Practices
*******************************************************************************

Assertions and Exceptions
===============================================================================

.. currentmodule:: lockup.exceptions

* Do not use ``assert`` statements except in unit tests.
  Assertions are not triggered in optimized compilations. Raise a
  :py:exc:`InvalidState` exception to report invalid internal state.

* Do not report incorrect invocations or invalid argument data
  as invalid internal state. I.e., raise an exception in the
  :py:exc:`InvalidOperation` family rather than an exception in the
  :py:exc:`InvalidState` family.

* Never raise a non-package exception from inside the package.
  Part of the API contract is that only exceptions in the
  :py:exc:`InvalidOperation` and :py:exc:`InvalidState` families are permitted
  to cross the API boundary.

* Always consider whether an invocation can leak Python built-in
  exceptions across the API boundary and explicitly manage those which can.

Code Style and Legibility
===============================================================================

Code style can be a surprisingly contentious issue. This project *does not* run
any style checker or code reformatter, such as `autopep8
<https://pypi.org/project/autopep8/>`_ or `black
<https://pypi.org/project/black/>`_. However, it is expected that patches will
follow a style similar to what is already present. Some basic guidance is
enforced via EditorConfig_, but mostly it is up to the patch submitter to try
to match the existing style. Though it is not perfect and good judgment will
still need to be exercised, you can execute the following on an uncommitted
patch to receive additional hints::

    python3 develop.py check-code-style

Unwitting "offenses" in new code can be readily forgiven, but patches which
contain reformatting noise against existing code will almost certainly be
rejected. Please digest this `Stack Exchange discussion on reformatting
<https://softwareengineering.stackexchange.com/questions/226440/is-it-okay-to-make-coding-style-changes-on-an-open-source-project-that-doesnt-f>`_.

Some tips:

* Horizontal space surrounding identifiers and literals improves legibility.
  Prior to the introduction of spaces between words around fourteen centuries
  ago, readers had to either parse words from `scriptio continua
  <https://en.wikipedia.org/wiki/Scriptio_continua>`_ or with the use of a
  `word divider <https://en.wikipedia.org/wiki/Word_divider>`_ symbol, such as
  the `interpunct <https://en.wikipedia.org/wiki/Interpunct>`_. Reading
  identifiers from code, which are separated only by delimiters, is equivalent
  to reading words separated by interpuncts, except that the syntactic noise is
  even higher due to the variety of delimiters (parentheses, commas, colons,
  etc...). Using horizontal space, an innovation from nearly 1.5 millennia ago,
  can reduce the cognitive load of filtering noise from syntactic markers.

* Try to keep function bodies under twenty (20) lines, no more than thirty
  (30) lines maximum. Long functions are probably doing too much and they
  are also difficult for the reader to comprehend. Bugs in them will be more
  likely to occur and possibly harder to track down.

* Related to the previous bullets is the principle of maintaining a vertically
  compact visual presentation for more related code on screen at the same time.
  To this end, single line conditional statements are not only accepted but
  encouraged. Examples include ``if <condition>: break``, ``if <condition>:
  continue``, ``if <condition>: return <data>``, ``else: return <data>``,
  ``except <exception-list> as exc: pass``, etc....

* Please avoid excessive indentation. For example, using ``if not <condition>:
  continue`` inside a loop body is generally preferable to using ``if
  <condition>:`` followed by indented lines inside that body. Excessive
  indentation tends to cause code to become smushed against the right margin,
  which reduces legibility.

* Please do not use lower camel case (``camelCase``) for anything. In addition
  to increasing the chance for typographic errors from not pressing or
  releasing the shift key on time, it suffers from legibility issues. Upper
  camel case (aka., Pascal case) (``CamelCase``) can be used for the names of
  types, but not for anything else. Aside from that, please use an underscore
  (``_``) to separate words within an identifier. Since Python does not support
  hyphens in identifiers, underscores can serve as reasonable visual separators
  instead, although they can also suffer typographic errors from incorrect
  shift key timing. I.e., prefer ``is_function`` to ``isfunction`` and
  ``starts_with`` to ``startswith``, in spite of seeing the unseparated words
  convention in use on standard Python types and in the Python standard
  library. The convenience of legibility outweighs the inconvenience of
  mistyping underscores or letters around them, as code should be read more
  than it is written.
