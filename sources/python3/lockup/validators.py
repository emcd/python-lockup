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


def validate_argument_invocability( argument, name, invocation ):
    ''' Validates argument as an invocable object, such as a function. '''
    if callable( argument ): return argument
    from .exceptions import create_argument_validation_exception
    raise create_argument_validation_exception( name, invocation, 'invocable' )


def validate_attribute_name( name, context ):
    ''' Validates attribute name as Python identifier. '''
    from .nomenclature import is_python_identifier
    if is_python_identifier( name ): return name
    from .nomenclature import calculate_label
    label = calculate_label( context, f"attribute '{name}'" )
    from .exceptions import InaccessibleAttribute
    raise InaccessibleAttribute( f"Illegal name for {label}." )


def validate_attribute_existence( name, context ):
    ''' Validates attribute existence on context object. '''
    if hasattr( context, name ): return name
    from .exceptions import create_attribute_nonexistence_exception
    raise create_attribute_nonexistence_exception( name, context )
