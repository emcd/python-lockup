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

    from lockup import exceptions
    from lockup._base import intercept
    from lockup.interception import (
        create_interception_decorator,
    )


def _provide_exception( name ):
    ''' Simple exception provider. '''
    return getattr( __.exceptions, name )


def test_011_create_interception_decorator( ):
    ''' Interception decorator receives invocable and returns invocable. '''
    decorator = __.create_interception_decorator(
        exception_provider = _provide_exception )
    assert callable( decorator )


@mark.parametrize( 'provider', ( 123, 'ph00b4r' * 5, ) )
def test_012_interceptor_creation_with_invalid_exception_provider( provider ):
    ''' Only class factory classes can be reflected. '''
    with raises( __.exceptions.IncorrectData ):
        __.create_interception_decorator( exception_provider = provider )


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
