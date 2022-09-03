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


''' Ensure correctness of base functionality. '''


from pytest import mark, raises

from lockup import NamespaceClass


class __( metaclass = NamespaceClass ):

    import types

    from functools import wraps

    from lockup.base import (
        Class,
        calculate_label,
        calculate_class_label,
        calculate_invocable_label,
        calculate_module_label,
        create_namespace,
        intercept,
        is_operational_name,
        is_public_or_operational_name,
        module_qualify_class_name,
        select_public_attributes,
        select_public_attributes,
    )
    from lockup.exceptions import (
        AbsentImplementation,
        FugitiveException,
        InaccessibleAttribute,
        IncorrectData,
        InvalidOperation,
        InvalidState,
        create_argument_validation_exception,
        create_implementation_absence_exception,
    )
    from lockup.validators import (
        validate_argument_invocability,
        validate_attribute_existence,
    )


def _decorator( invocable ):
    ''' Decorator used for testing wrapped functions. '''
    @__.wraps( invocable )
    def envelop_execution( *posargs, **nomargs ):
        ''' Completely transparent function wrapper. '''
        return invocable( *posargs, **nomargs )
    return envelop_execution

class _InvocableObject:
    ''' Produces invocable instances. '''

    def __call__( self ): return self

    def a_method( self ):
        ''' For testing bound methods on an instance. '''
        return self

    @_decorator
    def decorated_method( self ):
        ''' For testing decorated bound methods of an instance. '''
        return self

    class Inner:
        ''' Nested class for '__qualname__' testing. '''

        def generator( self ):
            ''' For testing generator methods. '''
            yield self

        async def agenerator( self ):
            ''' For testing async generator methods. '''
            yield self

        async def coroutine( self ):
            ''' For testing async methods. '''
            return self

_invocable_object = _InvocableObject( )
_inner_object = _InvocableObject.Inner( )
_invocables = (
    lambda: None, __.intercept, _InvocableObject,
    _invocable_object, _invocable_object.a_method,
)

class _A: red = 1
class _B( metaclass = NamespaceClass ): blue = 2
class _C: __slots__ = ( 'blue', 'red', )


def test_006_is_operational_name( ):
    ''' Verify valid operational Python identifier. '''
    assert __.is_operational_name( '__dict__' )


@mark.parametrize(
    'name', ( 'public', '_non_public', '__', '__nope', 'if', '123', )
)
def test_007_is_not_operational_name( name ):
    ''' Verify invalid operational Python identifier. '''
    assert not __.is_operational_name( name )


@mark.parametrize( 'name', ( 'public', '__dict__', ) )
def test_011_is_public_or_operational_name( name ):
    ''' Verify valid public or operational Python identifier. '''
    assert __.is_public_or_operational_name( name )


@mark.parametrize( 'name', ( '_non_public', '__', '__nope', 'if', '123', ) )
def test_012_is_not_public_or_operational_name( name ):
    ''' Verify invalid public or operational Python identifier. '''
    assert not __.is_public_or_operational_name( name )


@mark.parametrize(
    'class_',
    ( _InvocableObject,
      { '__module__': _InvocableObject.__module__,
        '__qualname__': _InvocableObject.__qualname__ } ) )
def test_016_module_qualify_class_name( class_ ):
    ''' Valid class or class dictionary qualifies name. '''
    assert f"{__name__}._InvocableObject" \
            == __.module_qualify_class_name( class_ )


@mark.parametrize(
    'class_',
    ( 123, { '__qualname__': 'A.B' }, { '__module__': 'me' }, ) )
def test_017_module_qualify_invalid_class_name( class_ ):
    ''' Invalid class or class dictionary raises exception. '''
    with raises( __.IncorrectData ): __.module_qualify_class_name( class_ )


@mark.parametrize(
    'class_, object_, includes, excludes, expectation',
    ( ( type, _A, ( ), ( ), [ 'mro', 'red' ] ),
      ( _A, _A( ), ( ), ( ), [ 'red' ] ),
      ( __.Class, NamespaceClass, ( ), ( ), [ 'mro' ] ),
      ( NamespaceClass, _B, ( ), ( ), [ 'blue' ] ),
      ( _C, _C( ), ( ), ( ), [ 'blue', 'red' ] ),
      ( _C, _C( ), ( '__str__', ), ( 'red', ), [ '__str__', 'blue' ] ) ) )
def test_021_select_public_attributes(
    class_, object_, includes, excludes, expectation
):
    ''' Verify selection of public attributes for given class and object. '''
    assert (
           expectation
        == sorted( __.select_public_attributes(
            class_, object_, includes = includes, excludes = excludes ) ) )


@mark.parametrize(
    'object_, expectation',
    ( ( __.types, "module 'types'" ),
      ( _InvocableObject,
        f"class '{__name__}._InvocableObject'" ),
      ( _invocable_object,
        f"instance of class '{__name__}._InvocableObject'" ) ) )
def test_031_calculate_label( object_, expectation ):
    ''' Label calculation is dispatched according to kind of object. '''
    assert expectation == __.calculate_label( object_ )


def test_032_calculate_label_on_invalid_module( ):
    ''' Invalid module raises exception for label calculation. '''
    with raises( __.IncorrectData ): __.calculate_module_label( 123 )


def test_041_calculate_class_label( ):
    ''' Calculate correct label for class object. '''
    assert (
           f"class '{__name__}._InvocableObject'"
        == __.calculate_class_label( _InvocableObject ) )


def test_042_calculate_class_dictionary_label( ):
    ''' Calculate correct label for class production dictionary. '''
    assert (
           f"class '{__name__}._InvocableObject'"
        == __.calculate_class_label( {
            '__module__': __name__, '__qualname__': '_InvocableObject' } ) )


def test_043_calculate_classes_label( ):
    ''' Calculate correct labels for multiple classes. '''
    assert (
           f"class '{__name__}._InvocableObject' or class 'builtins.module'"
        == __.calculate_class_label(
            ( _InvocableObject, __.types.ModuleType ) ) )


def test_044_calculate_class_attribute_label( ):
    ''' Calculate correct attribute label for class object. '''
    assert (
           f"function 'a_method' on class '{__name__}._InvocableObject'"
        == __.calculate_class_label(
            _InvocableObject, "function 'a_method'" ) )


@mark.parametrize(
    'invocable, expectation',
    ( ( lambda: None, f"lambda from module '{__name__}'" ),
      ( __.calculate_label,
        "function 'calculate_label' on module 'lockup.base'" ),
      ( _InvocableObject, f"class '{__name__}._InvocableObject'" ),
      ( _invocable_object,
        f"invocable instance of class '{__name__}._InvocableObject'" ),
      ( _invocable_object.a_method,
        f"method 'a_method' on instance "
        f"of class '{__name__}._InvocableObject'" ),
      ( _invocable_object.decorated_method,
        f"method 'decorated_method' on instance "
        f"of class '{__name__}._InvocableObject'" ),
      ( _inner_object.generator,
        f"generator method 'generator' on instance "
        f"of class '{__name__}._InvocableObject.Inner'" ),
      ( _inner_object.agenerator,
        f"async generator method 'agenerator' on instance "
        f"of class '{__name__}._InvocableObject.Inner'" ),
      ( _inner_object.coroutine,
        f"async method 'coroutine' on instance "
        f"of class '{__name__}._InvocableObject.Inner'" ),
      ( sorted, "builtin function 'sorted' on module 'builtins'" ),
    ) )
def test_051_calculate_invocable_label( invocable, expectation ):
    ''' Calculate correct label for invocable object. '''
    assert expectation == __.calculate_invocable_label( invocable )


@mark.parametrize( 'argument', _invocables )
def test_061_argument_validation_exception( argument ):
    ''' Validation exception is created from argument. '''
    def tester( argument ): return argument
    assert isinstance(
        __.create_argument_validation_exception(
            'argument', tester, type( argument ) ), __.IncorrectData )


def test_062_argument_validation_exception_with_label( ):
    ''' Validation exception with special label is created from argument. '''
    label = 'special integer'
    def tester( argument ): return argument
    result = __.create_argument_validation_exception(
        'argument', tester, label )
    assert isinstance( result, __.IncorrectData )
    assert label in str( result )


@mark.parametrize(
    'trial_function',
    ( sorted, lambda iterable: iterable, lambda *iterable: len( iterable ),
      lambda iterable = 1: iterable, lambda **iterable: len( iterable ) ) )
def test_063_argument_validation_exceptions( trial_function ):
    ''' Validation exception with different categories of arguments. '''
    assert isinstance(
        __.create_argument_validation_exception(
            'iterable', trial_function, object ), __.IncorrectData )


@mark.parametrize( 'argument', _invocables )
def test_066_implementation_absence_exception( argument ):
    ''' Validation exception is created from argument. '''
    assert isinstance(
        __.create_implementation_absence_exception( argument, 'something' ),
        __.AbsentImplementation )


@mark.parametrize( 'argument', _invocables )
def test_081_validate_invocable_argument( argument ):
    ''' Invocables are returned without alteration. '''
    def tester( argument ): return argument
    assert argument == __.validate_argument_invocability(
        argument, 'argument', tester )


@mark.parametrize( 'argument', ( 123, 'ph00b4r' * 5, ) )
def test_082_validate_noninvocable_argument( argument ):
    ''' Noninvocable objects causes exceptions. '''
    def tester( argument ): return argument
    with raises( __.IncorrectData ):
        __.validate_argument_invocability( argument, 'argument', tester )


def test_091_validate_attribute_existence( ):
    ''' Names of valid attributes are returned without alteration. '''
    assert 'a_method' == __.validate_attribute_existence(
        'a_method', _invocable_object )


def test_092_validate_attribute_nonexistence( ):
    ''' Nonexistent attributes cause exceptions. '''
    aname = 'ph00b4r' * 5
    with raises( __.InaccessibleAttribute ):
        __.validate_attribute_existence( aname, _invocable_object )


@mark.parametrize( 'value',
    ( None, 42, 'test', Exception, Exception( ), ( ), [ 42 ], ) )
def test_101_intercept_normal_return( value ):
    ''' Returns across package API boundary without alteration. '''

    @__.intercept
    def return_per_normal( value ): return value

    assert value == return_per_normal( value )


def test_102_intercept_fugitive_exception( ):
    ''' Non-package exception cannot cross package API boundary. '''

    @__.intercept
    def release_fugitive( ): return 1 / 0

    with raises( __.FugitiveException ): release_fugitive( )


@mark.parametrize( 'exception_class',
    ( __.InvalidOperation, __.InvalidState, ) )
def test_103_intercept_permissible_exception( exception_class ):
    ''' Package exception can cross package API boundary. '''

    @__.intercept
    def release_package_exception( exception_class ):
        raise exception_class( 'Something wicked comes this way!' )

    with raises( exception_class ):
        release_package_exception( exception_class )


def test_104_intercept_invalid_invocation( ):
    ''' Special report on invalid invocation arguments. '''

    @__.intercept
    def a_function( ): pass

    with raises( __.IncorrectData ):
        a_function( 123 )   # pylint: disable=too-many-function-args
