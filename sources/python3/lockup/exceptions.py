# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Classes of exceptions emitted by the functionality of this package.

    :py:exc:`Omniexception` is the ancestor of all the exception classes. It
    has an ``exception_labels`` attribute which allows instances of it to bear
    information about exceptions beyond what a class alone can convey. As a
    principle, we try to avoid class hierarchies and instead use labels.
    However, sometimes the Python implementation or the test machinery expect
    exception classes which are explicitly subclassed from certain Python
    builtin exception classes. So, variants of the omniexception class, which
    are fused to necessary Python builtin exception classes, are also provided.
    Exceptions from the fused classes can be matched by their corresponding
    builtin exception classes or by their ancestral exception classes from this
    module:

    .. code-block:: python

        >>> import csv
        >>> type( csv )
        <class 'module'>
        >>> import lockup
        >>> from lockup.exceptions import InvalidOperation
        >>> lockup.reclassify_module( csv )
        >>> type( csv )
        <class 'lockup.module.Module'>
        >>> try: del csv.reader
        ... except AttributeError as exc: type( exc ).mro( )
        ...
        [<class 'lockup.exceptions.ImpermissibleAttributeOperation'>, <class 'lockup.exceptions.ImpermissibleOperation'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Omniexception'>, <class 'TypeError'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
        >>> try: del csv.reader
        ... except InvalidOperation as exc: pass
        ...
        >>> try: del csv.nonexistent_attribute
        ... except InvalidOperation as exc: type( exc ).mro( )
        ...
        [<class 'lockup.exceptions.InaccessibleAttribute'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Omniexception'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
    ''' # pylint: disable=line-too-long


# pylint: disable=too-many-ancestors


class Omniexception( BaseException ):
    ''' Base for all exceptions in the package. '''

    def __init__( self, *posargs, exception_labels = None, **nomargs ):
        from collections.abc import Mapping as Dictionary
        from types import MappingProxyType as DictionaryProxy
        self.exception_labels = (
            DictionaryProxy( exception_labels )
            if isinstance( exception_labels, Dictionary )
            else DictionaryProxy( { } ) )
        super( ).__init__( *posargs, **nomargs )

    # TODO: __repr__ which includes exception labels


#------------------------------ Object Interface -----------------------------#


class InvalidOperation( Omniexception, Exception ):
    ''' Complaint about invalid operation. '''


class AbsentImplementation( InvalidOperation, NotImplementedError ):
    ''' Complaint about attempt to execute nonexistent implementation. '''


class ImpermissibleOperation( InvalidOperation, TypeError ):
    ''' Complaint about impermissible operation. '''


class ImpermissibleAttributeOperation(
    ImpermissibleOperation, AttributeError
):
    ''' Complaint about impermissible attribute operation.

        Cannot use :py:exc:`ImpermissibleOperation` because some packages,
        such as Sphinx Autodoc, expect an :py:exc:`AttributeError`. '''


class InaccessibleAttribute( InvalidOperation, AttributeError ):
    ''' Complaint about attempt to retrieve inaccessible attribute.

        Cannot use :py:exc:`InvalidOperation` because some Python internals
        expect an :py:exc:`AttributeError`. '''


class IncorrectData( InvalidOperation, TypeError, ValueError ):
    ''' Complaint about incorrect data for invocation or operation. '''


#------------------------------- Internal State ------------------------------#


class InvalidState( Omniexception, RuntimeError ):
    ''' Alert about invalid internal state in the package. '''


# pylint: enable=too-many-ancestors
