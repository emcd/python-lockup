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


''' Ensure correctness of internal base. '''


from pytest import raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exceptions
    from lockup._base import (
        LatentExceptionController,
        exception_controller,
        package_name,
    )
    from lockup.exceptionality import (
        ExceptionController,
        validate_exception_controller,
    )


def test_001_validate_package_name( ):
    ''' Package name is correct. '''
    assert 'lockup' == __.package_name


def test_016_validate_excc_setattr_protection( ):
    ''' Exception controller attributes are immutable. '''
    excc = __.LatentExceptionController( )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        excc.apprehend_fugitive = lambda exc, inv: ( None, exc )


def test_017_validate_excc_delattr_protection( ):
    ''' Exception controller attributes are indelible. '''
    excc = __.LatentExceptionController( )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        del excc.provide_factory


def test_101_validate_exception_controller( ):
    ''' Exception controller is valid. '''
    assert __.exception_controller is __.validate_exception_controller(
        __.exception_controller )


# TODO: Move to exceptionality test module.
def test_103_validate_noninvocable_attribute_exception_controller( ):
    ''' Exception controller has non-invocable attribute. '''
    with raises( __.exceptions.InvalidOperation ):
        __.validate_exception_controller( __.ExceptionController(
            factory_provider = 42,
            fugitive_apprehender = 43,
        ) )
