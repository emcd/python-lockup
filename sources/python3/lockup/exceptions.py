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
#   exceptions -> factories
#   exceptions -> nomenclature
# Latent Dependencies:
#   exceptions -> factories -> exceptions
# pylint: disable=cyclic-import


from .factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from ._base import package_name
    from .factories import Class
    from .nomenclature import (
        calculate_argument_label,
        calculate_class_label,
        calculate_invocable_label,
        # 'calculate_label' needs to be imported early to prevent cycles
        # between 'Module.__getattribute__', which may raise 'AttributeError'
        # as a normal part of attribute lookup, and
        # 'create_attribute_nonexistence_exception'.
        calculate_label,
    )


#============================ Exception Factories ============================#
# TODO: Move exception factories to separate internal module
#       or add exception provider as a mandatory argument.


def create_argument_validation_exception(
    name, invocation, expectation_label
):
    ''' Creates error with context about invalid argument. '''
    from inspect import signature as scan_signature
    signature = scan_signature( invocation )
    argument_label = __.calculate_argument_label( name, signature )
    invocation_label = __.calculate_invocable_label( invocation )
    if not isinstance( expectation_label, str ):
        expectation_label = __.calculate_label( expectation_label )
    return IncorrectData(
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation_label}" )

def create_attribute_nonexistence_exception( name, context ):
    ''' Creates error with context about nonexistent attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return InaccessibleAttribute(
        f"Attempt to access nonexistent {label}." )

def create_attribute_immutability_exception(
    name, context, action = 'assign'
):
    ''' Creates error with context about immutable attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return ImpermissibleAttributeOperation(
        f"Attempt to {action} immutable {label}." )

def create_attribute_indelibility_exception( name, context ):
    ''' Creates error with context about indelible attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return ImpermissibleAttributeOperation(
        f"Attempt to delete indelible {label}." )

def create_class_attribute_rejection_exception( name, class_ ):
    ''' Creates error with context about class attribute rejection. '''
    label = __.calculate_class_label( class_, f"attribute '{name}'" )
    return ImpermissibleOperation(
        f"Rejection of extant definition of {label}." )

def create_impermissible_instantiation_exception( class_ ):
    ''' Creates error with context about impermissible instantiation. '''
    label = __.calculate_class_label( class_ )
    return ImpermissibleOperation(
        f"Impermissible instantiation of {label}." )

def create_implementation_absence_exception( invocation, variant_name ):
    ''' Creates error about absent implementation of invocable. '''
    invocation_label = __.calculate_invocable_label( invocation )
    return AbsentImplementation(
        f"No implementation of {invocation_label} exists for {variant_name}." )

def create_invocation_validation_exception( invocation, cause ):
    ''' Creates error with context about invalid invocation. '''
    label = __.calculate_invocable_label( invocation )
    return IncorrectData(
        f"Incompatible arguments for invocation of {label}: {cause}" )


#================================= Exceptions ================================#


# pylint: disable=too-many-ancestors


class Exception0( BaseException, metaclass = __.Class ):
    ''' Base for all exceptions in the package. '''

    def __init__( self, *things, tags = None, **sundry ):
        from collections.abc import Mapping as Dictionary
        from types import MappingProxyType as DictionaryProxy
        self.tags = (
            DictionaryProxy( tags ) if isinstance( tags, Dictionary )
            else DictionaryProxy( { } ) )
        super( ).__init__( *things, **sundry )


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
    ''' Alert about invalid internal state in the package.

        Owner of problem: maintainers of this package. '''

    def __init__( self, supplement = None ):
        super( ).__init__( ' '.join( filter( None, (
            f"Invalid internal state encountered "
            f"in package '{__.package_name}'.",
            supplement,
            f"Please report this error to the package maintainers." ) ) ) )


class FugitiveException( InvalidState, RuntimeError ):
    ''' Alert about fugitive exception intercepted at API boundary.

        An fugitive exception is one which is not intended
        to be reported across the package API boundary.
        Fugitive exceptions include Python built-ins,
        such as :py:exc:`IndexError`. '''


# pylint: enable=too-many-ancestors
