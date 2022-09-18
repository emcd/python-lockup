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


''' Ensure correctness of exception factories and their produce. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup._base import intercept
    from lockup._exceptionality import exception_controller
    from lockup.exceptions import (
        AbsentImplementation,
        IncorrectData,
    )
    from lockup.exception_factories import (
        ExtraData,
        create_argument_validation_exception,
        create_implementation_absence_exception,
    )


from .invocables import InvocableObject as _InvocableObject
_invocable_object = _InvocableObject( )
_invocables = (
    lambda: None, __.intercept, _InvocableObject,
    _invocable_object, _invocable_object.a_method,
)


def test_011_argument_validation_exception( ):
    ''' Validation exception is created from argument. '''
    expectation = 'special integer'
    def tester( argument ): return argument
    extra_data = __.ExtraData(
        nominative_arguments = dict( exception_labels = { } ) )
    result = __.exception_controller.provide_factory( 'argument_validation' )(
        'argument', tester, expectation, extra_data = extra_data )
    assert isinstance( result, __.IncorrectData )
    assert expectation in str( result )


@mark.parametrize( 'provider', ( 123, 'ph00b4r' * 5 ) )
def test_012_argument_validation_exception_invalid_provider( provider ):
    ''' Cannot create validation exception because of invalid provider. '''
    def tester( argument ): return argument
    with raises( __.IncorrectData ):
        __.create_argument_validation_exception(
            provider, 'argument', tester, 'whatever' )


@mark.parametrize( 'invocation', ( 123, 'ph00b4r' * 5 ) )
def test_013_argument_validation_exception_invalid_invocation( invocation ):
    ''' Cannot create validation exception because of invalid invocation. '''
    with raises( __.IncorrectData ):
        __.exception_controller.provide_factory( 'argument_validation' )(
            'argument', invocation, 'whatever' )


@mark.parametrize( 'expectation', ( 123, lambda: None ) )
def test_014_argument_validation_exception_invalid_expectation( expectation ):
    ''' Cannot create validation exception because of invalid expectation. '''
    def tester( argument ): return argument
    with raises( __.IncorrectData ):
        __.exception_controller.provide_factory( 'argument_validation' )(
            'argument', tester, expectation )


@mark.parametrize(
    'trial_function',
    ( sorted, lambda iterable: iterable, lambda *iterable: len( iterable ),
      lambda iterable = 1: iterable, lambda **iterable: len( iterable ) ) )
def test_016_argument_validation_exceptions( trial_function ):
    ''' Validation exception with different categories of arguments. '''
    assert isinstance(
        __.exception_controller.provide_factory( 'argument_validation' )(
            'iterable', trial_function, 'function' ), __.IncorrectData )


def test_021_invocation_validation_exception( ):
    ''' Validation exception is created from arguments. '''
    def tester( argument ): return argument
    assert isinstance(
        __.exception_controller.provide_factory( 'invocation_validation' )(
            tester, 'mismatched arguments' ), __.IncorrectData )


@mark.parametrize( 'argument', _invocables )
def test_031_implementation_absence_exception( argument ):
    ''' Validation exception is created from argument. '''
    assert isinstance(
        __.exception_controller.provide_factory( 'implementation_absence' )(
            argument, 'something' ),
        __.AbsentImplementation )
