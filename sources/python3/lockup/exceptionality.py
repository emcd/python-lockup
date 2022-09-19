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


''' Facilities for exception production and control. '''


# Initialization Dependencies:
#   exceptionality -> class_factories
#   exceptionality -> exception_factories
#   exceptionality -> exceptions
# Latent Dependencies: (no cycles)


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from functools import partial as partial_function
    from types import MappingProxyType as DictionaryProxy

    from . import exception_factories, exceptions
    from .class_factories import Class
    from .visibility import is_public_name


class ExceptionController( metaclass = __.Class ):
    ''' Presents uniform interface for exception control. '''

    def __init__( self, factory_provider, fugitive_apprehender ):
        # TODO: Validate arguments.
        self.provide_factory = factory_provider
        self.apprehend_fugitive = fugitive_apprehender
        validate_exception_controller( self )

    # TODO: Protect against attribute mutation and deletion
    #       after initialization.


# Cannot wildcard import 'exceptions' module into a namespace,
# so we use immutable dictionary instead.
_our_exceptions = __.DictionaryProxy( {
    aname: getattr( __.exceptions, aname ) for aname in dir( __.exceptions )
    if __.is_public_name( aname )
} )


def our_fugitive_apprehender( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, tuple( _our_exceptions.values( ) ) ):
        return 'propagate-at-liberty', None
    return (
        'propagate-in-custody',
        our_exception_factory_provider( 'fugitive_apprehension' )(
            exception, invocation ) )


def our_exception_provider( name ):
    ''' Returns exception by name. '''
    return _our_exceptions[ name ]


# Cannot wildcard import 'exception_factories' module into a namespace,
# so we use immutable dictionary instead.
_our_exception_factories = __.DictionaryProxy( {
    aname: getattr( __.exception_factories, aname )
    for aname in dir( __.exception_factories )
    if __.is_public_name( aname ) and aname.startswith( 'create_' )
} )


def our_exception_factory_provider( name ):
    ''' Returns exception factory by name with wired-up exception provider. '''
    # TODO: Validate presence of name in dictionary.
    return __.partial_function(
        _our_exception_factories[ f"create_{name}_exception" ],
        our_exception_provider )


# TODO: Take an invocation argument.
def validate_exception_controller( controller ):
    ''' Validates alleged exception controller by attributes. '''
    from ._base import exception_controller
    from .validators import validate_attribute_invocability
    for aname in ( 'apprehend_fugitive', 'provide_factory', ):
        validate_attribute_invocability(
            exception_controller, aname, controller )
    return controller


our_exception_controller = ExceptionController(
    factory_provider = our_exception_factory_provider,
    fugitive_apprehender = our_fugitive_apprehender )
