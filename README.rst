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

.. todo:: Add row of status icons.

Enables the creation of safer modules and namespaces with cleaner programming
interfaces.

Contents of this package are:

* A module class which enforces **immutability** and **visibility restriction**
  upon module attributes, thereby allowing module authors to guarantee state
  and discourage the use of internal machinery by consumers. The module class
  can *replace* the standard Python module class *with a single line of code*
  in a module definition.

* A factory (metaclass) that creates **immutable** classes. (Just the classes
  themsleves are immutable and not the instances of the classes.)

* A factory that creates **immutable** namespaces, which also provide **inert
  access** to their attributes, meaning that no descriptor protocol, such as
  method binding, intercepts attribute accesses.

.. todo:: Provide link to online documentation.

Quick Tour
===============================================================================

Module immutability prevents tampering with critical module state:

	>>> import lockup
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

Immutable classes provide resistance to monkey-patching:

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
	>>> class B( metaclass = lockup.PrimalClassFactory ):
	...     def expected_functionality( self ): return 42
	...
	>>> b = B( )
	>>> b.expected_functionality( )
	42
	>>> B.expected_functionality = monkey_patch
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'expected_functionality' on class ...
	>>> type( B )
	<class 'lockup.PrimalClassFactory'>
	>>> del type( B ).__setattr__
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to delete indelible attribute '__setattr__' on class 'lockup.PrimalClassFactory'.
	>>> type( type( B ) )
	<class 'lockup.PrimalClassFactory'>
	>>> issubclass( type( B ), type )
	True

An alternative to :py:class:`types.SimpleNamespace` is available.
This alternative is immutable and restricts visibility to public attributes:

	>>> import lockup
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
	>>> class NS( metaclass = lockup.NamespaceFactory ):
	...     def run( ): return 42
	...
	>>> NS.run( )
	42
	>>> type( NS )
	<class 'lockup.NamespaceFactory'>
	>>> dir( NS )
	['run']
	>>> NS.__dict__
	mappingproxy(...)
	>>> type( NS.run )
	<class 'function'>
	>>> NS.run = lambda: 666
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'run' on class ...
	>>> NS.__dict__[ 'run' ] = lambda: 666
	Traceback (most recent call last):
	...
	TypeError: 'mappingproxy' object does not support item assignment
	>>> NS( )
	Traceback (most recent call last):
	...
	lockup.exceptions.ImpermissibleOperation: Impermissible instantiation of class ...

Exceptions can be intercepted with appropriate builtin exception classes or
with package exception classes:

	>>> import lockup
	>>> from lockup.exceptions import InvalidOperation
	>>> import os
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
