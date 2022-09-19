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
#   exception_factories -> _base
#   exception_factories -> nomenclature
#   exception_factories -> validators
# Latent Dependencies: (no cycles)


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from collections.abc import Sequence, Mapping as Dictionary
    from types import MappingProxyType as DictionaryProxy

    from ._base import intercept, exception_controller as excc
    from .class_factories import Class
    # 'calculate_label' needs to be imported early to prevent cycles between
    # 'Module.__getattribute__', which may raise 'AttributeError' as a normal
    # part of attribute lookup, and 'create_attribute_nonexistence_exception'.
    from .nomenclature import (
        calculate_argument_label,
        calculate_class_label,
        calculate_invocable_label,
        calculate_label,
    )
    from .validators import (
        validate_argument_class,
        validate_argument_invocability,
    )


class ExtraData( metaclass = __.Class ):
    ''' Data transfer object for extra exception data. '''

    def __init__(
        self,
        positional_arguments = ( ),
        nominative_arguments = __.DictionaryProxy( { } ),
        exception_labels = __.DictionaryProxy( { } ),
    ):
        self.positional_arguments = tuple(
            __.validate_argument_class(
                __.excc,
                positional_arguments, __.Sequence, 'positional_arguments',
                ExtraData ) )
        self.nominative_arguments = __.DictionaryProxy(
            __.validate_argument_class(
                __.excc,
                nominative_arguments, __.Dictionary, 'nominative_arguments',
                ExtraData ) )
        self.exception_labels = __.DictionaryProxy(
            __.validate_argument_class(
                __.excc,
                exception_labels, __.Dictionary, 'exception_labels',
                ExtraData ) )


@__.intercept # type: ignore[has-type]
def create_argument_validation_exception(
    exception_provider, name, invocation, expectation,
    extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid argument. '''
    sui = create_argument_validation_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    __.validate_argument_invocability( __.excc, invocation, 'invocation', sui )
    __.validate_argument_class( __.excc, expectation, str, 'expectation', sui )
    argument_label = __.calculate_argument_label( name, invocation )
    invocation_label = __.calculate_invocable_label( invocation )
    return exception_provider( 'IncorrectData' )(
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation}",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'invalid argument' } ) )


@__.intercept # type: ignore[has-type]
def create_attribute_immutability_exception(
    exception_provider, name, object_, action = 'assign',
    extra_data = ExtraData( ),
):
    ''' Creates error with context about immutable attribute. '''
    sui = create_attribute_immutability_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    __.validate_argument_class( __.excc, action, str, 'action', sui )
    label = __.calculate_label( object_, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleAttributeOperation' )(
        f"Attempt to {action} immutable {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'attribute immutability' } ) )


@__.intercept # type: ignore[has-type]
def create_attribute_indelibility_exception(
    exception_provider, name, object_, extra_data = ExtraData( ),
):
    ''' Creates error with context about indelible attribute. '''
    sui = create_attribute_indelibility_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    label = __.calculate_label( object_, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleAttributeOperation' )(
        f"Attempt to delete indelible {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'attribute indelibility' } ) )


@__.intercept # type: ignore[has-type]
def create_attribute_name_illegality_exception(
    exception_provider, name, extra_data = ExtraData( ),
):
    ''' Creates error about illegal attribute name. '''
    sui = create_attribute_name_illegality_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    return exception_provider( 'IncorrectData' )(
        f"Attempt to access attribute with illegal name '{name}'.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'illegal attribute name' } ) )


@__.intercept # type: ignore[has-type]
def create_attribute_nonexistence_exception(
    exception_provider, name, object_, extra_data = ExtraData( ),
):
    ''' Creates error with context about nonexistent attribute. '''
    sui = create_attribute_nonexistence_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    label = __.calculate_label( object_, f"attribute '{name}'" )
    return exception_provider( 'InaccessibleAttribute' )(
        f"Attempt to access nonexistent {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'attribute nonexistence' } ) )


@__.intercept # type: ignore[has-type]
def create_attribute_noninvocability_exception(
    exception_provider, name, object_, extra_data = ExtraData( ),
):
    ''' Creates error with context about noninvocable attribute. '''
    sui = create_attribute_noninvocability_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    label = __.calculate_label( object_, f"attribute '{name}'" )
    return exception_provider( 'InvalidOperation' )(
        f"Attempt to invoke noninvocable {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'attribute noninvocability' } ) )


@__.intercept # type: ignore[has-type]
def create_class_attribute_rejection_exception(
    exception_provider, name, class_, extra_data = ExtraData( ),
):
    ''' Creates error with context about class attribute rejection. '''
    sui = create_class_attribute_rejection_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class( __.excc, name, str, 'name', sui )
    label = __.calculate_class_label( class_, f"attribute '{name}'" )
    return exception_provider( 'ImpermissibleOperation' )(
        f"Rejection of extant definition of {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'class attribute rejection' } ) )


@__.intercept # type: ignore[has-type]
def create_fugitive_apprehension_exception(
    exception_provider, fugitive, invocation, extra_data = ExtraData( ),
):
    ''' Creates error with context about fugitive exception apprehension. '''
    sui = create_fugitive_apprehension_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_class(
        __.excc, fugitive, BaseException, 'fugitive', sui )
    __.validate_argument_invocability( __.excc, invocation, 'invocation', sui )
    exception_class_label = __.calculate_class_label( type( fugitive ) )
    invocation_label = __.calculate_invocable_label( invocation )
    return exception_provider( 'FugitiveException' )(
        f"Apprehension of fugitive exception of {exception_class_label} "
        f"at boundary of {invocation_label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'fugitive apprehension' } ) )


@__.intercept # type: ignore[has-type]
def create_impermissible_instantiation_exception(
    exception_provider, class_, extra_data = ExtraData( ),
):
    ''' Creates error with context about impermissible instantiation. '''
    sui = create_impermissible_instantiation_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    label = __.calculate_class_label( class_ )
    return exception_provider( 'ImpermissibleOperation' )(
        f"Impermissible instantiation of {label}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'impermissible instantiation' } ) )


@__.intercept # type: ignore[has-type]
def create_implementation_absence_exception(
    exception_provider, invocation, variant_name, extra_data = ExtraData( ),
):
    ''' Creates error about absent implementation of invocable. '''
    sui = create_implementation_absence_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_invocability( __.excc, invocation, 'invocation', sui )
    __.validate_argument_class(
        __.excc, variant_name, str, 'variant_name', sui )
    invocation_label = __.calculate_invocable_label( invocation )
    return exception_provider( 'AbsentImplementation' )(
        f"No implementation of {invocation_label} exists for {variant_name}.",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'implementation absence' } ) )


@__.intercept # type: ignore[has-type]
def create_invocation_validation_exception(
    exception_provider, invocation, cause, extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid invocation. '''
    sui = create_implementation_absence_exception
    _validate_standard_arguments( sui, exception_provider, extra_data )
    __.validate_argument_invocability( __.excc, invocation, 'invocation', sui )
    __.validate_argument_class( __.excc, cause, str, 'cause', sui )
    label = __.calculate_invocable_label( invocation )
    return exception_provider( 'IncorrectData' )(
        f"Incompatible arguments for invocation of {label}: {cause}",
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': 'invocation validation' } ) )


def _validate_standard_arguments( invocation, exception_provider, extra_data ):
    ''' Validates standard arguments to exception factory. '''
    _validate_exception_provider( exception_provider, invocation )
    __.validate_argument_class(
        __.excc, extra_data, ExtraData, 'extra_data', invocation )


def _validate_exception_provider( provider, invocation ):
    ''' Validates exception provider invocability and signature. '''
    # TODO: Validate signature.
    if callable( provider ): return provider
    raise __.excc.provide_factory( 'argument_validation' )(
        'exception_provider', invocation, 'exception provider' )


def _inject_exception_labels( extra_data, exception_labels ):
    ''' Injects exception labels into dictionary of nominative arguments.

        If the 'exception_labels' key already exists, does nothing.
        Also updates the 'exception_labels' entry with extra user-supplied
        exception labels. '''
    extra_arguments = extra_data.nominative_arguments
    if 'exception_labels' in extra_arguments: return extra_arguments
    extra_arguments = extra_arguments.copy( )
    extra_arguments[ 'exception_labels' ] = exception_labels
    extra_arguments[ 'exception_labels' ].update( extra_data.exception_labels )
    return extra_arguments
