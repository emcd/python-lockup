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

* Create ``develop.py`` script and manage Pythons on all platforms via that.
