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


''' Ensure correctness of reflection functionality. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from sys import implementation as python_implementation
    python_name = python_implementation.name

    from lockup import exceptions
    from lockup.reflection import reassign_class_factory


@mark.skipif(
    __.python_name not in (
        'cpython', 'pyston',
    ),
    reason = f"Not yet supported on Python implementation: {__.python_name}"
)
def test_011_reassign_class_factory( ):
    ''' Class factory class can be made into a factory of itself. '''
    class TrivialFactory( type ): ''' Trivial class factory class. '''
    assert issubclass( TrivialFactory, type )
    factory = __.reassign_class_factory(
        TrivialFactory, TrivialFactory, assert_implementation = False )
    assert issubclass( TrivialFactory, TrivialFactory )
    assert factory is TrivialFactory


@mark.skipif(
    __.python_name in (
        'cpython', 'pyston',
    ),
    reason = f"Unreachable branch on Python implementation: {__.python_name}"
)
def test_012_no_implementation_of_reassign_class_factory( ):
    ''' Class factory class cannot be made into a factory of itself. '''
    class TrivialFactory( type ): ''' Trivial class factory class. '''
    assert issubclass( TrivialFactory, type )
    with raises( __.exceptions.AbsentImplementation ):
        __.reassign_class_factory( TrivialFactory, TrivialFactory )
    assert issubclass( TrivialFactory, type )


@mark.parametrize( 'class_', ( 123, 'ph00b4r' * 5, ) )
def test_016_reflect_invalid_class( class_ ):
    ''' Only classes can receive assignment. '''
    class TrivialFactory( type ): ''' Trivial class factory class. '''
    with raises( __.exceptions.IncorrectData ):
        __.reassign_class_factory( class_, TrivialFactory )


@mark.parametrize( 'factory', ( 123, 'ph00b4r' * 5, ) )
def test_017_reflect_invalid_class_factory( factory ):
    ''' Only class factory classes can be assigned. '''
    class Object: ''' Trivial class. '''
    with raises( __.exceptions.IncorrectData ):
        __.reassign_class_factory( Object, factory )
