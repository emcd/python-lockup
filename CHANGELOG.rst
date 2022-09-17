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

v2.0.0 (not released yet)
-------------------------------------------------------------------------------

API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Provide ``create_interception_decorator`` function which creates function
  decorators that apprehend "fugitive" exceptions before they escape across the
  boundary of a public API. Fugitive exceptions are exceptions which are
  unexpected and which should have been caught internally.

* Provide ``ExceptionController`` for use with
  ``create_interception_decorator`` and the validaton utilities. This allows
  you to define custom behaviors for how to handle fugitive exceptions and also
  to plug your own exception factories into the validator utilities.

* Provide ``reflect_class_factory_per_se`` function which allows for a class
  factory class ("metaclass") to be made into its own factory, similar to how
  `type <https://docs.python.org/3/library/functions.html#type>`_ behaves. This
  package uses it internally, when possible, to allow class factory classes to
  enforce attribute concealment and immutability on themselves and not just
  their instances. But, it can be put to other purposes too.

* Provide nomenclatural utilities which determine the classification of objects
  that are provided to them. These are useful for the creation of more helpful
  exception messages or log entries. This package internally uses the utilities
  to create descritpive exception messages.

* Provide validation utilities which return back the object they validation if
  the validation is successful. Otherwise, they raise a validation error. This
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

* Drop CPython 3.6.

* Add PyPy 3.9.

v1.1.0
-------------------------------------------------------------------------------

Documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Officially verify and mention PyPy and Pyston support.
