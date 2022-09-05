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


from pytest import mark

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup._base import intercept
    from lockup.exceptions import (
        AbsentImplementation,
        IncorrectData,
        create_argument_validation_exception,
        create_implementation_absence_exception,
    )


from .invocables import InvocableObject as _InvocableObject
_invocable_object = _InvocableObject( )
_invocables = (
    lambda: None, __.intercept, _InvocableObject,
    _invocable_object, _invocable_object.a_method,
)


@mark.parametrize( 'argument', _invocables )
def test_011_argument_validation_exception( argument ):
    ''' Validation exception is created from argument. '''
    def tester( argument ): return argument
    assert isinstance(
        __.create_argument_validation_exception(
            'argument', tester, type( argument ) ), __.IncorrectData )


def test_012_argument_validation_exception_with_label( ):
    ''' Validation exception with special label is created from argument. '''
    label = 'special integer'
    def tester( argument ): return argument
    result = __.create_argument_validation_exception(
        'argument', tester, label )
    assert isinstance( result, __.IncorrectData )
    assert label in str( result )


@mark.parametrize(
    'trial_function',
    ( sorted, lambda iterable: iterable, lambda *iterable: len( iterable ),
      lambda iterable = 1: iterable, lambda **iterable: len( iterable ) ) )
def test_013_argument_validation_exceptions( trial_function ):
    ''' Validation exception with different categories of arguments. '''
    assert isinstance(
        __.create_argument_validation_exception(
            'iterable', trial_function, object ), __.IncorrectData )


@mark.parametrize( 'argument', _invocables )
def test_021_implementation_absence_exception( argument ):
    ''' Validation exception is created from argument. '''
    assert isinstance(
        __.create_implementation_absence_exception( argument, 'something' ),
        __.AbsentImplementation )
