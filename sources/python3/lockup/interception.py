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


def create_interception_decorator( exception_provider ):
    ''' Creates function decorator to apprehend "fugitive" exceptions.

        Fugitive exceptions are exceptions which are not expected to cross the
        boundary of an API and which should have been caught internally.
        When the function apprehends a fugitive exception, it creates an
        instance of a class which officially denotes fugitive exceptions and
        chains the fugitive to its ``cause`` before propagating across the API
        boundary. A list of permissible exceptions is consulted to determine
        whether an exception is permissible, and thus allowed to propagate
        freely, or if it is a fugitive.

        The ``exception_provider`` argument must be a callable object, such as
        a function, which takes an exception name as an argument.  The
        exception name will be ``FugitiveException``; the provider must return
        a valid exception class.

        The ``exception_provider`` argument must have an attribute, named
        ``is_permissible_exception``. This attribute must be a callable object,
        such as a function, that takes an exception as an argument and returns
        a boolean value. '''
    from .validators import (
        validate_argument_invocability,
        validate_attribute_existence,
    )
    validate_argument_invocability(
        exception_provider, 'exception_provider',
        create_interception_decorator )
    validate_attribute_existence(
        'is_permissible_exception', exception_provider )
    # TODO: Validate attribute invocability.

    def intercept( invocation ):
        ''' Decorates function to intercept fugitive exceptions. '''
        validate_argument_invocability( invocation, 'invocation', intercept )
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
                raise exception_provider(
                    'create_invocation_validation_exception' )(
                        invocation, exc ) from exc
            # Invoke function. Apprehend fugitives as necessary.
            try: return invocation( *things, **sundry )
            except BaseException as exc: # pylint: disable=broad-except
                if exception_provider.is_permissible_exception( exc ): raise
                # TODO: Validate returned exception class.
                raise exception_provider( 'FugitiveException' ) from exc

        return interception_invoker

    return intercept
