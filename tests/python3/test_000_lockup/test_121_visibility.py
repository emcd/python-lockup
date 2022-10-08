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


''' Ensure correctness of visibility functions. '''


from pytest import mark

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup.factories import Class
    from lockup.visibility import (
        is_operational_name,
        is_public_or_operational_name,
        select_public_attributes,
    )


def test_011_is_operational_name( ):
    ''' Verify valid operational Python identifier. '''
    assert __.is_operational_name( '__dict__' )


@mark.parametrize(
    'name', ( 'public', '_non_public', '__', '__nope', 'if', '123', )
)
def test_016_is_not_operational_name( name ):
    ''' Verify invalid operational Python identifier. '''
    assert not __.is_operational_name( name )


@mark.parametrize( 'name', ( 'public', '__dict__', ) )
def test_021_is_public_or_operational_name( name ):
    ''' Verify valid public or operational Python identifier. '''
    assert __.is_public_or_operational_name( name )


@mark.parametrize(
    'name', ( '_non_public', '__', '__nope', 'if', '123', 123, None, )
)
def test_026_is_not_public_or_operational_name( name ):
    ''' Verify invalid public or operational Python identifier. '''
    assert not __.is_public_or_operational_name( name )


class _A: red = 1
class _B( metaclass = _NamespaceClass ): blue = 2
class _C: __slots__ = ( 'blue', 'red', )


@mark.parametrize(
    'class_, object_, includes, excludes, expectation',
    ( ( type, _A, ( ), ( ), [ 'mro', 'red' ] ),
      ( _A, _A( ), ( ), ( ), [ 'red' ] ),
      ( __.Class, _NamespaceClass, ( ), ( ), [ 'mro' ] ),
      ( _NamespaceClass, _B, ( ), ( ), [ 'blue' ] ),
      ( _C, _C( ), ( ), ( ), [ 'blue', 'red' ] ),
      ( _C, _C( ), ( '__str__', ), ( 'red', ), [ '__str__', 'blue' ] ) ) )
def test_051_select_public_attributes(
    class_, object_, includes, excludes, expectation
):
    ''' Verify selection of public attributes for given class and object. '''
    assert (
           expectation
        == sorted( __.select_public_attributes(
            class_, object_, includes = includes, excludes = excludes ) ) )
