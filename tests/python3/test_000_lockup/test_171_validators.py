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


''' Ensure correctness of validators. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup.exception_factories import (
        our_exception_factory_provider,
    )
    from lockup.exceptions import (
        InaccessibleAttribute,
        IncorrectData,
        InvalidOperation,
    )
    from lockup.interception import our_interceptor
    from lockup.validators import (
        validate_argument_invocability,
        validate_attribute_existence,
        validate_attribute_invocability,
    )


from .invocables import InvocableObject as _InvocableObject
_invocable_object = _InvocableObject( )
_invocables = (
    lambda: None, __.our_interceptor, _InvocableObject,
    _invocable_object, _invocable_object.a_method,
)


@mark.parametrize( 'argument', _invocables )
def test_011_validate_invocable_argument( argument ):
    ''' Invocables are returned without alteration. '''
    def tester( argument ): return argument
    assert argument == __.validate_argument_invocability(
        __.our_exception_factory_provider, argument, 'argument', tester )


@mark.parametrize( 'argument', ( 123, 'ph00b4r' * 5, ) )
def test_012_validate_noninvocable_argument( argument ):
    ''' Noninvocable objects causes exceptions. '''
    def tester( argument ): return argument
    with raises( __.IncorrectData ):
        __.validate_argument_invocability(
            __.our_exception_factory_provider, argument, 'argument', tester )


def test_021_validate_attribute_existence( ):
    ''' Names of valid attributes are returned without alteration. '''
    assert 'a_method' == __.validate_attribute_existence(
        __.our_exception_factory_provider, 'a_method', _invocable_object )


def test_022_validate_attribute_nonexistence( ):
    ''' Nonexistent attributes cause exceptions. '''
    aname = 'ph00b4r' * 5
    with raises( __.InaccessibleAttribute ):
        __.validate_attribute_existence(
            __.our_exception_factory_provider, aname, _invocable_object )


def test_031_validate_invocable_attribute( ):
    ''' Names of invocable attributes are returned without alteration. '''
    assert 'a_method' == __.validate_attribute_invocability(
        __.our_exception_factory_provider, 'a_method', _invocable_object )


def test_032_validate_attribute_noninvocability( ):
    ''' Noninvocable attributes cause exceptions. '''
    aname = '__dict__'
    with raises( __.InvalidOperation ):
        __.validate_attribute_invocability(
            __.our_exception_factory_provider, aname, _invocable_object )
