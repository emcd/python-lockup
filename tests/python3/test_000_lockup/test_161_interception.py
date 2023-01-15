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
    from lockup.exceptionality import (
        our_exception_factory_provider,
    )
    from lockup.interception import (
        create_interception_decorator,
        intercept_fugitive_exception_apprehender,
        our_fugitive_exception_apprehender,
        our_interceptor,
    )


def test_011_intercept_apprehender( ):
    ''' Ensures validation and decoration of apprehender. '''
    apprehender = __.intercept_fugitive_exception_apprehender(
        __.our_fugitive_exception_apprehender,
        test_011_intercept_apprehender )
    assert callable( apprehender )
    exc = __.exceptions.Omniexception( 'test' )
    assert ( exc, None ) == apprehender( exc, test_011_intercept_apprehender )


def test_016_error_invalid_argument_vector_for_apprehender( ):
    ''' Expect error on invalid argument vector for apprehender. '''
    apprehender = __.intercept_fugitive_exception_apprehender(
        __.our_fugitive_exception_apprehender,
        test_016_error_invalid_argument_vector_for_apprehender )
    with raises( __.exceptions.InvalidOperation ): apprehender( )


def _faulty_apprehender( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. Not really. '''
    raise RuntimeError( 'lol' )

def test_017_error_faulty_apprehender( ):
    ''' Expect error on faulty apprehender. '''
    apprehender = __.intercept_fugitive_exception_apprehender(
        _faulty_apprehender, test_017_error_faulty_apprehender )
    with raises( __.exceptions.InvalidState ):
        apprehender(
            __.exceptions.Omniexception, test_017_error_faulty_apprehender )


def test_021_create_interception_decorator( ):
    ''' Interception decorator receives invocable and returns invocable. '''
    decorator = __.create_interception_decorator(
        __.our_exception_factory_provider,
        apprehender = __.our_fugitive_exception_apprehender )
    assert callable( decorator )


@mark.parametrize( 'provider', ( 123, 'ph00b4r' * 5, ) )
def test_026_interceptor_creation_with_invalid_provider( provider ):
    ''' Interception decorator creation fails on invalid provider. '''
    with raises( __.exceptions.IncorrectData ):
        __.create_interception_decorator(
            provider, apprehender = __.our_fugitive_exception_apprehender )


@mark.parametrize( 'apprehender', ( 123, 'ph00b4r' * 5, ) )
def test_027_interceptor_creation_with_invalid_apprehender( apprehender ):
    ''' Interception decorator creation fails on invalid apprehender. '''
    with raises( __.exceptions.IncorrectData ):
        __.create_interception_decorator(
            __.our_exception_factory_provider, apprehender = apprehender )


@mark.parametrize(
    'value', ( None, 42, 'test', Exception, Exception( ), ( ), [ 42 ], )
)
def test_031_intercept_normal_return( value ):
    ''' Returns across API boundary without alteration. '''
    @__.our_interceptor
    def return_per_normal( value ): return value
    assert value == return_per_normal( value )


def test_032_translate_fugitive_with_interceptor( ):
    ''' Interception decorator intercepts and translates fugitives. '''
    @__.our_interceptor
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.InvalidState ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.InvalidState as exc:
        assert isinstance( exc.__cause__, ZeroDivisionError )


@mark.parametrize(
    'exception_class', (
        __.exceptions.InvalidOperation,
        __.exceptions.InvalidState,
    )
)
def test_033_relay_permissible_with_interceptor( exception_class ):
    ''' Interception decorator relays permissible exceptions. '''
    @__.our_interceptor
    def raise_permissible_exception( ): raise exception_class
    with raises( exception_class ): raise_permissible_exception( )


def test_034_intercept_invalid_invocation( ):
    ''' Special report on invalid invocation arguments. '''
    # nosemgrep: python.lang.best-practice.pass-body-fn
    @__.our_interceptor
    def a_function( ): pass
    with raises( __.exceptions.IncorrectData ):
        a_function( 123 ) # pylint: disable=too-many-function-args


def _return_fugitive( exception, invocation ): # pylint: disable=unused-argument
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, __.exceptions.Omniexception ):
        return exception, None
    return None, None

def test_035_intercept_and_return_fugitive( ):
    ''' Interception decorator returns apprehended fugitives. '''
    @__.create_interception_decorator(
        __.our_exception_factory_provider,
        apprehender = _return_fugitive )
    def release_fugitive( ): return 1 / 0
    assert isinstance( release_fugitive( ), ZeroDivisionError )


def _propagate_replacement( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, __.exceptions.Omniexception ):
        return exception, None
    return (
        None,
        __.our_exception_factory_provider( 'fugitive_apprehension' )(
            exception, invocation ) )

def test_036_intercept_and_propagate_replacement( ):
    ''' Interception decorator propagates replacements for fugitives. '''
    @__.create_interception_decorator(
        __.our_exception_factory_provider,
        apprehender = _propagate_replacement )
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.InvalidState ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.InvalidState as exc:
        assert None is exc.__cause__


def _propagate_invalid_origin( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, __.exceptions.Omniexception ):
        return exception, None
    return invocation, None

def test_037_intercept_and_check_invalid_origin( ):
    ''' Inteception decorator checks invalid custodian for fugitives. '''
    @__.create_interception_decorator(
        __.our_exception_factory_provider,
        apprehender = _propagate_invalid_origin )
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.InvalidState ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.InvalidState as exc:
        assert 'return validation' == exc.exception_labels[ 'failure class' ]


def _propagate_invalid_custodian( exception, invocation ):
    ''' Apprehends fugitive exceptions at API boundary. '''
    if isinstance( exception, __.exceptions.Omniexception ):
        return exception, None
    return None, invocation

def test_038_intercept_and_check_invalid_custodian( ):
    ''' Inteception decorator checks invalid custodian for fugitives. '''
    @__.create_interception_decorator(
        __.our_exception_factory_provider,
        apprehender = _propagate_invalid_custodian )
    def release_fugitive( ): return 1 / 0
    with raises( __.exceptions.InvalidState ): release_fugitive( )
    try: release_fugitive( )
    except __.exceptions.InvalidState as exc:
        assert 'return validation' == exc.exception_labels[ 'failure class' ]
