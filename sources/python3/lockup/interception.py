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


from .exceptionality import (
    our_exception_factory_provider as _our_exception_factory_provider,
)


# TODO: Create interception decorator factory for classes that will produce
#       class decorators which will attach function decorators to all public
#       and operational methods on a class.


def create_interception_decorator(
    exception_factory_provider, apprehender
): # pylint: disable=too-complex
    ''' Creates function decorator to apprehend "fugitive" exceptions.

        Takes an ``exception_factory_provider`` argument, which must behave as
        an exception factory provider as described in the
        :py:mod:`lockup.exceptions` module. This provider must be capable of
        providing an exception factory, which is indexed by the name
        ``invocation_validation`` and which has an interface that corresponds
        to
        :py:func:`lockup.exceptionality.our_factories.create_invocation_validation_exception`.

        Takes an ``apprehender`` argument, which must be a callable that
        accepts exactly two arguments and which returns two values. The first
        argument to the callable is expected to be an exception raised by the
        function wrapped by the decorator produced from this factory. The
        second argument to the callable is expected to be the function wrapped
        by the decorator. The first return value from the apprehender is
        expected to either be the expection that was passed to it or else
        ``None``. The second return value from the apprehender is expected to
        either be an another exception or else ``None``.

        If both return values from the apprehender are ``None``, then the
        apprehended exception will be returned directly rather than propagated
        as an exception. If the first return value from the apprehender is the
        apprehended exception and the second return value is ``None``, then
        propagation of the apprehended exception continues (i.e., it is
        re-raised). If the first return value from the apprehender is the
        apprehended exception and the second return value is another exception,
        then the other exception is propagated with the apprehended exception
        in its custody (i.e., its ``__cause__``). If the first return value is
        ``None`` and the second return value is another exception, then that
        exception is propagated instead of the originally apprehended one with
        no reference to the originally apprehended one. ''' # pylint: disable=line-too-long
    from .exceptionality import intercept_exception_factory_provider
    exception_factory_provider = intercept_exception_factory_provider(
        exception_factory_provider, create_interception_decorator )
    apprehender = intercept_fugitive_exception_apprehender(
        apprehender, create_interception_decorator )

    def intercept( invocation ):
        ''' Decorates function to apprehend fugitive exceptions. '''
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
            ''' Intercepts function invocations and apprehends fugitives. '''
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
    ''' Encloses fugitive apprehender with interceptor.

        Ensures that the apprehender follows protocol. '''
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
        # Ensure apprehender returns valid origin and custodian exceptions
        # without raising exception.
        try: origin, custodian = apprehender( *posargs, **nomargs )
        except BaseException as exc:
            raise _our_exception_factory_provider( 'fugitive_apprehension' )(
                exc, apprehender ) from exc
        valid = None is origin
        valid = valid or (
            isinstance( origin, BaseException )
            and arguments.args[ 0 ] is origin )
        if not valid:
            raise _our_exception_factory_provider( 'return_validation' )(
                apprehender, 'None or the original exception',
                position = 0 )
        valid = None is custodian or isinstance( custodian, BaseException )
        if not valid:
            raise _our_exception_factory_provider( 'return_validation' )(
                apprehender, 'None or instance of exception class',
                position = 1 )
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
    ''' Apprehends fugitive exceptions at API boundary.

        Used internally within this package. '''
    from .exceptions import Omniexception
    if isinstance( exception, Omniexception ): return exception, None
    return (
        exception,
        _our_exception_factory_provider( 'fugitive_apprehension' )(
            exception, invocation ) )


#: Intercepts invocations within this package.
our_interceptor = create_interception_decorator(
    _our_exception_factory_provider, our_fugitive_exception_apprehender )
