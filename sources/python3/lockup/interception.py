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


''' Invocation boundary protection. '''


from .exception_factories import (
    our_exception_factory_provider as _our_exception_factory_provider,
)


# TODO: Create interception decorator factory for classes that will produce
#       class decorators which will attach function decorators to all public
#       and operational methods on a class.


def create_interception_decorator(
    exception_factory_provider, apprehender
): # pylint: disable=too-complex
    ''' Creates function decorator to apprehend "fugitive" exceptions.

        Fugitive exceptions are exceptions which are not expected to cross the
        boundary of an API and which should have been caught internally.
        When the function apprehends a fugitive exception, it creates an
        instance of a class which officially denotes fugitive exceptions and
        chains the fugitive to its ``cause`` before propagating across the API
        boundary. A list of permissible exceptions is consulted to determine
        whether an exception is permissible, and thus allowed to propagate
        freely, or if it is a fugitive. '''
    from .exception_factories import intercept_exception_factory_provider
    exception_factory_provider = intercept_exception_factory_provider(
        exception_factory_provider, create_interception_decorator )
    apprehender = intercept_fugitive_exception_apprehender(
        apprehender, create_interception_decorator )

    def intercept( invocation ):
        ''' Decorates function to intercept fugitive exceptions. '''
        from .validators import validate_argument_invocability
        validate_argument_invocability(
            _our_exception_factory_provider,
            invocation, 'invocation', intercept )
        from inspect import signature as scan_signature
        signature = scan_signature( invocation )
        from functools import wraps

        # https://github.com/returntocorp/semgrep-rules/issues/2367
        # nosemgrep: local.scm-modules.semgrep-rules.python.lang.maintainability.useless-inner-function
        @wraps( invocation )
        def interception_invoker( *posargs, **nomargs ):
            # Validate that arguments correspond to function signature.
            try: signature.bind( *posargs, **nomargs )
            except TypeError as exc:
                raise exception_factory_provider( 'invocation_validation' )(
                    invocation, str( exc ) ) from exc
            # Invoke function. Apprehend fugitives as necessary.
            try: return invocation( *posargs, **nomargs )
            except BaseException as exc: # pylint: disable=broad-except
                origin, custodian = apprehender( exc, invocation )
                if origin:
                    if custodian: raise custodian from origin
                    raise
                if custodian: raise custodian from None
                return exc

        return interception_invoker

    return intercept


def intercept_fugitive_exception_apprehender( apprehender, invocation ):
    ''' Encloses fugitive apprehender with interceptor. '''
    signature = _validate_fugitive_exception_apprehender(
        apprehender, invocation )
    from functools import wraps

    @wraps( apprehender )
    def invoker( *posargs, **nomargs ):
        ''' Ensures apprehender returns exception. '''
        # Validate that arguments correspond to signature.
        try: arguments = signature.bind( *posargs, **nomargs )
        except TypeError as exc:
            raise _our_exception_factory_provider( 'invocation_validation' )(
                apprehender, str( exc ) ) from exc
        # TODO: Validate arguments proper.
        # Ensure apprehender returns valid origin and custodian exceptions
        # without raising exception.
        try: origin, custodian = apprehender( *posargs, **nomargs )
        except BaseException as exc:
            raise _our_exception_factory_provider( 'fugitive_apprehension' )(
                exc, apprehender ) from exc
        # TODO: Add position information to return value exceptions.
        valid = None is origin
        valid = valid or (
            isinstance( origin, BaseException )
            and arguments.args[ 0 ] is origin )
        if not valid:
            raise _our_exception_factory_provider( 'return_validation' )(
                apprehender, 'None or the original exception' )
        valid = None is custodian or isinstance( custodian, BaseException )
        if not valid:
            raise _our_exception_factory_provider( 'return_validation' )(
                apprehender, 'None or instance of exception class' )
        return origin, custodian

    return invoker


def _validate_fugitive_exception_apprehender( apprehender, invocation ):
    ''' Validates fugitive exception apprehender as invocation argument. '''
    from inspect import signature as scan_signature
    valid = callable( apprehender )
    if valid:
        signature = scan_signature( apprehender )
        valid = 2 == len( signature.parameters )
    if valid: return signature
    raise _our_exception_factory_provider( 'argument_validation' )(
        'fugitive_exception_apprehender',
        invocation,
        'fugitive exception apprehender' )


def our_fugitive_exception_apprehender( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    from .exceptions import Exception0
    if isinstance( exception, Exception0 ): return exception, None
    return (
        exception,
        _our_exception_factory_provider( 'fugitive_apprehension' )(
            exception, invocation ) )


our_interceptor = create_interception_decorator(
    _our_exception_factory_provider, our_fugitive_exception_apprehender )
