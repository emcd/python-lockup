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


''' Ensure correctness of interceptor factories and their produce. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from functools import partial as partial_function
    from types import MappingProxyType as DictionaryProxy

    from lockup import exception_factories, exceptions
    from lockup._base import intercept
    from lockup.exceptionality import (
        ExceptionController,
        our_exception_controller,
    )
    from lockup.interception import create_interception_decorator
    from lockup.visibility import is_public_name


# Cannot wildcard import 'exceptions' module into a namespace,
# so we use immutable dictionary instead.
_exceptions = __.DictionaryProxy( {
    aname: getattr( __.exceptions, aname ) for aname in dir( __.exceptions )
    if __.is_public_name( aname )
} )


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
    return __.partial_function(
        _exception_factories[ f"create_{name}_exception" ],
        _provide_exception )


def _return_fugitive( exception, invocation ): # pylint: disable=unused-argument
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, tuple( _exceptions.values( ) ) ):
        return 'propagate-at-liberty', None
    return 'return', None

_return_fugitive_ec = __.ExceptionController(
    factory_provider = _provide_exception_factory,
    fugitive_apprehender = _return_fugitive )


def _propagate_replacement( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, tuple( _exceptions.values( ) ) ):
        return 'propagate-at-liberty', None
    return (
        'silence-and-except',
        _provide_exception_factory( 'fugitive_apprehension' )(
            exception, invocation ) )

_propagate_replacement_ec = __.ExceptionController(
    factory_provider = _provide_exception_factory,
    fugitive_apprehender = _propagate_replacement )


def _return_replacement( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, tuple( _exceptions.values( ) ) ):
        return 'propagate-at-liberty', None
    return (
        'return-replacement',
        _provide_exception_factory( 'fugitive_apprehension' )(
            exception, invocation ) )

_return_replacement_ec = __.ExceptionController(
    factory_provider = _provide_exception_factory,
    fugitive_apprehender = _return_replacement )


def test_011_create_interception_decorator( ):
    ''' Interception decorator receives invocable and returns invocable. '''
    decorator = __.create_interception_decorator( __.our_exception_controller )
    assert callable( decorator )


# TODO: Check for wrapped exception controller.


@mark.parametrize( 'controller', ( 123, 'ph00b4r' * 5, ) )
def test_012_interceptor_creation_with_invalid_exception_controller(
    controller
):
    ''' Interception decorator fails on invalid invocable. '''
    with raises( __.exceptions.InaccessibleAttribute ):
        __.create_interception_decorator( controller )


# TODO: Check that exception controller is tested
#       for its attributes and that they are invocable.


@mark.parametrize(
    'value', ( None, 42, 'test', Exception, Exception( ), ( ), [ 42 ], )
)
def test_016_intercept_normal_return( value ):
    ''' Returns across API boundary without alteration. '''
    @__.intercept
    def return_per_normal( value ): return value
    assert value == return_per_normal( value )


def test_017_translate_fugitive_with_interceptor( ):
    ''' Interception decorator intercepts and translates fugitives. '''
    @__.intercept
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.FugitiveException ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.FugitiveException as exc:
        assert isinstance( exc.__cause__, ZeroDivisionError )


@mark.parametrize(
    'exception_class', (
        __.exceptions.InvalidOperation,
        __.exceptions.InvalidState,
    )
)
def test_018_relay_permissible_with_interceptor( exception_class ):
    ''' Interception decorator relays permissible exceptions. '''
    @__.intercept
    def raise_permissible_exception( ): raise exception_class
    with raises( exception_class ): raise_permissible_exception( )


def test_019_intercept_invalid_invocation( ):
    ''' Special report on invalid invocation arguments. '''
    @__.intercept
    def a_function( ): pass
    with raises( __.exceptions.IncorrectData ):
        a_function( 123 ) # pylint: disable=too-many-function-args


def test_021_intercept_and_return_fugitive( ):
    ''' Interception decorator returns apprehended fugitives. '''
    @__.create_interception_decorator( _return_fugitive_ec )
    def release_fugitive( ): return 1 / 0
    assert isinstance( release_fugitive( ), ZeroDivisionError )


def test_022_intercept_and_propagate_replacement( ):
    ''' Interception decorator propagates replacements for fugitives. '''
    @__.create_interception_decorator( _propagate_replacement_ec )
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.FugitiveException ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.FugitiveException as exc:
        assert None is exc.__cause__


def test_023_intercept_and_return_replacement( ):
    ''' Interception decorator returns replacements for fugitives. '''
    @__.create_interception_decorator( _return_replacement_ec )
    def release_fugitive( ): return 1 / 0
    assert isinstance( release_fugitive( ), __.exceptions.FugitiveException )
