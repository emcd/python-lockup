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


# Latent Dependencies:
#   validators -> exceptionality -> validators
#   validators -> nomenclature -> validators
# pylint: disable=cyclic-import


def validate_argument_class(
    exception_factory_provider, argument, classes, name, invocation
):
    ''' Validates argument as an instance of one or more classes. '''
    if isinstance( argument, classes ): return argument
    from .nomenclature import calculate_class_label
    expectation = calculate_class_label( classes )
    raise _intercept_exception_factory_provider(
        exception_factory_provider, validate_argument_class )(
            'argument_validation' )( name, invocation, expectation )


def validate_argument_invocability(
    exception_factory_provider, argument, name, invocation
):
    ''' Validates argument as an invocable object, such as a function. '''
    if callable( argument ): return argument
    raise _intercept_exception_factory_provider(
        exception_factory_provider, validate_argument_invocability )(
            'argument_validation' )( name, invocation, 'invocable' )


def validate_attribute_name( exception_factory_provider, name ):
    ''' Validates attribute name as Python identifier. '''
    from .nomenclature import is_python_identifier
    if is_python_identifier( name ): return name
    raise _intercept_exception_factory_provider(
        exception_factory_provider, validate_attribute_name )(
            'attribute_name_illegality' )( name )


def validate_attribute_existence(
    exception_factory_provider, name, object_, extra_context = None
):
    ''' Validates attribute existence on object. '''
    if hasattr( object_, name ): return name
    raise _intercept_exception_factory_provider(
        exception_factory_provider, validate_attribute_existence )(
            'attribute_nonexistence' )(
                name, object_, extra_context = extra_context )


def validate_attribute_invocability(
    exception_factory_provider, name, object_, extra_context = None
):
    ''' Validates attribute invocability on object.

        Implies attribute existence validation. '''
    validate_attribute_existence(
        exception_factory_provider,
        name, object_, extra_context = extra_context )
    if callable( getattr( object_, name ) ): return name
    raise _intercept_exception_factory_provider(
        exception_factory_provider, validate_attribute_invocability )(
            'attribute_noninvocability' )(
                name, object_, extra_context = extra_context )


def _intercept_exception_factory_provider( provider, invocation ):
    ''' Encloses exception factory provider with interceptor. '''
    from .exceptionality import intercept_exception_factory_provider
    return intercept_exception_factory_provider( provider, invocation )
