Package Requirements Format
===============================================================================

* Comments which are part of the requiremets data structure, for ease of
  machine rewriting.

Tasks Interface Refinement
===============================================================================

* Remove pluralized versions of commands and use mutually-exclusive
  ``--all`` and ``--version`` flags with singular commands.

Testing Improvements
===============================================================================

* Build sdist and wheels as part of ``push`` command. Do not require sign them
  during a test run.

Windows Development Support
===============================================================================

* Investigate ``conda`` for environment management.
  If viable, then recommend its installation instead of ``asdf`` if the
  development environment is not a virtualized Linux, such as WSL.

* Create ``develop.py`` and manage Pythons on all platforms via that.

Remove Dependency on ``bump2version``
===============================================================================

* Can work directly with ``__version__`` for package and set ``version`` in
  :file:`pyproject.toml` to ``dynamic``.

* Will need to modify project version reader to support the ``dynamic`` field.

Remove Dependency on ``invoke``
===============================================================================

* Topological sort of tasks.

* Deduplication of tasks.

* Context managers for task execution.

* Pseudo-TTY support.

* Dynamic passing of arguments to subtasks.

* Surfacing parameters from subtasks.

* Handle via ``develop.py``.

Provide In-Tree PEP 517 Build Backend
===============================================================================

* Proxy to Setuptools 'build_meta' backend, once it supports the 'build_base'
  option.

* https://peps.python.org/pep-0517/#build-backend-interface

* https://setuptools.pypa.io/en/latest/build_meta.html#dynamic-build-dependencies-and-other-build-meta-tweaks

* https://github.com/pypa/setuptools/blob/main/setuptools/build_meta.py
