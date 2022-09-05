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


''' Ensure correctness of nomenclatural functions. '''


from pytest import mark, raises

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    import types
    from functools import wraps
    from inspect import signature as scan_signature

    from lockup._base import intercept
    from lockup.exceptions import IncorrectData
    from lockup.nomenclature import (
        calculate_argument_label,
        calculate_class_label,
        calculate_invocable_label,
        calculate_label,
        calculate_module_label,
        module_qualify_class_name,
    )


from . import invocables as _invocables
from .invocables import InvocableObject as _InvocableObject
_invocable_object = _InvocableObject( )
_inner_object = _InvocableObject.Inner( )


@mark.parametrize(
    'class_',
    ( _InvocableObject,
      { '__module__': _InvocableObject.__module__,
        '__qualname__': _InvocableObject.__qualname__ } ) )
def test_011_module_qualify_class_name( class_ ):
    ''' Valid class or class dictionary qualifies name. '''
    assert ( f"{_invocables.__name__}.InvocableObject"
        == __.module_qualify_class_name( class_ ) )


@mark.parametrize(
    'class_',
    ( 123, { '__qualname__': 'A.B' }, { '__module__': 'me' }, ) )
def test_012_module_qualify_invalid_class_name( class_ ):
    ''' Invalid class or class dictionary raises exception. '''
    with raises( __.IncorrectData ): __.module_qualify_class_name( class_ )


@mark.parametrize(
    'object_, expectation',
    ( ( __.types, "module 'types'" ),
      ( _InvocableObject,
        f"class '{_invocables.__name__}.InvocableObject'" ),
      ( _invocable_object,
        f"instance of class '{_invocables.__name__}.InvocableObject'" ) ) )
def test_021_calculate_label( object_, expectation ):
    ''' Label calculation is dispatched according to kind of object. '''
    assert expectation == __.calculate_label( object_ )


def test_022_calculate_label_on_invalid_module( ):
    ''' Invalid module raises exception for label calculation. '''
    with raises( __.IncorrectData ): __.calculate_module_label( 123 )


def test_031_calculate_class_label( ):
    ''' Calculate correct label for class object. '''
    assert ( f"class '{_invocables.__name__}.InvocableObject'"
        == __.calculate_class_label( _InvocableObject ) )


def test_032_calculate_class_dictionary_label( ):
    ''' Calculate correct label for class production dictionary. '''
    assert ( f"class '{__name__}._InvocableObject'"
        == __.calculate_class_label( {
            '__module__': __name__, '__qualname__': '_InvocableObject' } ) )


def test_033_calculate_classes_label( ):
    ''' Calculate correct labels for multiple classes. '''
    assert (
           f"class '{_invocables.__name__}.InvocableObject' "
           "or class 'builtins.module'"
        == __.calculate_class_label(
            ( _InvocableObject, __.types.ModuleType ) ) )


def test_034_calculate_class_attribute_label( ):
    ''' Calculate correct attribute label for class object. '''
    assert (
           f"function 'a_method' on class "
           f"'{_invocables.__name__}.InvocableObject'"
        == __.calculate_class_label(
            _InvocableObject, "function 'a_method'" ) )


@mark.parametrize(
    'invocable, expectation',
    (
        ( lambda: None, f"lambda from module '{__name__}'" ),
        ( __.calculate_label,
          "function 'calculate_label' on module 'lockup.nomenclature'" ),
        ( _InvocableObject,
          f"class '{_invocables.__name__}.InvocableObject'" ),
        ( _invocable_object,
          f"invocable instance of class "
          f"'{_invocables.__name__}.InvocableObject'" ),
        ( _invocable_object.a_method,
          f"method 'a_method' on instance "
          f"of class '{_invocables.__name__}.InvocableObject'" ),
        ( _invocable_object.decorated_method,
          f"method 'decorated_method' on instance "
          f"of class '{_invocables.__name__}.InvocableObject'" ),
        ( _inner_object.generator,
          f"generator method 'generator' on instance "
          f"of class '{_invocables.__name__}.InvocableObject.Inner'" ),
        ( _inner_object.agenerator,
          f"async generator method 'agenerator' on instance "
          f"of class '{_invocables.__name__}.InvocableObject.Inner'" ),
        ( _inner_object.coroutine,
          f"async method 'coroutine' on instance "
          f"of class '{_invocables.__name__}.InvocableObject.Inner'" ),
        ( sorted, "builtin function 'sorted' on module 'builtins'" ),
    )
)
def test_041_calculate_invocable_label( invocable, expectation ):
    ''' Calculate correct label for invocable object. '''
    assert expectation == __.calculate_invocable_label( invocable )


@mark.parametrize(
    'invocable, expectation',
    (
        # TODO: Positional-only argument once Python 3.8 is baseline.
        ( lambda foo: None, "argument 'foo' (position #0)" ),
        ( lambda *foo: None,
          "sequence of extra positional arguments 'foo'" ),
        ( lambda *, foo = 42: None, "argument 'foo'" ),
        ( lambda **foo: None,
          "dictionary of extra nominative arguments 'foo'" ),
    )
)
def test_051_calculate_argument_label( invocable, expectation ):
    ''' Calculate correct argument label for invocation signature. '''
    signature = __.scan_signature( invocable )
    assert expectation == __.calculate_argument_label( 'foo', signature )

@mark.parametrize( 'name', ( 123, 'ph00b4r' * 5 ) )
def test_052_calculate_argument_label_with_invalid_name( name ):
    ''' Error on attempt to calculate argument label for invalid name. '''
    signature = __.scan_signature( lambda foo: None )
    with raises( __.IncorrectData ):
        __.calculate_argument_label( name, signature )

def test_053_calculate_argument_label_with_nonexistent_name( ):
    ''' Error on attempt to calculate argument label for nonexistent name. '''
    signature = __.scan_signature( lambda foo: None )
    with raises( __.IncorrectData ):
        __.calculate_argument_label( 'bar', signature )

def test_054_calculate_argument_label_with_invalid_signature( ):
    ''' Error on attempt to calculate argument label for invalid signature. '''
    with raises( __.IncorrectData ):
        __.calculate_argument_label( 'bar', None )
