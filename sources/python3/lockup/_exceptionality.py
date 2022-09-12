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


''' Internal facilities for exception production and control. '''


# Initialization Dependencies:
#   _exceptionality -> class_factories
#   _exceptionality -> exception_factories
#   _exceptionality -> exceptions
# Latent Dependencies: (no cycles)


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from functools import partial as partial_function
    from types import MappingProxyType as DictionaryProxy

    from . import exception_factories, exceptions
    from .exceptionality import ExceptionController
    from .visibility import is_public_name


# Cannot wildcard import 'exceptions' module into a namespace,
# so we use immutable dictionary instead.
_exceptions = __.DictionaryProxy( {
    aname: getattr( __.exceptions, aname ) for aname in dir( __.exceptions )
    if __.is_public_name( aname )
} )


def _apprehend_fugitive( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, tuple( _exceptions.values( ) ) ):
        return 'propagate-at-liberty', None
    return (
        'propagate-in-custody',
        _provide_exception_factory( 'fugitive_apprehension' )(
            exception, invocation ) )


def _provide_exception( name ):
    ''' Returns exception by name. '''
    return _exceptions[ name ]


# Cannot wildcard import 'exception_factories' module into a namespace,
# so we use immutable dictionary instead.
_exception_factories = __.DictionaryProxy( {
    aname: getattr( __.exception_factories, aname )
    for aname in dir( __.exception_factories )
    if __.is_public_name( aname )
} )


def _provide_exception_factory( name ):
    ''' Returns exception factory by name with wired-up exception provider. '''
    # TODO: Validate presence of name in dictionary.
    return __.partial_function(
        _exception_factories[ f"create_{name}_exception" ],
        _provide_exception )


exception_controller = __.ExceptionController(
    factory_provider = _provide_exception_factory,
    fugitive_apprehender = _apprehend_fugitive )


def excoriate_exception_controller( controller ):
    ''' Excoriates exception controller via invocation, if necessary. '''
    if not callable( controller ): return controller
    try: return controller( )
    except BaseException as exc: # pylint: disable=broad-except
        raise exception_controller.provide_factory(
            'nonexcoriable_exception_controller' )( controller ) from exc


def validate_exception_controller( controller ):
    ''' Validates exception controller. '''
    for aname in ( 'apprehend_fugitive', 'provide_factory', ):
        if not hasattr( controller, aname ):
            raise exception_controller.provide_factory(
                'attribute_nonexistence' )( aname, controller )
        if not callable( getattr( controller, aname ) ):
            raise exception_controller.provide_factory(
                'attribute_noninvocability' )( aname, controller )
    return controller
