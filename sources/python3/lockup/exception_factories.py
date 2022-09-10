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


''' Factories to produce exceptions with standard message formats. '''


# Initialization Dependencies:
#   exception_factories -> nomenclature
# Latent Dependencies: (no cycles)


# TODO: Add 'exception_provider' argument to factories.


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from .exceptions import InaccessibleAttribute
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
    from .exceptions import IncorrectData
    return IncorrectData(
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation_label}" )

def create_attribute_nonexistence_exception( name, context ):
    ''' Creates error with context about nonexistent attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    #from .exceptions import InaccessibleAttribute
    return __.InaccessibleAttribute(
        f"Attempt to access nonexistent {label}." )

def create_attribute_immutability_exception(
    name, context, action = 'assign'
):
    ''' Creates error with context about immutable attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    from .exceptions import ImpermissibleAttributeOperation
    return ImpermissibleAttributeOperation(
        f"Attempt to {action} immutable {label}." )

def create_attribute_indelibility_exception( name, context ):
    ''' Creates error with context about indelible attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    from .exceptions import ImpermissibleAttributeOperation
    return ImpermissibleAttributeOperation(
        f"Attempt to delete indelible {label}." )

def create_class_attribute_rejection_exception( name, class_ ):
    ''' Creates error with context about class attribute rejection. '''
    label = __.calculate_class_label( class_, f"attribute '{name}'" )
    from .exceptions import ImpermissibleOperation
    return ImpermissibleOperation(
        f"Rejection of extant definition of {label}." )

def create_impermissible_instantiation_exception( class_ ):
    ''' Creates error with context about impermissible instantiation. '''
    label = __.calculate_class_label( class_ )
    from .exceptions import ImpermissibleOperation
    return ImpermissibleOperation(
        f"Impermissible instantiation of {label}." )

def create_implementation_absence_exception( invocation, variant_name ):
    ''' Creates error about absent implementation of invocable. '''
    invocation_label = __.calculate_invocable_label( invocation )
    from .exceptions import AbsentImplementation
    return AbsentImplementation(
        f"No implementation of {invocation_label} exists for {variant_name}." )

def create_invocation_validation_exception( invocation, cause ):
    ''' Creates error with context about invalid invocation. '''
    label = __.calculate_invocable_label( invocation )
    from .exceptions import IncorrectData
    return IncorrectData(
        f"Incompatible arguments for invocation of {label}: {cause}" )
