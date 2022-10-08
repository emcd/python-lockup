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


''' Ensure correctness of module class and reclassifier function. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exceptions
    from lockup.module import (
        Module,
        reclassify_module,
    )


def test_111_reclassify_module_object( ):
    ''' Module instance can be reclassified. '''
    # NOTE: Must NOT reclassify any module that we use in our package during
    #       testing. This causes nasty dependency cycles / infinite recursion
    #       during exception generation, likely due to Pytest's modification of
    #       the import mechanism. Choose ones which are "obscure" relative to
    #       the purpose of our package.
    import bisect
    __.reclassify_module( bisect )
    assert isinstance( bisect, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        bisect.bisect_left = bisect.bisect_right


def test_112_reclassify_module_by_name( ):
    ''' Module can be reclassified by import name. '''
    # NOTE: Must NOT reclassify any module that we use in our package during
    #       testing. This causes nasty dependency cycles / infinite recursion
    #       during exception generation, likely due to Pytest's modification of
    #       the import mechanism. Choose ones which are "obscure" relative to
    #       the purpose of our package.
    import numbers
    __.reclassify_module( 'numbers' )
    assert isinstance( numbers, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        numbers.Complex = numbers.Real


def test_113_reclassify_module_idempotence( ):
    ''' Module reclassification is idempotent. '''
    assert isinstance( __.exceptions, __.Module )
    __.reclassify_module( __.exceptions )
    assert isinstance( __.exceptions, __.Module )


@mark.parametrize( 'module', ( 123, 'ph00b4r' * 5, ) )
def test_116_reclassify_invalid_module( module ):
    ''' Only modules may be reclassified. '''
    with raises( __.exceptions.IncorrectData ):
        __.reclassify_module( module )
