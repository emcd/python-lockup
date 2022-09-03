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
# Latent Dependencies:
#   interception -> exceptions -> base -> interception
#   interception -> validators -> exceptions -> interception


def create_interception_decorator( exception_provider ):
    ''' Creates function decorator to intercept fugitive exceptions.

        Fugitive exceptions are ones which are not expected
        to cross an API boundary. '''
    from .validators import validate_argument_invocability
    validate_argument_invocability(
            exception_provider, 'exception_provider',
            create_interception_decorator )
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
            try: return invocation( *things, **sundry )
            except ( # pylint: disable=try-except-raise
                exception_provider( 'InvalidState' ),
                exception_provider( 'InvalidOperation' ),
            ): raise
            # Prevent escape of impermissible exceptions.
            except BaseException as exc: # pylint: disable=broad-except
                raise exception_provider( 'FugitiveException' ) from exc
        return interception_invoker
    return intercept