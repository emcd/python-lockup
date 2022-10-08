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


''' General interceptors and validators for exception management utilities. '''


# Latent Dependencies:
#   general -> ours -> general
# pylint: disable=cyclic-import


def intercept_exception_factory_provider( provider, invocation ):
    ''' Encloses exception factory provider with interceptor. '''
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )
    from ..validators import validate_argument_invocability
    validate_argument_invocability(
        our_exception_factory_provider,
        invocation, 'invocation', intercept_exception_factory_provider )
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
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_factory_provider',
        invocation,
        'exception factory provider' )


def _intercept_exception_factory( factory, invocation ):
    ''' Encloses exception factory with interceptor. '''
    signature = _validate_exception_factory( factory, invocation )
    from functools import wraps
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )

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
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_factory', invocation, 'exception factory' )


def intercept_exception_class_provider( provider, invocation ):
    ''' Encloses exception class provider with interceptor. '''
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )
    from ..validators import validate_argument_invocability
    validate_argument_invocability(
        our_exception_factory_provider,
        invocation, 'invocation', intercept_exception_class_provider )
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
    from .our_factories import (
        provide_exception_factory as our_exception_factory_provider,
    )
    raise our_exception_factory_provider( 'argument_validation' )(
        'exception_class_provider', invocation, 'exception class provider' )
