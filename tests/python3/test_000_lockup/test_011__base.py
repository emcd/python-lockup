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
        provide_exception_controller,
    )
    from lockup._exceptionality import (
        exception_controller,
        excoriate_exception_controller,
        validate_exception_controller,
    )
    from lockup.exceptionality import ExceptionController


# TODO: Validate 'package_name' and 'provide_exception_controller'.


def test_101_excoriate_exception_controller( ):
    ''' Exception controller is unwrapped. '''
    assert __.exception_controller is  __.excoriate_exception_controller(
        __.provide_exception_controller )


def test_102_excoriate_exception_controller_from_angry_wrapper( ):
    ''' Wrapper execution exception is handled. '''
    def unwrap( ): return 1 / 0
    with raises( __.exceptions.IncorrectData ):
        __.excoriate_exception_controller( unwrap )


def test_111_validate_exception_controller( ):
    ''' Exception controller is valid. '''
    assert __.exception_controller is __.validate_exception_controller(
        __.exception_controller )


def test_113_validate_noninvocable_attribute_exception_controller( ):
    ''' Exception controller has non-invocable attribute. '''
    with raises( __.exceptions.InvalidOperation ):
        __.validate_exception_controller( __.ExceptionController(
            factory_provider = 42,
            fugitive_apprehender = 43,
        ) )
