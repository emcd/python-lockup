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


# TODO: Move tests to correct modules.


from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exception_factories, exceptions
    from lockup.exception_factories import (
        our_exception_class_provider,
        our_exception_factory_provider,
    )


def test_011_provide_exception_class( ):
    ''' Can provide existent exception class. '''
    assert (
        __.exceptions.Exception0
        is __.our_exception_class_provider( 'Exception0' ) )


def test_012_error_on_provide_nonexistent_exception_class( ):
    ''' Error on attempt to provide nonexistent exception class. '''
    with raises( __.exceptions.InvalidOperation ):
        __.our_exception_class_provider( 123 )


def test_021_provide_exception_factory( ):
    ''' Can provide existent exception factory. '''
    assert (
        __.exception_factories.create_argument_validation_exception
        is __.our_exception_factory_provider( 'argument_validation' ).func )


def test_022_error_on_provide_nonexistent_exception_factory( ):
    ''' Error on attempt to provide nonexistent exception factory. '''
    with raises( __.exceptions.InvalidOperation ):
        __.our_exception_factory_provider( 123 )
