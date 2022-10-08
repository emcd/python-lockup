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


''' Ensure correctness of class factories. '''


from pytest import raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exceptions
    from lockup.factories import (
        Class,
        NamespaceClass,
        create_namespace,
    )


def test_011_produce_class( ):
    ''' Normal production of class. '''
    class Object( metaclass = __.Class ): ''' Test class. '''
    assert isinstance( Object, __.Class )


def test_111_produce_namespace( ):
    ''' Normal production of namespace. '''
    class Namespace( metaclass = __.NamespaceClass ):
        ''' Test namespace. '''
        answer = 42
    assert isinstance( Namespace, __.NamespaceClass )


def test_116_fail_to_produce_instantiable_namespace( ):
    ''' No production of namespace with possible instantiation. '''
    with raises( __.exceptions.InvalidOperation ):
        class Namespace( metaclass = __.NamespaceClass ): # pylint: disable=unused-variable
            ''' Test namespace. '''
            def __new__( class_, *pos_arguments, **nom_arguments ):
                return super( class_, __.NamespaceClass ).__new__(
                    *pos_arguments, **nom_arguments )


def test_151_create_namespace( ):
    ''' Produce namespace via factory. '''
    namespace = __.create_namespace( answer = 42 )
    assert isinstance( namespace, __.NamespaceClass )
