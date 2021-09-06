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


''' Ensure correctness of package API. '''


from pytest import mark, raises

from lockup import NamespaceFactory


class __( metaclass = NamespaceFactory ):

    from lockup import exceptions
    from lockup import (
        reclassify_module,
        Module,
        NamespaceFactory,
        PrimalClassFactory,
    )


def test_211_produce_namespace( ):
    ''' Normal production of namespace. '''

    class Namespace( metaclass = __.NamespaceFactory ):
        ''' Test namespace. '''

        answer = 42

    assert isinstance( Namespace, __.NamespaceFactory )


def test_212_fail_to_produce_instantiable_namespace( ):
    ''' No production of namespace with possible instantiation. '''

    with raises( __.exceptions.InvalidOperation ):

        class Namespace( metaclass = __.NamespaceFactory ):
            ''' Test namespace. '''

            def __new__( class_, *pos_arguments, **nom_arguments ):
                return super( class_, __.NamespaceFactory ).__new__(
                    *pos_arguments, **nom_arguments )

        del Namespace


def test_301_reclassify_module_object( ):
    ''' Module instance can be reclassified. '''
    import types
    __.reclassify_module( types )
    assert isinstance( types, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        types.ModuleType = types.FunctionType


def test_302_reclassify_module_by_name( ):
    ''' Module can be reclassified by import name. '''
    import pprint
    __.reclassify_module( 'pprint' )
    assert isinstance( pprint, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        pprint.pprint = print


def test_303_reclassify_module_idempotence( ):
    ''' Module reclassification is idempotent. '''
    assert isinstance( __.exceptions, __.Module )
    __.reclassify_module( __.exceptions )
    assert isinstance( __.exceptions, __.Module )


@mark.parametrize( 'module', ( 123, 'ph00b4r' * 5, ) )
def test_304_reclassify_invalid_module( module ):
    ''' Only modules may be reclassified. '''
    with raises( __.exceptions.IncorrectData ):
        __.reclassify_module( module )
