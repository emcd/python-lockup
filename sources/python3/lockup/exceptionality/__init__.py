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


# Latent Dependencies:
#   exceptionality -> nomenclature -> validators -> exceptionality
#   exceptionality -> validators -> exceptionality


from types import MappingProxyType as _DictionaryProxy
from ..validators import (
    validate_argument_class as _validate_argument_class,
    validate_argument_invocability as _validate_argument_invocability,
)


def our_exception_class_provider( name ):
    ''' Provides package-internal exception. '''
    from .. import exceptions
    from ..visibility import is_public_name
    if is_public_name( name ) and hasattr( exceptions, name ):
        exception_class = getattr( exceptions, name )
        if issubclass( exception_class, exceptions.Exception0 ): # pragma: no branch
            return exception_class
    raise our_exception_factory_provider( 'inaccessible_entity' )(
        name, 'name of available exception class' )


def our_exception_factory_provider( name ):
    ''' Provides package-internal exception factory. '''
    complete_name = f"create_{name}_exception"
    if complete_name in globals( ):
        # nosemgrep: local.scm-modules.semgrep-rules.python.lang.security.dangerous-globals-use
        exception_factory = globals( )[ complete_name ]
        from functools import partial as partial_function
        return partial_function(
            exception_factory, our_exception_class_provider )
    raise our_exception_factory_provider( 'inaccessible_entity' )(
        complete_name, 'name of available exception factory' )

_excfp = our_exception_factory_provider  # Internal alias.


class ExtraData:
    ''' Data transfer object for extra exception data. '''

    def __init__(
        self,
        positional_arguments = ( ),
        nominative_arguments = _DictionaryProxy( { } ),
        exception_labels = _DictionaryProxy( { } ),
    ):
        from collections.abc import Sequence, Mapping as Dictionary
        self.positional_arguments = tuple(
            _validate_argument_class(
                our_exception_factory_provider,
                positional_arguments, Sequence, 'positional_arguments',
                ExtraData ) )
        self.nominative_arguments = _DictionaryProxy(
            _validate_argument_class(
                our_exception_factory_provider,
                nominative_arguments, Dictionary, 'nominative_arguments',
                ExtraData ) )
        self.exception_labels = _DictionaryProxy(
            _validate_argument_class(
                our_exception_factory_provider,
                exception_labels, Dictionary, 'exception_labels',
                ExtraData ) )


def create_argument_validation_exception(
    exception_provider, name, invocation, expectation,
    extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid argument. '''
    sui = create_argument_validation_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    _validate_argument_invocability( _excfp, invocation, 'invocation', sui )
    _validate_argument_class( _excfp, expectation, str, 'expectation', sui )
    from ..nomenclature import (
        calculate_argument_label,
        calculate_invocable_label,
    )
    argument_label = calculate_argument_label( name, invocation )
    invocation_label = calculate_invocable_label( invocation )
    return _produce_exception(
        exception_provider, sui, 'IncorrectData',
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation}",
        extra_data )


def create_attribute_immutability_exception(
    exception_provider, name, object_, action = 'assign',
    extra_data = ExtraData( ),
):
    ''' Creates error with context about immutable attribute. '''
    sui = create_attribute_immutability_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    _validate_argument_class( _excfp, action, str, 'action', sui )
    from ..nomenclature import calculate_label
    label = calculate_label( object_, f"attribute '{name}'" )
    return _produce_exception(
        exception_provider, sui, 'ImpermissibleAttributeOperation',
        f"Attempt to {action} immutable {label}.",
        extra_data )


def create_attribute_indelibility_exception(
    exception_provider, name, object_, extra_data = ExtraData( ),
):
    ''' Creates error with context about indelible attribute. '''
    sui = create_attribute_indelibility_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    from ..nomenclature import calculate_label
    label = calculate_label( object_, f"attribute '{name}'" )
    return _produce_exception(
        exception_provider, sui, 'ImpermissibleAttributeOperation',
        f"Attempt to delete indelible {label}.",
        extra_data )


def create_attribute_name_illegality_exception(
    exception_provider, name, extra_data = ExtraData( ),
):
    ''' Creates error about illegal attribute name. '''
    sui = create_attribute_name_illegality_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    return _produce_exception(
        exception_provider, sui, 'IncorrectData',
        f"Attempt to access attribute with illegal name '{name}'.",
        extra_data )


def create_attribute_nonexistence_exception(
    exception_provider, name, object_,
    extra_context = None, extra_data = ExtraData( ),
):
    ''' Creates error with context about nonexistent attribute. '''
    sui = create_attribute_nonexistence_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    from ..nomenclature import calculate_label
    label = calculate_label( object_, f"attribute '{name}'" )
    if extra_context:
        _validate_argument_class(
            _excfp, extra_context, str, 'extra_context', sui )
        label = f"{label} {extra_context}"
    return _produce_exception(
        exception_provider, sui, 'InaccessibleAttribute',
        f"Attempt to access nonexistent {label}.",
        extra_data )


def create_attribute_noninvocability_exception(
    exception_provider, name, object_,
    extra_context = None, extra_data = ExtraData( ),
):
    ''' Creates error with context about noninvocable attribute. '''
    sui = create_attribute_noninvocability_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    from ..nomenclature import calculate_label
    label = calculate_label( object_, f"attribute '{name}'" )
    if extra_context:
        _validate_argument_class(
            _excfp, extra_context, str, 'extra_context', sui )
        label = f"{label} {extra_context}"
    return _produce_exception(
        exception_provider, sui, 'InvalidOperation',
        f"Attempt to invoke noninvocable {label}.",
        extra_data )


def create_class_attribute_rejection_exception(
    exception_provider, name, class_, extra_data = ExtraData( ),
):
    ''' Creates error with context about class attribute rejection. '''
    sui = create_class_attribute_rejection_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    from ..nomenclature import calculate_class_label
    label = calculate_class_label( class_, f"attribute '{name}'" )
    return _produce_exception(
        exception_provider, sui, 'ImpermissibleOperation',
        f"Rejection of extant definition of {label}.",
        extra_data )


def create_fugitive_apprehension_exception(
    exception_provider, fugitive, invocation, extra_data = ExtraData( ),
):
    ''' Creates error with context about fugitive exception apprehension. '''
    sui = create_fugitive_apprehension_exception
    _validate_argument_class(
        _excfp, fugitive, BaseException, 'fugitive', sui )
    _validate_argument_invocability( _excfp, invocation, 'invocation', sui )
    from ..nomenclature import (
        calculate_class_label,
        calculate_invocable_label,
    )
    exception_class_label = calculate_class_label( type( fugitive ) )
    invocation_label = calculate_invocable_label( invocation )
    return _produce_exception(
        exception_provider, sui, 'InvalidState',
        f"Apprehension of fugitive exception of {exception_class_label} "
        f"at boundary of {invocation_label}.",
        extra_data )


def create_impermissible_instantiation_exception(
    exception_provider, class_, extra_data = ExtraData( ),
):
    ''' Creates error with context about impermissible instantiation. '''
    sui = create_impermissible_instantiation_exception
    from ..nomenclature import calculate_class_label
    label = calculate_class_label( class_ )
    return _produce_exception(
        exception_provider, sui, 'ImpermissibleOperation',
        f"Impermissible instantiation of {label}.",
        extra_data )


def create_implementation_absence_exception(
    exception_provider, invocation, variant_name, extra_data = ExtraData( ),
):
    ''' Creates error about absent implementation of invocable. '''
    sui = create_implementation_absence_exception
    _validate_argument_invocability( _excfp, invocation, 'invocation', sui )
    _validate_argument_class(
        _excfp, variant_name, str, 'variant_name', sui )
    from ..nomenclature import calculate_invocable_label
    invocation_label = calculate_invocable_label( invocation )
    return _produce_exception(
        exception_provider, sui, 'AbsentImplementation',
        f"No implementation of {invocation_label} exists for {variant_name}.",
        extra_data )


def create_inaccessible_entity_exception(
    exception_provider, name, expectation, extra_data = ExtraData( ),
):
    ''' Creates error with context about inaccessible entity. '''
    sui = create_inaccessible_entity_exception
    _validate_argument_class( _excfp, name, str, 'name', sui )
    _validate_argument_class( _excfp, expectation, str, 'expectation', sui )
    return _produce_exception(
        exception_provider, sui, 'InvalidOperation',
        f"Impermissible attempt to access entity '{name}': "
        f"must access {expectation}",
        extra_data )


def create_invalid_state_exception(
    exception_provider, message, package_name, extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid state. '''
    sui = create_invalid_state_exception
    _validate_argument_class( _excfp, message, str, 'message', sui )
    _validate_argument_class( _excfp, package_name, str, 'package_name', sui )
    from ..nomenclature import calculate_apex_package_name
    apex_package_name = calculate_apex_package_name( package_name )
    return _produce_exception(
        exception_provider, sui, 'InvalidState',
        f"Invalid internal state! {message} "
        f"Please report to the '{apex_package_name}' package maintainers.",
        extra_data )


def create_invocation_validation_exception(
    exception_provider, invocation, cause, extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid invocation. '''
    sui = create_invocation_validation_exception
    _validate_argument_invocability( _excfp, invocation, 'invocation', sui )
    _validate_argument_class( _excfp, cause, str, 'cause', sui )
    from ..nomenclature import calculate_invocable_label
    label = calculate_invocable_label( invocation )
    return _produce_exception(
        exception_provider, sui, 'IncorrectData',
        f"Incompatible arguments for invocation of {label}: {cause}",
        extra_data )


def create_return_validation_exception(
    exception_provider, invocation, expectation, position = None,
    extra_data = ExtraData( ),
):
    ''' Creates error with context about invalid return value. '''
    sui = create_return_validation_exception
    _validate_argument_invocability( _excfp, invocation, 'invocation', sui )
    _validate_argument_class( _excfp, expectation, str, 'expectation', sui )
    from ..nomenclature import calculate_invocable_label
    invocation_label = calculate_invocable_label( invocation )
    if isinstance( position, ( int, str ) ):
        return_label = f"return value (position #{position})"
    else: return_label = "return value"
    return _produce_exception(
        exception_provider, sui, 'InvalidState',
        f"Invalid {return_label} from {invocation_label}: "
        f"must be {expectation}",
        extra_data )


def intercept_exception_factory_provider( provider, invocation ):
    ''' Encloses exception factory provider with interceptor. '''
    # TODO: Validate invocation.
    signature = _validate_exception_factory_provider( provider, invocation )
    from functools import wraps

    @wraps( provider )
    def invoker( *posargs, **nomargs ):
        ''' Ensures provider returns exception factory. '''
        # Validate that arguments correspond to signature.
        try: signature.bind( *posargs, **nomargs )
        except TypeError as exc:
            raise our_exception_factory_provider( 'invocation_validation' )(
                provider, str( exc ) ) from exc
        try: factory = provider( *posargs, **nomargs )
        except BaseException as exc:
            raise our_exception_factory_provider( 'fugitive_apprehension' )(
                exc, provider ) from exc
        return _intercept_exception_factory( factory, provider )

    return invoker


def _validate_exception_factory_provider( provider, invocation ):
    ''' Validates exception factory provider as invocation argument. '''
    from inspect import signature as scan_signature
    valid = callable( provider )
    if valid:
        signature = scan_signature( provider )
        valid = 1 == len( signature.parameters )
    if valid: return signature
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_factory_provider',
        invocation,
        'exception factory provider' )


def _intercept_exception_factory( factory, invocation ):
    ''' Encloses exception factory with interceptor. '''
    signature = _validate_exception_factory( factory, invocation )
    from functools import wraps

    @wraps( factory )
    def invoker( *posargs, **nomargs ):
        ''' Ensures exception factory returns exception. '''
        # Validate that arguments correspond to signature.
        try: signature.bind( *posargs, **nomargs )
        except TypeError as exc:
            raise our_exception_factory_provider( 'invocation_validation' )(
                factory, str( exc ) ) from exc
        # Ensure factory returns exception without raising exception.
        try: exception = factory( *posargs, **nomargs )
        except BaseException as exc:
            raise our_exception_factory_provider( 'fugitive_apprehension' )(
                exc, factory ) from exc
        if not isinstance( exception, BaseException ):
            raise our_exception_factory_provider( 'return_validation' )(
                factory, 'instance of exception class' )
        return exception

    return invoker


def _validate_exception_factory( factory, invocation ):
    ''' Validates exception factory provider as invocation argument. '''
    from inspect import signature as scan_signature
    if callable( factory ): return scan_signature( factory )
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_factory', invocation, 'exception factory' )


def _produce_exception(
    exception_class_provider, invocation, name, message, extra_data
):
    ''' Produces exception by provider with message and failure class. '''
    exception_class_provider = intercept_exception_class_provider(
        exception_class_provider, invocation )
    _validate_argument_class(
        _excfp, extra_data, ExtraData, 'extra_data', invocation )
    failure_class = ' '.join( invocation.__name__.split( '_' )[ 1 : -1 ] )
    return exception_class_provider( name )(
        message,
        *extra_data.positional_arguments,
        **_inject_exception_labels(
            extra_data, { 'failure class': failure_class } ) )


def intercept_exception_class_provider( provider, invocation ):
    ''' Encloses exception class provider with interceptor. '''
    # TODO: Validate invocation.
    signature = _validate_exception_class_provider( provider, invocation )
    from functools import wraps

    @wraps( provider )
    def invoker( *posargs, **nomargs ):
        ''' Ensures exception class provider returns exception class. '''
        # Validate that arguments correspond to signature.
        try: signature.bind( *posargs, **nomargs )
        except TypeError as exc:
            raise our_exception_factory_provider( 'invocation_validation' )(
                provider, str( exc ) ) from exc
        # Ensure provider returns exception class without raising exception.
        try: exception_class = provider( *posargs, **nomargs )
        except BaseException as exc:
            raise our_exception_factory_provider( 'fugitive_apprehension' )(
                exc, provider ) from exc
        from inspect import isclass as is_class
        valid = is_class( exception_class )
        valid = valid and issubclass( exception_class, BaseException )
        if not valid:
            raise our_exception_factory_provider( 'return_validation' )(
                provider, 'exception class' )
        return exception_class

    return invoker


def _validate_exception_class_provider( provider, invocation ):
    ''' Validates exception provider invocability and signature. '''
    from inspect import signature as scan_signature
    valid = callable( provider )
    if valid:
        signature = scan_signature( provider )
        valid = 1 == len( signature.parameters )
    if valid: return signature
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_class_provider', invocation, 'exception class provider' )


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
