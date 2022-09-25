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


''' :py:exc:`Exception0` is the ancestor of all exceptions from this package.

    These exceptions can be matched by corresponding builtin exception classes
    or by their ancestral exception classes from this module:

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
        [<class 'lockup.exceptions.ImpermissibleAttributeOperation'>, <class 'lockup.exceptions.ImpermissibleOperation'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Exception0'>, <class 'TypeError'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
        >>> try: del csv.reader
        ... except InvalidOperation as exc: pass
        ...
        >>> try: del csv.nonexistent_attribute
        ... except InvalidOperation as exc: type( exc ).mro( )
        ...
        [<class 'lockup.exceptions.InaccessibleAttribute'>, <class 'lockup.exceptions.InaccessibleEntity'>, <class 'lockup.exceptions.InvalidOperation'>, <class 'lockup.exceptions.Exception0'>, <class 'AttributeError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>]
    ''' # pylint: disable=line-too-long


# Initialization Dependencies:
#   exceptions -> _base
# Latent Dependencies: (no cycles)


# pylint: disable=too-many-ancestors


class Exception0( BaseException ):
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

    # TODO: Attribute protection.


#------------------------------ Object Interface -----------------------------#


class InvalidOperation( Exception0, Exception ):
    ''' Complaint about invalid operation. '''


class AbsentImplementation( Exception0, NotImplementedError ):
    ''' Complaint about attempt execute nonexistent implementation. '''


class ImpermissibleOperation( InvalidOperation, TypeError ):
    ''' Complaint about impermissible operation. '''


class ImpermissibleAttributeOperation(
    ImpermissibleOperation, AttributeError
):
    ''' Complaint about impermissible attribute operation.

        Cannot use :py:exc:`ImpermissibleOperation` because some packages,
        such as Sphinx Autodoc, expect an :py:exc:`AttributeError`. '''


class InaccessibleEntity( InvalidOperation ):
    ''' Complaint about attempt to retrieve inaccessible entity. '''


class InaccessibleAttribute( InaccessibleEntity, AttributeError ):
    ''' Complaint about attempt to retrieve inaccessible attribute.

        Cannot use :py:exc:`InaccessibleEntity` because some Python internals
        expect an :py:exc:`AttributeError`. '''


class IncorrectData( InvalidOperation, TypeError, ValueError ):
    ''' Complaint about incorrect data for invocation or operation. '''


#------------------------------- Internal State ------------------------------#


class InvalidState( Exception0, Exception ):
    ''' Alert about invalid internal state in the package. '''

    # TODO: Implement factory for this.
    #def __init__( self, supplement = None ):
    #    from ._base import package_name
    #    super( ).__init__( ' '.join( filter( None, (
    #        f"Invalid internal state encountered "
    #        f"in package '{package_name}'.",
    #        supplement,
    #        f"Please report this error to the package maintainers." ) ) ) )


class FugitiveException( InvalidState, RuntimeError ):
    ''' Alert about fugitive exception intercepted at API boundary.

        An fugitive exception is one which is not intended
        to be reported across the package API boundary.
        Fugitive exceptions include Python built-ins,
        such as :py:exc:`IndexError`. '''


# pylint: enable=too-many-ancestors
