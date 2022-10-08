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


''' Ensure correctness of exception factories and their produce. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exceptions
    from lockup.exceptionality import (
        intercept_exception_class_provider,
        intercept_exception_factory_provider,
        our_exception_class_provider,
        our_exception_factory_provider,
    )
    from lockup.exceptionality.our_factories import (
        ExtraData,
        create_argument_validation_exception,
        create_implementation_absence_exception,
    )
    from lockup.interception import our_interceptor


from .invocables import InvocableObject as _InvocableObject
_invocable_object = _InvocableObject( )
_invocables = (
    lambda: None, __.our_interceptor, _InvocableObject,
    _invocable_object, _invocable_object.a_method,
)


def test_011_intercept_factory_provider( ):
    ''' Ensures validation and decoration of factory provider. '''
    provider = __.intercept_exception_factory_provider(
        __.our_exception_factory_provider,
        test_011_intercept_factory_provider )
    assert callable( provider )
    assert (
        __.create_argument_validation_exception # pylint: disable=comparison-with-callable
        == provider( 'argument_validation' ).__wrapped__.func )


def test_017_error_invalid_argument_vector_for_factory_provider( ):
    ''' Expect error on invalid argument vector for factory provider. '''
    provider = __.intercept_exception_factory_provider(
        __.our_exception_factory_provider,
        test_017_error_invalid_argument_vector_for_factory_provider )
    with raises( __.exceptions.InvalidOperation ): provider( )


def _faulty_factory_provider( name ):
    ''' Provides exception factories. Not really. '''
    raise RuntimeError( 'lol' )

def test_018_error_faulty_factory_provider( ):
    ''' Expect error on faulty factory provider. '''
    provider = __.intercept_exception_factory_provider(
        _faulty_factory_provider, test_018_error_faulty_factory_provider )
    with raises( __.exceptions.InvalidState ):
        provider( 'argument_validation' )


def test_021_intercept_factory( ):
    ''' Ensures validation and decoration of factory. '''
    provider = __.intercept_exception_factory_provider(
        __.our_exception_factory_provider, test_021_intercept_factory )
    factory = provider( 'inaccessible_entity' )
    assert callable( factory )
    assert isinstance(
        factory( 'foo', 'a Bar' ), __.exceptions.InvalidOperation )


def _provide_invalid_factory( name ): # pylint: disable=unused-argument
    ''' Provides exception factory that explodes. '''
    return 123

def test_026_error_invalid_factory( ):
    ''' Expect error on invalid factory. '''
    provider = __.intercept_exception_factory_provider(
        _provide_invalid_factory, test_026_error_invalid_factory )
    with raises( __.exceptions.IncorrectData ):
        provider( 'inaccessible_entity' )


def test_027_error_invalid_argument_vector_for_factory( ):
    ''' Expect error on invalid argument vector for factory. '''
    provider = __.intercept_exception_factory_provider(
        __.our_exception_factory_provider,
        test_027_error_invalid_argument_vector_for_factory )
    factory = provider( 'inaccessible_entity' )
    with raises( __.exceptions.InvalidOperation ): factory( )


def _provide_faulty_factory( name ): # pylint: disable=unused-argument
    ''' Provides exception factory that explodes. '''
    return _faulty_factory

def _faulty_factory( ):
    ''' Produces exceptions. Not really. '''
    raise RuntimeError( 'lol' )

def test_028_error_faulty_factory( ):
    ''' Expect error on faulty factory. '''
    provider = __.intercept_exception_factory_provider(
        _provide_faulty_factory, test_028_error_faulty_factory )
    factory = provider( 'inaccessible_entity' )
    with raises( __.exceptions.InvalidState ): factory( )


def _provide_corrupt_factory( name ): # pylint: disable=unused-argument
    ''' Provides exception factory that produces non-exceptions. '''
    return _corrupt_factory

def _corrupt_factory( ):
    ''' Produces exceptions. Not really. '''
    return None

def test_029_error_corrupt_factory( ):
    ''' Expect error on factory that produces non-exceptions. '''
    provider = __.intercept_exception_factory_provider(
        _provide_corrupt_factory, test_029_error_corrupt_factory )
    factory = provider( 'inaccessible_entity' )
    with raises( __.exceptions.InvalidState ): factory( )


def test_031_intercept_class_provider( ):
    ''' Ensures validation and decoration of class provider. '''
    provider = __.intercept_exception_class_provider(
        __.our_exception_class_provider,
        test_031_intercept_class_provider )
    assert callable( provider )
    assert __.exceptions.InvalidOperation is provider( 'InvalidOperation' )


def test_037_error_invalid_argument_vector_for_class_provider( ):
    ''' Expect error on invalid argument vector for class provider. '''
    provider = __.intercept_exception_class_provider(
        __.our_exception_class_provider,
        test_037_error_invalid_argument_vector_for_class_provider )
    with raises( __.exceptions.InvalidOperation ): provider( )


def _faulty_class_provider( name ):
    ''' Provides exception classes. Not really. '''
    raise RuntimeError( 'lol' )

def test_038_error_faulty_class_provider( ):
    ''' Expect error on faulty class provider. '''
    provider = __.intercept_exception_class_provider(
        _faulty_class_provider, test_038_error_faulty_class_provider )
    with raises( __.exceptions.InvalidState ): provider( 'InvalidOperation' )


def _corrupt_class_provider( name ): # pylint: disable=unused-argument
    ''' Provides exception classes. Not really. '''
    return None

def test_039_error_corrupt_class_provider( ):
    ''' Expect error on corrupt class provider. '''
    provider = __.intercept_exception_class_provider(
        _corrupt_class_provider, test_039_error_corrupt_class_provider )
    with raises( __.exceptions.InvalidState ): provider( 'InvalidOperation' )


@mark.parametrize( 'name', ( 'ph00b4r' * 5, 123, ) )
def test_116_error_invalid_exception_class_name( name ):
    ''' Error on attempt to provide nonexistent exception class. '''
    with raises( __.exceptions.InvalidOperation ):
        __.our_exception_class_provider( name )


@mark.parametrize( 'name', ( 'ph00b4r' * 5, 123, ) )
def test_126_error_invalid_exception_factory_name( name ):
    ''' Error on attempt to provide nonexistent exception factory. '''
    with raises( __.exceptions.InvalidOperation ):
        __.our_exception_factory_provider( name )


def test_211_argument_validation_exception( ):
    ''' Validation exception is created from argument. '''
    expectation = 'special integer'
    def tester( argument ): return argument
    extra_data = __.ExtraData(
        nominative_arguments = dict( exception_labels = { } ) )
    result = __.our_exception_factory_provider( 'argument_validation' )(
        'argument', tester, expectation, extra_data = extra_data )
    assert isinstance( result, __.exceptions.IncorrectData )
    assert expectation in str( result )


@mark.parametrize(
    'trial_function',
    ( sorted, lambda iterable: iterable, lambda *iterable: len( iterable ),
      lambda iterable = 1: iterable, lambda **iterable: len( iterable ) ) )
def test_212_argument_validation_exceptions( trial_function ):
    ''' Validation exception with different categories of arguments. '''
    assert isinstance(
        __.our_exception_factory_provider( 'argument_validation' )(
            'iterable', trial_function, 'function' ),
        __.exceptions.IncorrectData )


@mark.parametrize( 'provider', ( 123, 'ph00b4r' * 5 ) )
def test_216_argument_validation_exception_invalid_provider( provider ):
    ''' Cannot create validation exception because of invalid provider. '''
    def tester( argument ): return argument
    with raises( __.exceptions.IncorrectData ):
        __.create_argument_validation_exception(
            provider, 'argument', tester, 'whatever' )


@mark.parametrize( 'invocation', ( 123, 'ph00b4r' * 5 ) )
def test_217_argument_validation_exception_invalid_invocation( invocation ):
    ''' Cannot create validation exception because of invalid invocation. '''
    with raises( __.exceptions.IncorrectData ):
        __.our_exception_factory_provider( 'argument_validation' )(
            'argument', invocation, 'whatever' )


@mark.parametrize( 'expectation', ( 123, lambda: None ) )
def test_218_argument_validation_exception_invalid_expectation( expectation ):
    ''' Cannot create validation exception because of invalid expectation. '''
    def tester( argument ): return argument
    with raises( __.exceptions.IncorrectData ):
        __.our_exception_factory_provider( 'argument_validation' )(
            'argument', tester, expectation )


def test_251_attribute_nonexistence_exception( ):
    ''' Ensures exception creation. '''
    class Object: ''' Trivial test class. '''
    object_ = Object( )
    tracer = 'ph00b4r' * 5
    result = __.our_exception_factory_provider( 'attribute_nonexistence' )(
        'attribute', object_, extra_context = tracer )
    assert isinstance( result, __.exceptions.InvalidOperation )
    assert tracer in str( result )


def test_261_attribute_noninvocability_exception( ):
    ''' Validation exception is created from arguments. '''
    class Object: ''' Trivial test class. '''
    object_ = Object( )
    object_.attribute = 1 # pylint: disable=attribute-defined-outside-init
    tracer = 'ph00b4r' * 5
    result = __.our_exception_factory_provider( 'attribute_noninvocability' )(
        'attribute', object_, extra_context = tracer )
    assert isinstance( result, __.exceptions.InvalidOperation )
    assert tracer in str( result )


@mark.parametrize( 'argument', _invocables )
def test_301_implementation_absence_exception( argument ):
    ''' Validation exception is created from argument. '''
    assert isinstance(
        __.our_exception_factory_provider( 'implementation_absence' )(
            argument, 'something' ),
        __.exceptions.AbsentImplementation )


def test_321_invalid_state_exception( ):
    ''' Invalid state exception is created from arguments. '''
    tracer = 'ph00b4r' * 5
    result = __.our_exception_factory_provider( 'invalid_state' )(
        tracer, __package__ )
    assert isinstance( result, __.exceptions.InvalidState )
    assert tracer in str( result )


def test_331_invocation_validation_exception( ):
    ''' Validation exception is created from arguments. '''
    def tester( argument ): return argument
    assert isinstance(
        __.our_exception_factory_provider( 'invocation_validation' )(
            tester, 'mismatched arguments' ),
        __.exceptions.IncorrectData )
