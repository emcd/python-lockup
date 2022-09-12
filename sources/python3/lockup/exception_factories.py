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


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    # 'calculate_label' needs to be imported early to prevent cycles between
    # 'Module.__getattribute__', which may raise 'AttributeError' as a normal
    # part of attribute lookup, and 'create_attribute_nonexistence_exception'.
    from .nomenclature import (
        calculate_argument_label,
        calculate_class_label,
        calculate_invocable_label,
        calculate_label,
    )


def create_argument_validation_exception(
    exception_provider, name, invocation, expectation_label
):
    ''' Creates error with context about invalid argument. '''
    from inspect import signature as scan_signature
    signature = scan_signature( invocation )
    argument_label = __.calculate_argument_label( name, signature )
    invocation_label = __.calculate_invocable_label( invocation )
    if not isinstance( expectation_label, str ):
        expectation_label = __.calculate_label( expectation_label )
    return exception_provider( 'IncorrectData' )(
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation_label}" )

def create_attribute_immutability_exception(
    exception_provider, name, context, action = 'assign'
):
    ''' Creates error with context about immutable attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleAttributeOperation' )(
        f"Attempt to {action} immutable {label}." )

def create_attribute_indelibility_exception(
    exception_provider, name, context
):
    ''' Creates error with context about indelible attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleAttributeOperation' )(
        f"Attempt to delete indelible {label}." )

def create_attribute_name_illegality_exception( exception_provider, name ):
    ''' Creates error about illegal attribute name. '''
    return exception_provider( 'IncorrectData' )(
        f"Attempt to access attribute with illegal name '{name}'." )

def create_attribute_nonexistence_exception(
    exception_provider, name, context
):
    ''' Creates error with context about nonexistent attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return exception_provider( 'InaccessibleAttribute' )(
        f"Attempt to access nonexistent {label}." )

def create_attribute_noninvocability_exception(
    exception_provider, name, context
):
    ''' Creates error with context about noninvocable attribute. '''
    label = __.calculate_label( context, f"attribute '{name}'" )
    return exception_provider( 'InvalidOperation' )(
        f"Attempt to invoke noninvocable {label}." )

def create_class_attribute_rejection_exception(
    exception_provider, name, class_
):
    ''' Creates error with context about class attribute rejection. '''
    label = __.calculate_class_label( class_, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleOperation' )(
        f"Rejection of extant definition of {label}." )

def create_fugitive_apprehension_exception(
    exception_provider, fugitive, invocation
):
    ''' Creates error with context about fugitive exception apprehension. '''
    exception_class_label = __.calculate_class_label( type( fugitive ) )
    invocation_label = __.calculate_invocable_label( invocation )
    return exception_provider( 'FugitiveException' )(
        f"Apprehension of fugitive exception of {exception_class_label} "
        f"at boundary of {invocation_label}." )

def create_impermissible_instantiation_exception(
    exception_provider, class_
):
    ''' Creates error with context about impermissible instantiation. '''
    label = __.calculate_class_label( class_ )
    return exception_provider( 'ImpermissibleOperation' )(
        f"Impermissible instantiation of {label}." )

def create_implementation_absence_exception(
    exception_provider, invocation, variant_name
):
    ''' Creates error about absent implementation of invocable. '''
    invocation_label = __.calculate_invocable_label( invocation )
    return exception_provider( 'AbsentImplementation' )(
        f"No implementation of {invocation_label} exists for {variant_name}." )

def create_invocation_validation_exception(
    exception_provider, invocation, cause
):
    ''' Creates error with context about invalid invocation. '''
    label = __.calculate_invocable_label( invocation )
    return exception_provider( 'IncorrectData' )(
        f"Incompatible arguments for invocation of {label}: {cause}" )

def create_nonexcoriable_exception_controller_exception(
    exception_provider, controller
):
    ''' Creates error about non-excoriable exception controller. '''
    label = __.calculate_label( controller )
    return exception_provider( 'IncorrectData' )(
        f"Impossible to excoriate exception controller from {label}." )
