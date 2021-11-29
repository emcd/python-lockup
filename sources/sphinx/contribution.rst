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

*******************************************************************************
Contribution
*******************************************************************************

Contribution to this project is welcome!
Here are some ways that you can help:

* Filing `issues <https://github.com/emcd/python-lockup/issues>`_
  for bug reports, feature requests, and other relevant discussion.
* Helping out with the development_ of the source code and documentation.

Please do note that all interactions about this project
on media under its control are subject to its `Code of Conduct`_.

Code of Conduct
===============================================================================

Please take a look at:

* `How to Ask Questions the Smart Way
  <http://www.catb.org/~esr/faqs/smart-questions.html>`_ (but understand that
  some of the showcased responses to "stupid questions" may not be acceptable)

* `Python Software Foundation Code of Conduct
  <https://www.python.org/psf/conduct/>`_ (in particular, the ``Our Community``
  and ``Our Standards: Inappropriate Behavior`` sections)

as well as note the following bullet points from the `Rust Code of Conduct
<https://www.rust-lang.org/policies/code-of-conduct>`_:

  |bull| Respect that people have differences of opinion and that every design
  or implementation choice carries a trade-off and numerous costs. There is
  seldom a right answer.

  |bull| Please keep unstructured critique to a minimum. If you have solid
  ideas you want to experiment with, make a fork and see how it works.

  |bull| Likewise any spamming, trolling, flaming, baiting or other
  attention-stealing behavior is not welcome.

.. note:: Please do not contact the authors of the above documents
          for anything related to this project.

Please act in the spirit of respect for others, whether you are asking
questions, providing feedback, or answering questions. Please remember that
volunteerism powers much of the open source available for you to use.

Also, no need to create noise with "+1" or "me too" comments in issue
tracker threads. Please only add substantive comments that will further advance
the understanding of an issue. If you wish to upvote a comment, then please use
an appropriate reacji on that comment.

Development
===============================================================================

Environment
-------------------------------------------------------------------------------

`asdf <https://github.com/asdf-vm/asdf>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We develop against one baseline version of the CPython reference
implementation; this is the first version listed in the ``.tool-versions``
file, located at the top level of the project repository. However, we also test
against successive minor versions beyond this baseline version, as well as
equivalent versions for alternative implementations. Those versions are listed
after the baseline version in the same file. This file is used by the excellent
asdf_ version manager to determine which versions of Python are considered
active for the project. We strongly recommend the use of asdf_ to manage
multiple versions of Python.

To build the CPython implementations that we support, you may need to install
some packages with your OS package manager first:

.. tab:: apt

    .. code-block:: sh

        sudo apt update && sudo apt install libbz2-dev libffi-dev libsqlite3-dev libssl-dev libreadline-dev zlib1g-dev

If you have installed asdf_, then you can execute the following commands to
ensure that the necessary Python environments are available:

.. tab:: Bourne Shells |dagger|

    .. code-block:: sh

        . $HOME/.asdf/asdf.sh  # or equivalent for non-standard installation
        asdf plugin-add python
        for python_version in $(egrep ^python .tool-versions | sed 's|^python ||'); do
            asdf install python ${python_version}
        done

|dagger| Contemporary Bourne shells include ``ash``, ``bash``, and ``zsh``.

*Why not use* `pyenv <https://github.com/pyenv/pyenv>`_ *?*

When one considers all of the other language-specific version
managers out there, such as `jEnv <https://www.jenv.be/>`_, `rbenv
<https://github.com/rbenv/rbenv>`_, and `tfenv
<https://github.com/tfutils/tfenv>`_, it becomes clear that having a single
version management interface reduces cognitive load on developers, as they only
need to remember one command-line interface and one file format for managed
versions. And, while this project may only be Python-specific, the practice of
using a more generalized version manager may cross to other projects.

`pipenv <https://pypi.org/project/pipenv>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you have done any significant amount of Python development
or have tried using Python on a machine where you do not have administrative
privileges, then you have probably encountered the concept of virtual
environments to provide sandboxes into which you can install packages.
Traditionally, you would have to create such virtual environments,
"activate" them, and then install packages into them. The creation of such an
environment may involve a tool,
like `virtualenv <https://virtualenv.pypa.io/en/latest>`_,
or the `venv <https://docs.python.org/3/library/venv.html>`_ module
that comes with all recent versions of Python 3. Activation of such an
environment typically involves using a shell script. And, installing
into an activated environment is commonly done by running
`pip <https://pypi.org/project/pip>`_ from within that environment.
All of that is a lot of work if you simply want to play in a sandbox
- and you do not even get reproducible installations for your hassle.

The pipenv_ tool is a very respectable solution to the above problems.
It creates a virtual environment and can transparently install packages
into it. Installed development dependencies and runtime dependencies
are both tracked as separate categories within a ``Pipfile``.
This grants portability and reproducibility of development
environments and removes the need to maintain various ``requirements.txt``
files. Furthermore, the ``pipenv shell`` and ``pipenv run`` commands are
very useful for iterating on dependency changes during development.
For these reasons, we strongly recommend installing and using this tool.

We provide a ``Pipfile`` in the top level of the project repository. After
you clone the project and have installed pipenv_, just run::

    pipenv sync --dev

to prepare a virtual environment for development.

To use certain development tools that we support, you may need to install
some packages with your OS package manager first:

.. tab:: apt

    .. code-block:: sh

        sudo apt update && sudo apt install gpg

`EditorConfig <https://editorconfig.org>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Most modern code editors support per-file type configuration via EditorConfig_.
This ensures that project standards for things, such as maximum line length,
trailing whitespace, and indentation are enforced without the need
for lots of editor-specific configurations to be distributed with the project.
We recommend that you install an EditorConfig plugin for your editor of choice,
if necessary. We provide an ``.editorconfig`` file at the top level
of the project repository; this file has configurations relevant
to the project.

Common Tasks
-------------------------------------------------------------------------------
During development, some tasks are repeated again and again.
And some tasks are dependent upon other tasks.
Traditionally, the :command:`make` command or a script or batch file
would be used to automate such tasks.
However, in to provide maximum portability
and to reduce the number of languages that a developer needs to remember,
we use a Python-native solution:
`invoke <https://www.pyinvoke.org/>`_.
The :command:`invoke` is available as part of the virtual environment
maintained by Pipenv for this project.

Instead of defining tasks in a ``Makefile``,
we instead define them as Python code in :file:`tasks`.
To see a summary of the available tasks, you can execute::

    pipenv run invoke --list

We recommend the use of :command:`invoke` rather than running tools directly,
since it performs environment sanitization
and other frequently-overlooked tasks automatically,
freeing you from fighting weird cache effects or various oversights,
such as validating URLs in documentation or linting tests.

Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

Internal API Documentation
-------------------------------------------------------------------------------

.. automodule:: lockup.base

Principles and Advices
-------------------------------------------------------------------------------

Assertions and Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Code style can be a surprisingly contentious issue. This project *does not* run
any style checker or code reformatter, such as `autopep8
<https://pypi.org/project/autopep8/>`_ or `black
<https://pypi.org/project/black/>`_. However, it is expected that patches will
follow a style similar to what is already present. Some basic guidance is
enforced via EditorConfig_, but mostly it is up to the patch submitter to try
to match the existing style. Though it is not perfect and good judgment will
still need to be exercised, you can execute the following on an uncommitted
patch to receive additional hints::

    pipenv run invoke check-code-style

Unwitting "offenses" in new code can be readily forgiven, but patches which
contain reformatting noise against existing code will almost certainly be
rejected. Please digest this `Stack Exchange discussion on reformatting
<https://softwareengineering.stackexchange.com/questions/226440/is-it-okay-to-make-coding-style-changes-on-an-open-source-project-that-doesnt-f>`_.

Some tips:

* Horizontal space between identifiers and literals improves legibility. Prior
  to the introduction of spaces between words around fourteen centuries ago,
  readers had to either parse words from `scriptio continua
  <https://en.wikipedia.org/wiki/Scriptio_continua>`_ or with the use of a
  `word divider <https://en.wikipedia.org/wiki/Word_divider>`_ symbol, such as
  the `interpunct <https://en.wikipedia.org/wiki/Interpunct>`_. Reading
  identifiers from code, which are separated only by delimiters, is equivalent
  to reading words separated by interpuncts, except that the cognitive load is
  even higher due to the variety of delimiters (parentheses, commas, colons,
  etc...). Using horizontal space, an innovation from nearly 1.5 millennia ago,
  can reduce this cognitive load.

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
