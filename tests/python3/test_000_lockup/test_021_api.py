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


''' Ensure correctness of package API. '''


from pytest import mark, raises

from lockup import NamespaceClass


class __( metaclass = NamespaceClass ):

    from importlib import import_module
    from sys import implementation as python_implementation
    python_name = python_implementation.name

    from lockup import exceptions
    from lockup import (
        Module,
        NamespaceClass,
        create_interception_decorator,
        reclassify_module,
        reflect_class_factory_per_se,
    )


def test_211_produce_namespace( ):
    ''' Normal production of namespace. '''

    class Namespace( metaclass = __.NamespaceClass ):
        ''' Test namespace. '''

        answer = 42

    assert isinstance( Namespace, __.NamespaceClass )


def test_212_fail_to_produce_instantiable_namespace( ):
    ''' No production of namespace with possible instantiation. '''

    with raises( __.exceptions.InvalidOperation ):

        class Namespace( metaclass = __.NamespaceClass ):
            ''' Test namespace. '''

            def __new__( class_, *pos_arguments, **nom_arguments ):
                return super( class_, __.NamespaceClass ).__new__(
                    *pos_arguments, **nom_arguments )

        del Namespace


def test_301_reclassify_module_object( ):
    ''' Module instance can be reclassified. '''
    # NOTE: Must NOT reclassify any module that we use in our package during
    #       testing. This causes nasty dependency cycles / infinite recursion
    #       during exception generation, likely due to Pytest's modification of
    #       the import mechanism. Choose ones which are "obscure" relative to
    #       the purpose of our package.
    import bisect
    __.reclassify_module( bisect )
    assert isinstance( bisect, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        bisect.bisect_left = bisect.bisect_right


def test_302_reclassify_module_by_name( ):
    ''' Module can be reclassified by import name. '''
    # NOTE: Must NOT reclassify any module that we use in our package during
    #       testing. This causes nasty dependency cycles / infinite recursion
    #       during exception generation, likely due to Pytest's modification of
    #       the import mechanism. Choose ones which are "obscure" relative to
    #       the purpose of our package.
    import numbers
    __.reclassify_module( 'numbers' )
    assert isinstance( numbers, __.Module )
    with raises( __.exceptions.ImpermissibleAttributeOperation ):
        numbers.Complex = numbers.Real


def test_303_reclassify_module_idempotence( ):
    ''' Module reclassification is idempotent. '''
    assert isinstance( __.exceptions, __.Module )
    __.reclassify_module( __.exceptions )
    assert isinstance( __.exceptions, __.Module )


@mark.parametrize( 'module', ( 123, 'ph00b4r' * 5, ) )
def test_304_reclassify_invalid_module( module ):
    ''' Only modules may be reclassified. '''
    with raises( __.exceptions.IncorrectData ):
        __.reclassify_module( module )


@mark.skipif(
    __.python_name not in (
        'cpython', 'pyston',
    ),
    reason = f"Functionality not supported on '{__.python_name}'."
)
def test_401_reflect_class_factory( ):
    ''' Class factory class can be made into a factory of itself. '''
    class TrivialFactory( type ): ''' Trivial class factory class. '''
    assert issubclass( TrivialFactory, type )
    factory = __.reflect_class_factory_per_se(
        TrivialFactory, assert_implementation = False )
    assert issubclass( TrivialFactory, TrivialFactory )
    assert factory is TrivialFactory


@mark.parametrize( 'factory', ( 123, 'ph00b4r' * 5, ) )
def test_402_reflect_invalid_class_factory( factory ):
    ''' Only class factory classes can be reflected. '''
    with raises( __.exceptions.IncorrectData ):
        __.reflect_class_factory_per_se( factory )


def _provide_exception( name ):
    ''' Simple exception provider. '''
    from lockup import exceptions
    return getattr( exceptions, name )


def test_501_create_interception_decorator( ):
    ''' Interception decorator receives invocable and returns invocable. '''
    decorator = __.create_interception_decorator(
        exception_provider = _provide_exception )
    assert callable( decorator )


@mark.parametrize( 'provider', ( 123, 'ph00b4r' * 5, ) )
def test_502_interceptor_creation_with_invalid_exception_provider( provider ):
    ''' Only class factory classes can be reflected. '''
    with raises( __.exceptions.IncorrectData ):
        __.create_interception_decorator( exception_provider = provider )


def test_506_translate_fugitive_with_interceptor( ):
    ''' Interception decorator intercepts and translates fugitives. '''
    decorator = __.create_interception_decorator(
        exception_provider = _provide_exception )
    @decorator
    def raise_divide_by_zero( ): 1 / 0 # pylint: disable=pointless-statement
    with raises( __.exceptions.FugitiveException ):
        raise_divide_by_zero( )


@mark.parametrize(
    'exception_class', (
        __.exceptions.InvalidOperation,
        __.exceptions.InvalidState,
    )
)
def test_507_relay_permissible_with_interceptor( exception_class ):
    ''' Interception decorator relays permissible exceptions. '''
    decorator = __.create_interception_decorator(
        exception_provider = _provide_exception )
    @decorator
    def raise_permissible_exception( ): raise exception_class
    with raises( exception_class ):
        raise_permissible_exception( )
