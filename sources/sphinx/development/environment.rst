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
Environment and Utilities
*******************************************************************************

`asdf <https://github.com/asdf-vm/asdf>`_
===============================================================================

We develop against one baseline version of the CPython reference
implementation; this is the first version listed in the ``.tool-versions``
file, located at the top level of the project repository. However, we also test
against successive minor versions beyond this baseline version, as well as
equivalent versions for alternative implementations. Those versions are listed
after the baseline version in the same file. This file is used by the excellent
asdf_ version manager to determine which versions of Python are considered
active for the project. We strongly recommend the use of asdf_ to manage
multiple versions of Python, if you use an operating system that is supported
by asdf_.

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
        asdf plugin add python
        asdf install python

|dagger| Contemporary Bourne shells include ``ash``, ``bash``, and ``zsh``.

Contrasts to Alternatives
-------------------------------------------------------------------------------

`pyenv <https://github.com/pyenv/pyenv>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When one considers all of the other language-specific version managers out
there, such as `jEnv <https://www.jenv.be/>`_, `rbenv
<https://github.com/rbenv/rbenv>`_, and `tfenv
<https://github.com/tfutils/tfenv>`_, it becomes clear that having a single
version management interface reduces cognitive load on developers, as only one
command-line interface needs to be remembered to manage versions. A
generalized version manager, such as asdf_, can be reused consistently across
all projects, regardless of their implementation language, whereas pyenv_
cannot.

`invoke <https://www.pyinvoke.org>`_
===============================================================================

Many common development tasks, such as running tests, pushing new commit tags,
uploading a new release, etc... can be automated. We use invoke_ to run such
automations. It has various nice features, such as the ability to tee standard
output streams, run commands in a pseudo-TTY, manage dependencies between tasks
... to name a few. The :file:`.local/sources/python3/devshim__tasks` directory
contains the various task definitions available for use within the project.
This package will be automatically installed to a local cache in the project
directory on the first time you run::

    python3 develop.py

You can use::

    python3 develop.py --list

to see a list of the available development tasks.

To use certain development tools that we support, you may need to install
some packages with your OS package manager first:

.. tab:: apt

    .. code-block:: sh

        sudo apt update && sudo apt install gpg rustc

Contrasts to Alternatives
-------------------------------------------------------------------------------

`make <https://www.gnu.org/software/make>`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* The Makefile language, while generally elegant and well-suited to
  deterministic workflows, such as software maintenance automation, is an
  additional language which must be remembered.

* While GNU Make is essentially ubiquitous in the Unix world, it is not
  available by default on Windows.  Moreover, Microsoft Nmake does not have
  entirely compatible syntax.  Dual maintenance of DOS/Windows batch files or
  Powershell scripts is also undesirable.

* As Python is a prerequisite for this project and we have the infrastructure
  to guarantee a particular software environment, we can ensure a specific
  version of :command:`invoke` is available.  We would have no similar
  assurance with a system-provided :command:`make` and cannot provide this
  command via the Python package ecosystem.

* We can avoid the use of commands, such as :command:`find`, which have
  platform-specific variations, and instead use equivalent standardized
  functions.  An additional benefit is that function invocations are within the
  same Python interpreter session, whereas command invocations have fork-exec
  overhead.

* Separate options can be passed for each of multiple targets to
  :command:`invoke`, whereas :command:`make` only consumes global options and
  variables.

* A summary of all available targets/subcommands along with brief descriptions
  can be listed by :command:`invoke`, whereas :command:`make` does not provide
  such a facility.

`EditorConfig <https://editorconfig.org>`_
===============================================================================

Most modern code editors support per-file type configuration via EditorConfig_.
This ensures that project standards for things, such as maximum line length,
trailing whitespace, and indentation are enforced without the need
for lots of editor-specific configurations to be distributed with the project.
We recommend that you install an EditorConfig plugin for your editor of choice,
if necessary. We provide an :file:`.editorconfig` file at the top level
of the project repository; this file has configurations relevant
to the project.

`pre-commit <https://pre-commit.com>`_
===============================================================================

As part of the development environment that we provide via Pipenv, there is the
pre-commit_ command. Among other things, this allows you to install
Git pre-commit hooks which will perform additional checks, such as TOML and
YAML linting, before recording a new commit. To use these hooks, you can run::

    pre-commit install --config sources/pre-commit.yaml
