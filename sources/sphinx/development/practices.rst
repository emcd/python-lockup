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

    devshim check-code-style

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

Importation
===============================================================================

Locality
-------------------------------------------------------------------------------

Although :PEP:`8` encourages imports near the top of module source code, this
has a number of drawbacks:

* Increases number of globals in module. And, to remember which ones are
  available, one must look at the top of the module source code or use an
  integrated development environment with code completion.

* Inhibits refactoring of classes and functions between modules, because any
  imports on which they depend must either be duplicated or moved too.

* Without aliasing via the ``as`` keyword, the imports will be part of the
  public interface of the module, which creates noise that competes with the
  actual interface being provided.

* Import cycles are more likely as the imports are evaluated at module
  initialization time.

The PEP provides no arguments to support its recommendation. By contrast, if
you import what you need within a function, then you can readily recall what is
available without having to jump to another part of the source code. Also, the
imports will travel with the function during a refactor to another module. And,
the imports will be concealed and not part of the public interface of the
module. And, last but not least, you can often avoid import cycles, due to the
deferred nature of function evaluation.

However, there are some extenuating circumstances, where importation outside of
functions is preferable. Examples include:

* Heavy use of the same imported module attribute across many functions in the
  module, such that separate imports would cause a significant increase in the
  number of lines of code or present a maintenance problem.

* Hot path code where even the retrieval of an attribute from an
  already-imported module could negatively impact performance.

* If the module being imported has a custom ``__getattribute__`` method, which
  is assigned to the module after module initialization and which could
  introduce an import cycle with a deferred import in another module that might
  invoke it.

So, please prefer function-local imports, but keep an eye out for special cases
and use good judgment.

Order
-------------------------------------------------------------------------------

In most other respects, the recommendations of :PEP:`8` are quite reasonable
and one should adhere to them whenever possible. This includes the
recommendation on import order, which is as follows. Imports should be grouped
in the following order:

1. Standard library imports.
2. Related third-party imports.
3. Local application-/library-specific imports.

Each group should be separated by a blank line. Also, the order of imports
within each group should follow a lexicographical order from the cardinal
values of the characters of the `standard ASCII table
<https://www.asciitable.com/>`_.
