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

.. image:: https://img.shields.io/pypi/pyversions/lockup
   :alt: Python Versions

.. image:: https://img.shields.io/pypi/v/lockup
   :alt: Project Version
   :target: https://pypi.org/project/lockup/

.. image:: https://github.com/emcd/python-lockup/actions/workflows/test.yaml/badge.svg?branch=master&event=push
   :alt: Tests Status
   :target: https://github.com/emcd/python-lockup/actions/workflows/test.yaml

.. image:: https://codecov.io/gh/emcd/python-lockup/branch/master/graph/badge.svg?token=PA9QI9RL63
   :target: https://app.codecov.io/gh/emcd/python-lockup

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

    >>> import math
    >>> math.pi = math.e
    >>> f"Oh no! π is {math.pi}"
    'Oh no! π is 2.718281828459045'
    >>> math.pi = 4 * math.atan( 1 )
    >>> import lockup
    >>> lockup.reclassify_module( math )
    >>> math.pi = math.e
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'pi' on module 'math'.
    >>> math.pi
    3.141592653589793

  .. code-block:: python

    >>> import lockup
    >>> ns = lockup.create_namespace( some_constant = 6 )
    >>> ns.some_constant = 13
    Traceback (most recent call last):
    ...
    lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'some_constant' on class 'lockup.Namespace'.

* Non-public attributes are **concealed**. Concealment means that functions,
  such as `dir <https://docs.python.org/3/library/functions.html#dir>`_, can
  report a subset of attributes that are intended for programmers to use
  (without directly exposing internals).

  .. code-block:: python

    >>> import lockup
    >>> class Demo( metaclass = lockup.Class ):
    ...     _foo = 'Semi-private class variable.'
    ...     hello = 'Public class variable.'
    ...     def __len__( self ): return 1
    ...
    >>> dir( Demo )
    ['hello']

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
	>>> os.EX_OK
	0
	>>> del os.EX_OK
	>>> os.EX_OK
	Traceback (most recent call last):
	...
	AttributeError: module 'os' has no attribute 'EX_OK'
	>>> os.EX_OK = 0
	>>> type( os )
	<class 'module'>

Now, let us see what protection it gains from becoming immutable:

.. code-block:: python

	>>> import os
	>>> import lockup
	>>> lockup.reclassify_module( os )
	>>> del os.EX_OK
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to delete indelible attribute 'EX_OK' on module 'os'.
	>>> os.EX_OK = 255
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'EX_OK' on module 'os'.
	>>> type( os )
	<class 'lockup.Module'>

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
    <class 'lockup.NamespaceClass'>
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

Reflection
-------------------------------------------------------------------------------

Have you ever wondered how the type of `type
<https://docs.python.org/3/library/functions.html#type>`_ can be type_ itself?
Have you ever had a need to make a class with a similar behavior?

.. code-block:: python

    >>> type( type )
    <class 'type'>

Well, we can:

.. code-block:: python

    >>> class Class( type ): pass
    ...
    >>> type( Class )
    <class 'type'>
    >>> import lockup
    >>> lockup.reflect_class_factory_per_se( Class, assert_implementation = False )
    <class '__main__.Class'>
    >>> type( Class )  # doctest: +SKIP
    <class '__main__.Class'>

The above technique is used internally within this package itself.

.. note::
   This function only works on some flavors of Python, such as the reference
   implementation (CPython) and Pyston, at present. You can still use this
   package on other flavors of Python, but the reflection operation may not be
   implemented.

Compatibility
===============================================================================

This package has been verified to work on the following Python implementations:

* `CPython <https://github.com/python/cpython>`_
* `PyPy <https://www.pypy.org/>`_
* `Pyston <https://www.pyston.org/>`_

It likely works on others as well, but please report if it does not.

.. TODO: https://github.com/oracle/graalpython
.. TODO: https://github.com/IronLanguages/ironpython3
.. TODO: https://github.com/RustPython/RustPython
