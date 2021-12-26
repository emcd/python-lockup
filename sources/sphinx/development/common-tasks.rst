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

.. _asdf: https://github.com/asdf-vm/asdf
.. _pipenv: https://pypi.org/project/pipenv

*******************************************************************************
Common Tasks
*******************************************************************************

During development, some tasks are repeated again and again.  And some tasks
are dependent upon other tasks. Traditionally, the :command:`make` command or
a script or batch file would be used to automate such tasks. However, in to
provide maximum portability and to reduce the number of languages that a
developer needs to remember, we use a Python-native solution: `invoke
<https://www.pyinvoke.org/>`_. The :command:`invoke` command is available as
part of the virtual environment maintained by Pipenv for this project.

Instead of defining tasks in a ``Makefile``, we instead define them as Python
code in :file:`tasks`. To see a summary of the available tasks, you can
execute::

    pipenv run invoke --list

We recommend the use of :command:`invoke` rather than running tools directly,
since it performs environment sanitization and other frequently-overlooked
tasks automatically, freeing you from fighting weird cache effects or various
oversights, such as validating URLs in documentation or linting tests.

Documentation
===============================================================================

Documentation artifacts are built by
`Sphinx <https://www.sphinx-doc.org/en/master/>`_
using an extended form of the
`reStructuredText <https://docutils.sourceforge.io/rst.html>`_ (``rst``)
plaintext markup language. The sources for the documentation are under
:file:`sources/sphinx`; the artifacts can be produced by::

    pipenv run invoke make-html

Some useful references for editing the sources are:

* `reStructuredText Quick Reference
  <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_
* `reStructuredText Directives
  <https://docutils.sourceforge.io/docs/ref/rst/directives.html>`_
* `reStructuredText Directives in Sphinx
  <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`_
* `reStructuredText Roles in Sphinx
  <https://www.sphinx-doc.org/en/master/usage/restructuredtext/roles.html>`_
* `reStructuredText Domains in Sphinx
  <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html>`_

*Why not use a flavor of Markdown instead?*

While Markdown is almost certainly better known than reStructuredText, Sphinx
provides first-class support for the latter; Sphinx is a very powerful
documentation generator and it is also the de facto standard within the Python
community. Furthermore, reStructuredText is very well-suited to technical
documentation, whereas Markdown is more general purpose. Although Markdown may
have a somewhat simpler syntax than reStructuredText, `multiple, competing
flavors
<https://about.gitlab.com/blog/2019/06/13/how-we-migrated-our-markdown-processing-to-commonmark/>`_
of the language exist, which partially negates the simplicity. In light of
these factors, we have standardized on 100% reStructuredText for all project
documentation.

*Why not use Markdown for some things at least?*

Context-switching between multiple languages adds cognitive load
and increases the chance of misapplied syntax.

Linting
===============================================================================

Our primary Python linter is `Pylint <https://www.pylint.org/>`_.
Note that we use this as an actual static analysis tool
and not merely a style checker. You can lint the sources by::

    pipenv run invoke lint

*Why not use* `Flake8 <https://flake8.pycqa.org/en/latest/>`_ *?*

Flake8 does not catch nearly as many issues as Pylint does and tends to focus
on code style rather than finding actual bugs and smells. Because of Pylint's
greater sensitivity, it may have a reputation as "not working" out of the box,
which may be why some people prefer Flake8. However, we prefer the fact that
Pylint finds more bugs and smells and have already taken the time to tune it
for the project's needs.

Testing
===============================================================================

Our primary Python tester is `Pytest <https://docs.pytest.org/en/stable/>`_.
We use this to run unit tests and doctests.  In general, we prefer to write
test functions rather than heavyweight `unittest
<https://docs.python.org/3/library/unittest.html>`_ classes.  Also, we make
extensive use of `parametrized tests
<https://docs.pytest.org/en/stable/parametrize.html#parametrize-basics>`_ and
`property-based testing <https://hypothesis.readthedocs.io/en/latest/>`_.  To
run the test suite in the current virtual environment maintained by pipenv_,
you can execute::

    pipenv run invoke test

To ensure that the test suite passes on all Python implementations,
which are supported by the project, you can execute::

    pipenv run invoke test-all-versions

This may take a longer time to complete.  Under the covers, it is using `tox
<https://pypi.org/project/tox>`_, which runs the test suite in an array of
isolated virtual environments.  The virtual environments are instantiated via
the `tox-asdf <https://pypi.org/project/tox-asdf/>`_ plugin, thus integrating
with the Python implementations already available via asdf_.
