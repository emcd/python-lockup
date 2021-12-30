Dissolution of Pipenv Dependency
===============================================================================

Why
-------------------------------------------------------------------------------

* Significant difficulties with Pipenv installed in CPython 3.10 and in PyPy3
  virtual environments. Vendored dependencies in Pipenv sources are out-of-sync
  with current Python versions and the full breadth of common environment
  combinations does not seem to be tested.

* Ridiculously slow dependency resolution.

* Uses ``pexpect.interact`` as an intermediary for interactive shell, which
  sometimes does not play nicely with other programs that interact with the raw
  TTY device, such as GPG ``pinentry``.

Why Not
-------------------------------------------------------------------------------

* Will lose the convenience of ``pipenv shell``. Will need to make many Invoke
  tasks aware of "current virtual environment" perhaps.

* Will lose dependency freezing - at least until a replacement is developed,
  possibly using ``pip freeze`` and ``pip hash`` or something from ``distlib``.

Plan
-------------------------------------------------------------------------------

* Recommend installation of ``invoke`` via ``pipx``. We will use ``invoke`` to
  perform development environment maintenance instead of ``pipenv``.

* Create ``invoke bootstrap`` to configure development environment.
  - ``asdf install`` all desired Pythons.
  - Create virtual environment corresponding to each desired Python.
  - ``pip install`` all development packages in virtual environment
    corresponding to each desired Python.
  - Setup Git pre-commit hooks.

* Virtual environments stored in project ``caches`` directory.
  - Maybe add a cleaner task for them.
  - Name according to wheel-like ABI identifier.
  - Add selection for "current virtual environment". Assume first entry in
    ``.tool-versions``, coupled with platform, if one not explicitly selected.

* Move project metadata from ``setup.cfg`` into PEP 621-compliant
  ``pyproject.toml`` sections. Read this with ``tomli`` from ``setup.py``.

* Move project dependencies from ``setup.cfg`` into
  ``sources/dependencies.toml`` with PEP 631-like dependency specifications,
  but with proper support for development dependencies. Read this with
  ``tomli`` from ``setup.py``.

Windows Development Support
===============================================================================

* Investigate ``conda`` for environment management.
  If viable, then recommend its installation instead of ``asdf`` if the
  development environment is not a virtualized Linux, such as WSL.

Dissolution of Tox Dependency
===============================================================================

Why
-------------------------------------------------------------------------------

* Removal of restrictive, domain-specific configuration via an INI file, in
  favor of programming the test suite in Python.

* Removal of a development dependency, which can be replaced with a more
  elegant and targeted implementation on top of ``invoke``.

Alternatives
-------------------------------------------------------------------------------

* Nox. Maybe, but does not seem worth the effort, compared to Invoke.
