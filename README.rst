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

.. TODO: Add row of status icons.

Enables the creation of classes, modules, and namespaces on which all
attributes are **immutable** and for which non-public attributes are concealed
(**visibility restriction**).  Immutability increases code safety by
discouraging monkey-patching and preventing accidental or deliberate changes to
state. Visibility restriction means that functions, like ``dir``, can report a
subset of attributes that are intended for programmers to use without exposing
internals.

Contents of this package are:

* A module class, which enforces immutability and visibility restriction upon
  module attributes. This module class can *replace* the standard Python module
  class *with a single line of code* in a module definition.

* A factory (metaclass) that creates classes, enforcing immutability and
  visibility restriction upon their attributes. (Just attributes on the
  classes, themsleves, are immutable and visibility-restricted and not
  attributes on the instances of the classes.)

* A factory that creates namespaces, enforcing immutability and visibility
  restriction upon their attributes.

.. TODO: Provide link to online documentation.

Quick Tour
===============================================================================

Module
-------------------------------------------------------------------------------

Let us consider the mutable `os <https://docs.python.org/3/library/os.html>`_
module from the Python standard library and how we can alter "constants" that
may be used in many places:

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

Class Factory
-------------------------------------------------------------------------------

Let us monkey-patch a mutable class:

	>>> import lockup
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
	>>> type( B )
	<class 'lockup.Class'>
	>>> del type( B ).__setattr__
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to delete indelible attribute '__setattr__' on class 'lockup.Class'.
	>>> issubclass( type( B ), type )
	True

Namespace Factory
-------------------------------------------------------------------------------

An alternative to `types.SimpleNamespace
<https://docs.python.org/3/library/types.html#types.SimpleNamespace>`_ is
provided. First, let us observe the behaviors on a standard namespace:

	>>> import types
	>>> sn = types.SimpleNamespace( run = lambda: 42 )
	>>> sn
	namespace(run=<function <lambda> at ...>)
	>>> sn.run( )
	42
	>>> type( sn )
	<class 'types.SimpleNamespace'>
	>>> dir( sn )
	['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'run']
	>>> sn.__dict__
	{'run': <function <lambda> at ...>}
	>>> type( sn.run )
	<class 'function'>
	>>> sn.run = lambda: 666
	>>> sn.run( )
	666
	>>> sn( )
	Traceback (most recent call last):
	...
	TypeError: 'types.SimpleNamespace' object is not callable

Now, let us compare those behaviors to an immutable namespace:

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

    >>> class __( metaclass = lockup.NamespaceClass ):
    ...     from os import O_RDONLY, O_RDWR
    ...
    >>> __.O_RDONLY
    0

The above technique is used internally within this package itself.

Exceptions
-------------------------------------------------------------------------------

Exceptions can be intercepted with appropriate builtin exception classes or
with package exception classes:

	>>> import os
	>>> import lockup
	>>> from lockup.exceptions import InvalidOperation
	>>> os.O_RDONLY
	0
	>>> lockup.reclassify_module( os )
	>>> try: os.O_RDONLY = 15
	... except AttributeError as exc:
	...     type( exc ).mro( )
	...
	[<class 'lockup.exceptions.ImpermissibleAttributeOperation'>, <class 'lockup.exceptions.ImpermissibleOperation'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Exception0'>, <class 'TypeError'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
	>>> try: os.does_not_exist
	... except InvalidOperation as exc:
	...     type( exc ).mro( )
	...
	[<class 'lockup.exceptions.InaccessibleAttribute'>, <class 'lockup.exceptions.InaccessibleEntity'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Exception0'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
