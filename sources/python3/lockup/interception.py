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


# Initialization Dependencies: (none)
# Latent Dependencies: (no cycles)


# TODO: Create interception decorator factory for classes that will produce
#       class decorators which will attach function decorators to all public
#       and operational methods on a class.


def create_interception_decorator( exception_controller ): # pylint: disable=too-complex
    ''' Creates function decorator to apprehend "fugitive" exceptions.

        Fugitive exceptions are exceptions which are not expected to cross the
        boundary of an API and which should have been caught internally.
        When the function apprehends a fugitive exception, it creates an
        instance of a class which officially denotes fugitive exceptions and
        chains the fugitive to its ``cause`` before propagating across the API
        boundary. A list of permissible exceptions is consulted to determine
        whether an exception is permissible, and thus allowed to propagate
        freely, or if it is a fugitive. '''
    _validate_exception_controller( exception_controller )

    def intercept( invocation ):
        ''' Decorates function to intercept fugitive exceptions. '''
        from ._base import exception_controller as our_exception_controller
        from .validators import validate_argument_invocability
        validate_argument_invocability(
            our_exception_controller, invocation, 'invocation', intercept )
        from inspect import signature as scan_signature
        signature = scan_signature( invocation )
        from functools import wraps

        # https://github.com/returntocorp/semgrep-rules/issues/2367
        # nosemgrep: local.scm-modules.semgrep-rules.python.lang.maintainability.useless-inner-function
        @wraps( invocation )
        def interception_invoker( *things, **sundry ):
            # Validate that arguments correspond to function signature.
            try: signature.bind( *things, **sundry )
            except TypeError as exc:
                raise exception_controller.provide_factory(
                    'invocation_validation' )( invocation, exc ) from exc
            # Invoke function. Apprehend fugitives as necessary.
            try: return invocation( *things, **sundry )
            except BaseException as exc: # pylint: disable=broad-except
                behavior, propagand = exception_controller.apprehend_fugitive(
                    exc, invocation )
                # TODO: Use 'match' statement once Python 3.10 is baseline.
                if 'propagate-at-liberty' == behavior: raise
                if 'return' == behavior: return exc
                # TODO: Validate that propagand is exception.
                #       Use 'our_exception_controller'.
                if 'propagate-in-custody' == behavior: raise propagand from exc
                if 'silence-and-except' == behavior: raise propagand from None
                return propagand

        return interception_invoker

    return intercept


# TODO: Take invocation argument.
def _validate_exception_controller( controller ):
    ''' Validates alleged exception controller.

        Gives a free pass if it is the early internal exception controller.
        This is to prevent import cycles. '''
    from ._base import exception_controller as our_exception_controller
    if controller is our_exception_controller: return controller
    from .exceptionality import validate_exception_controller
    return validate_exception_controller( controller )
