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


''' Validation functions. '''


# Module Initialization Dependencies: (none)
# Module Execution Dependencies:
#   validators -> nomenclature -> validators
# pylint: disable=cyclic-import


def validate_argument_class(
    exception_controller, argument, classes, name, invocation
):
    ''' Validates argument as an instance of one or more classes. '''
    if isinstance( argument, classes ): return argument
    from .nomenclature import calculate_class_label
    expectation = calculate_class_label( classes )
    raise _excoriate_and_validate_excc( exception_controller ).provide_factory(
        'argument_validation' )( name, invocation, expectation )


def validate_argument_invocability(
    exception_controller, argument, name, invocation
):
    ''' Validates argument as an invocable object, such as a function. '''
    if callable( argument ): return argument
    raise _excoriate_and_validate_excc( exception_controller ).provide_factory(
        'argument_validation' )( name, invocation, 'invocable' )


def validate_attribute_name( exception_controller, name ):
    ''' Validates attribute name as Python identifier. '''
    from .nomenclature import is_python_identifier
    if is_python_identifier( name ): return name
    raise _excoriate_and_validate_excc( exception_controller ).provide_factory(
        'attribute_name_illegality' )( name )


def validate_attribute_existence( exception_controller, name, object_ ):
    ''' Validates attribute existence on object. '''
    if hasattr( object_, name ): return name
    raise _excoriate_and_validate_excc( exception_controller ).provide_factory(
        'attribute_nonexistence' )( name, object_ )


def validate_attribute_invocability( exception_controller, name, object_ ):
    ''' Validates attribute invocability on object.

        Implies attribute existence validation. '''
    validate_attribute_existence( exception_controller, name, object_ )
    if callable( getattr( object_, name ) ): return name
    raise _excoriate_and_validate_excc( exception_controller ).provide_factory(
        'attribute_noninvocability' )( name, object_ )


def _excoriate_and_validate_excc( controller ):
    ''' Validates exception controller, first unwrapping if it is callable. '''
    from ._exceptionality import (
        excoriate_exception_controller,
        validate_exception_controller,
    )
    return validate_exception_controller( excoriate_exception_controller(
        controller ) )
