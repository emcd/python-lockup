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


''' Ensure correctness of exception controller. '''


from pytest import raises


from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exception_factories, exceptions
    from lockup.exceptionality import (
        ExceptionController,
        our_exception_factory_provider,
        our_exception_provider,
        our_fugitive_apprehender,
        validate_exception_controller,
    )


def test_011_provide_exception_class( ):
    ''' Can provide existent exception class. '''
    assert (
        __.exceptions.Exception0
        is __.our_exception_provider( 'Exception0' ) )


def test_012_error_on_provide_nonexistent_exception_class( ):
    ''' Error on attempt to provide nonexistent exception class. '''
    with raises( __.exceptions.IncorrectData ):
        __.our_exception_provider( 123 )


def test_021_provide_exception_factory( ):
    ''' Can provide existent exception factory. '''
    assert (
        __.exception_factories.create_entry_absence_exception
        is __.our_exception_factory_provider( 'entry_absence' ).func )


def test_022_error_on_provide_nonexistent_exception_factory( ):
    ''' Error on attempt to provide nonexistent exception factory. '''
    with raises( __.exceptions.IncorrectData ):
        __.our_exception_factory_provider( 123 )


def test_111_validate_noninvocable_attribute_exception_controller( ):
    ''' Exception controller has illegal non-invocable attribute. '''
    with raises( __.exceptions.InvalidOperation ):
        __.validate_exception_controller( __.ExceptionController(
            factory_provider = 42,
            fugitive_apprehender = 43,
        ) )


def test_116_validate_excc_setattr_protection( ):
    ''' Exception controller attributes are immutable. '''
    excc = __.ExceptionController(
        factory_provider = __.our_exception_factory_provider,
        fugitive_apprehender = __.our_fugitive_apprehender,
    )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        excc.apprehend_fugitive = lambda exc, inv: ( None, exc )


def test_117_validate_excc_delattr_protection( ):
    ''' Exception controller attributes are indelible. '''
    excc = __.ExceptionController(
        factory_provider = __.our_exception_factory_provider,
        fugitive_apprehender = __.our_fugitive_apprehender,
    )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        del excc.provide_factory
