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

Changelog
===============================================================================

v2.0.0
-------------------------------------------------------------------------------

API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* No more separate API for package-internal development. Everything is now
  exposed as part of an auxiliary public API as opposed to the primary public
  API.

  .. note::

     Some parts of the auxiliary public API may be refactored into separate
     packages at a later point.

* Provide ``create_interception_decorator`` function which creates function
  decorators that can apprehend "fugitive" exceptions before they escape across
  the boundary of a public API. Fugitive exceptions are exceptions which are
  unexpected and which should have been caught internally.

* Provide ``reassign_class_factory`` function which allows for a class to be
  assigned a new factory class ("metaclass"). This can even be used on a class
  factory class itself, resulting in a factory class similar to how `type
  <https://docs.python.org/3/library/functions.html#type>`_ behaves. This
  package uses it internally, when possible, to allow class factory classes to
  enforce attribute concealment and immutability on themselves and not just
  their instances. But, it can be put to other purposes too.

* Provide exception management utilities, including factories which can inject
  labels into instances of a single omniexception class as an alternative to
  working with a class hierarchy. This package internally uses the utilities to
  create exceptions with descriptive messages and labels.

* Provide nomenclatural utilities which determine the classification of objects
  that are provided to them. These are useful for the creation of more helpful
  exception messages or log entries. This package internally uses the utilities
  to create descritpive exception messages. A suite of exception factories,
  which use these utilities, is also exposed.

* Provide validation utilities which return back their argument if the
  validation is successful. Otherwise, they raise a validation error. This
  allows for multiple validators to be fluently applied in succession. This
  package internally uses the validators on arguments to functions that are
  part of its public API.

* Provide visibility utilities which determine if an attribute is considered
  public or non-public and what attributes should be concealed on an object.
  This package uses the utilities internally to conceal non-public attributes
  on classes, modules, and namespaces. But, they can be put to other purposes
  as well.

Python Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Remove CPython 3.6 because it is past end-of-life.

* Deprecate Pyston because of its new development direction.

* Add PyPy 3.9.

v1.1.0
-------------------------------------------------------------------------------

Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Officially verify and mention PyPy and Pyston support.
