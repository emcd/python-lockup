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

*******************************************************************************
                                    lockup
*******************************************************************************

.. image:: https://img.shields.io/pypi/v/lockup
   :alt: Project Version
   :target: https://pypi.org/project/lockup/

.. image:: https://img.shields.io/pypi/status/lockup
   :alt: PyPI - Status
   :target: https://pypi.org/project/lockup/

.. image:: https://github.com/emcd/python-lockup/actions/workflows/test.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-lockup/actions/workflows/test.yaml

.. image:: https://codecov.io/gh/emcd/python-lockup/branch/master/graph/badge.svg?token=PA9QI9RL63
   :alt: Code Coverage
   :target: https://app.codecov.io/gh/emcd/python-lockup

.. image:: https://img.shields.io/pypi/pyversions/lockup
   :alt: Python Versions
   :target: https://pypi.org/project/lockup/

.. image:: https://img.shields.io/pypi/l/lockup
   :alt: Project License
   :target: https://github.com/emcd/python-lockup/blob/master/LICENSE.txt

`API Documentation (stable)
<https://python-lockup.readthedocs.io/en/stable/api.html>`_
|
`API Documentation (current) <https://emcd.github.io/python-lockup/api.html>`_
|
`Code of Conduct
<https://emcd.github.io/python-lockup/contribution.html#code-of-conduct>`_
|
`Contribution Guide <https://emcd.github.io/python-lockup/contribution.html>`_

Overview
===============================================================================

Enables the creation of classes, modules, and namespaces on which the following
properties are true:

* All attributes are **immutable**. Immutability increases code safety by
  discouraging monkey-patching and preventing changes to state, accidental or
  otherwise.

  .. code-block:: python

    >>> import getpass
    >>> def steal_password( prompt = 'Password: ', stream = None ):
    ...     pwned = getpass.getpass( prompt = prompt, stream = stream )
    ...     # Send host address, username, and password to Dark Web collector.
    ...     return pwned
    ...
    >>> import lockup
    >>> lockup.reclassify_module( getpass )
    >>> getpass.getpass = steal_password
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'getpass' on module 'getpass'.

  .. code-block:: python

    >>> import lockup
    >>> ns = lockup.create_namespace( some_constant = 6 )
    >>> ns.some_constant = 13
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'some_constant' on class 'lockup.Namespace'.

* Non-public attributes are **concealed**. Concealment means that the
  `dir <https://docs.python.org/3/library/functions.html#dir>`_ function will
  report a subset of attributes that are intended for programmers to use...
  without exposing internals.

  .. code-block:: python

    >>> import lockup
    >>> class Demo( metaclass = lockup.Class ):
    ...     _foo = 'Semi-private class variable.'
    ...     hello = 'Public class variable.'
    ...     def __len__( self ): return 1
    ...
    >>> dir( Demo )
    ['hello']

In addition to the above, the package also provides the ability to apprehend
"fugitive" exceptions attempting to cross API boundaries. Various auxiliary
functionalities are provided as well; these are used internally within the
package but are deemed useful enough for public consumption. Please see the
documentation for more details.

Quick Tour
===============================================================================

.. _`Class Factory`: https://python-lockup.readthedocs.io/en/stable/api.html#lockup.Class
.. _Module: https://python-lockup.readthedocs.io/en/stable/api.html#lockup.Module
.. _`Namespace Factory`: https://python-lockup.readthedocs.io/en/stable/api.html#lockup.NamespaceClass

Module_
-------------------------------------------------------------------------------

Let us consider the mutable `os <https://docs.python.org/3/library/os.html>`_
module from the Python standard library and how we can alter "constants" that
may be used in many places:

.. code-block:: python

    >>> import os
    >>> type( os )
    <class 'module'>
    >>> os.O_RDONLY
    0
    >>> os.O_RDONLY = os.O_RDWR
    >>> os.O_RDONLY
    2
    >>> os.O_RDONLY = 0

Now, let us see what protection it gains from becoming immutable:

.. code-block:: python

    >>> import os
    >>> import lockup
    >>> lockup.reclassify_module( os )
    >>> type( os )
    <class 'lockup.module.Module'>
    >>> # How? https://docs.python.org/3/reference/datamodel.html#customizing-module-attribute-access
    >>> os.O_RDONLY = os.O_RDWR
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'O_RDONLY' on module 'os'.
    >>> del os.O_RDONLY
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to delete indelible attribute 'O_RDONLY' on module 'os'.

`Class Factory`_
-------------------------------------------------------------------------------

Let us monkey-patch a mutable class:

.. code-block:: python

	>>> class A:
	...     def expected_functionality( self ): return 42
	...
	>>> a = A( )
	>>> a.expected_functionality( )
	42
	>>> def monkey_patch( self ):
	...     return 'I selfishly change behavior upon which other consumers depend.'
	...
	>>> A.expected_functionality = monkey_patch
	>>> a = A( )
	>>> a.expected_functionality( )
	'I selfishly change behavior upon which other consumers depend.'

Now, let us try to monkey-patch an immutable class:

.. code-block:: python

	>>> import lockup
	>>> class B( metaclass = lockup.Class ):
	...     def expected_functionality( self ): return 42
	...
	>>> b = B( )
	>>> b.expected_functionality( )
	42
	>>> def monkey_patch( self ):
	...     return 'I selfishly change behavior upon which other consumers depend.'
	...
	>>> B.expected_functionality = monkey_patch
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'expected_functionality' on class ...
	>>> del B.expected_functionality
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to delete indelible attribute 'expected_functionality' on class ...

.. note::
   Only class attributes are immutable. Instances of immutable classes will
   have mutable attributes without additional intervention beyond the scope of
   this package.

`Namespace Factory`_
-------------------------------------------------------------------------------

An alternative to `types.SimpleNamespace
<https://docs.python.org/3/library/types.html#types.SimpleNamespace>`_ is
provided. First, let us observe the behaviors on a standard namespace:

.. code-block:: python

	>>> import types
	>>> sn = types.SimpleNamespace( run = lambda: 42 )
	>>> sn
	namespace(run=<function <lambda> at ...>)
	>>> sn.run( )
	42
	>>> type( sn )
	<class 'types.SimpleNamespace'>
	>>> sn.__dict__
	{'run': <function <lambda> at ...>}
	>>> type( sn.run )
	<class 'function'>
	>>> sn.run = lambda: 666
	>>> sn.run( )
	666
	>>> sn( )  # doctest: +SKIP
	Traceback (most recent call last):
	...
	TypeError: 'types.SimpleNamespace' object is not callable

Now, let us compare those behaviors to an immutable namespace:

.. code-block:: python

    >>> import lockup
    >>> ns = lockup.create_namespace( run = lambda: 42 )
    >>> ns
    NamespaceClass( 'Namespace', ('object',), { ... } )
    >>> ns.run( )
    42
    >>> type( ns )
    <class 'lockup.factories.NamespaceClass'>
    >>> ns.__dict__
    mappingproxy({...})
    >>> type( ns.run )
    <class 'function'>
    >>> ns.run = lambda: 666
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'run' on class 'lockup.Namespace'.
    >>> ns.__dict__[ 'run' ] = lambda: 666
    Traceback (most recent call last):
    ...
    TypeError: 'mappingproxy' object does not support item assignment
    >>> ns( )
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleOperation: Impermissible instantiation of class 'lockup.Namespace'.

Also of note is that we can define namespace classes directly, allowing us to
capture imports for internal use in a module without publicly exposing them as
part of the module API, for example:

.. code-block:: python

    >>> import lockup
    >>> class __( metaclass = lockup.NamespaceClass ):
    ...     from os import O_RDONLY, O_RDWR
    ...
    >>> __.O_RDONLY
    0

The above technique is used internally within this package itself.

Interception
-------------------------------------------------------------------------------

If a particular exceptional condition is not anticipated in Python code, a
"fugitive" exception can escape across the boundary of a published API. If you
have told the consumers of the API that it will only emit certain classes of
exceptions, then consumers might not handle exceptions outside of the expected
classes, i.e., fugitive exceptions. If you apprehend all fugitives at the API
boundary, then you can guarantee to your consumers that they will only need to
anticipate certain classes of exceptions.

Here is an example with an interceptor, which includes fugitive exception
apprehension, that this package uses internally:

.. code-block:: python

    >>> from lockup.exceptions import InvalidState
    >>> from lockup.interception import our_interceptor
    >>> @our_interceptor
    ... def divide_by_zero( number ): return number / 0
    ...
    >>> try: divide_by_zero( 42 )
    ... except InvalidState as exc:
    ...     type( exc ), type( exc.__cause__ ), str( exc )
    ...
    (<class 'lockup.exceptions.InvalidState'>, <class 'ZeroDivisionError'>, "Apprehension of fugitive exception of class 'builtins.ZeroDivisionError' at boundary of function 'divide_by_zero' on module '__main__'.")

As can be seen, the ``ZeroDivisionError`` is in the custody of an exception
that is of an expected class.

You can create your own interceptors with custom fugitive apprehension
behaviors using the ``create_interception_decorator`` function.

Compatibility
===============================================================================

This package has been verified to work on the following Python implementations:

* `CPython <https://github.com/python/cpython>`_

  - Complete functionality.

  - Support for interpreters compiled with ``Py_TRACE_REFS`` definition.

* `PyPy <https://www.pypy.org/>`_

  - Complete functionality except for reflection.

  - Reflection is a no-op if ``assert_implementation`` is ``False``.

* `Pyston <https://www.pyston.org/>`_

  - Complete functionality.

  .. warning::

     Support for Pyston may disappear in the future as the maintainers have
     decided to invest in a JIT module for CPython rather than a separate
     implementation.

It likely works on others as well, but please report if it does not.

.. TODO: https://github.com/facebookincubator/cinder
.. TODO: https://github.com/oracle/graalpython
.. TODO: https://github.com/IronLanguages/ironpython3
.. TODO: https://github.com/RustPython/RustPython

.. TODO: https://pypi.org/project/Cython/
.. TODO: https://pypi.org/project/Nuitka/
.. TODO: https://pypi.org/project/numba/
.. TODO: https://pypi.org/project/pyston-lite/
.. TODO: https://pypi.org/project/taichi/

`More Flair <https://www.imdb.com/title/tt0151804/characters/nm0431918>`_
===============================================================================
...than the required minimum

.. image:: https://img.shields.io/github/last-commit/emcd/python-lockup
   :alt: GitHub last commit
   :target: https://github.com/emcd/python-lockup

.. image:: https://img.shields.io/badge/security-bandit-yellow.svg
   :alt: Security Status
   :target: https://github.com/PyCQA/bandit

.. image:: https://img.shields.io/badge/linting-pylint-yellowgreen
   :alt: Static Analysis Status
   :target: https://github.com/PyCQA/pylint

.. image:: https://img.shields.io/pypi/implementation/lockup
   :alt: PyPI - Implementation
   :target: https://pypi.org/project/lockup/

.. image:: https://img.shields.io/pypi/wheel/lockup
   :alt: PyPI - Wheel
   :target: https://pypi.org/project/lockup/
