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


''' Concealment and immutability of class and namespace attributes. '''


from .interception import our_interceptor as _our_interceptor
from .visibility import (
    is_public_name as _is_public_name,
    select_public_attributes as _select_public_attributes,
)


class Class( type ):
    ''' Produces classes which have immutable attributes.

        Non-public attributes of each class are concealed from :py:func:`dir`.

        .. note::
           Only class attributes are immutable. Instances of immutable classes
           will have mutable attributes without additional intervention beyond
           the scope of this package. '''

    __slots__ = ( )

    @_our_interceptor
    def __new__( factory, name, bases, namespace ):
        return super( ).__new__( factory, name, bases, namespace )

    @_our_interceptor
    def __setattr__( class_, name, value ):
        from .exceptionality import our_exception_factory_provider
        from .validators import validate_attribute_name
        validate_attribute_name( our_exception_factory_provider, name )
        raise our_exception_factory_provider(
            'attribute_immutability' )( name, class_ )

    @_our_interceptor
    def __delattr__( class_, name ):
        from .exceptionality import our_exception_factory_provider
        from .validators import (
            validate_attribute_name,
            validate_attribute_existence,
        )
        validate_attribute_name( our_exception_factory_provider, name )
        validate_attribute_existence(
            our_exception_factory_provider, name, class_ )
        raise our_exception_factory_provider(
            'attribute_indelibility' )( name, class_ )

    @_our_interceptor
    def __dir__( class_ ):
        return _select_public_attributes( __class__, class_ )


class NamespaceClass( Class, metaclass = Class ):
    ''' Produces namespace classes which have immutable attributes.

        Each produced namespace is a unique class, which cannot be
        instantiated.

        Non-public attributes of each class are concealed from :py:func:`dir`.

        .. warning::
           Although most descriptor attributes will be inert on a class,
           :py:func:`types.DynamicClassAttribute` and similar, may trigger
           attribute errors when accessed. However, these are a fairly rare
           case and are probably not needed on namespaces, in general. '''

    @_our_interceptor
    def __new__( factory, name, bases, namespace ):
        for aname in namespace:
            if aname in ( '__doc__', '__module__', '__qualname__', ): continue
            if _is_public_name( aname ): continue
            from .exceptionality import our_exception_factory_provider
            raise our_exception_factory_provider(
                'class_attribute_rejection' )( aname, namespace )
        def __new__( kind, *posargs, **nomargs ): # pylint: disable=unused-argument
            from .exceptionality import our_exception_factory_provider
            raise our_exception_factory_provider(
                'impermissible_instantiation' )( kind )
        namespace[ '__new__' ] = __new__
        return super( ).__new__( factory, name, bases, namespace )

    @_our_interceptor
    def __repr__( kind ):
        namespace = {
            '__module__': kind.__module__, '__qualname__': kind.__qualname__ }
        namespace.update( kind.__dict__ )
        return "{kind}( {name!r}, {bases!r}, {{ {namespace} }} )".format(
            kind = type( kind ).__qualname__,
            name = kind.__name__,
            bases = tuple( ( base.__qualname__ for base in kind.__bases__ ) ),
            namespace = ", ".join( (
                f"{aname!r}: {avalue!r}" for aname, avalue
                in namespace.items( ) ) ) )


def create_namespace( **nomargs ):
    ''' Creates immutable namespaces from nominative arguments. '''
    from .nomenclature import calculate_apex_package_name
    namespace = {
        '__module__': calculate_apex_package_name( __package__ ),
        '__qualname__': 'Namespace' }
    namespace.update( nomargs )
    return NamespaceClass( 'Namespace', ( ), namespace )


def _reassign_class_factories( ):
    ''' Reassigns class factories for internal classes.

        If Python implementation does not support class reflection,
        we can still provide functionality without the extra protection. '''
    from inspect import isclass as is_class
    from . import exceptions
    from .exceptionality.our_factories import ExtraData
    from .reflection import reassign_class_factory
    reassign_class_factory(
        Class, Class, assert_implementation = False )
    for aname in dir( exceptions ):
        attribute = getattr( exceptions, aname )
        if not is_class( attribute ): continue
        if not issubclass( attribute, exceptions.Omniexception ): # pragma: no cover
            continue
        reassign_class_factory(
            attribute, Class, assert_implementation = False )
    reassign_class_factory( ExtraData, Class, assert_implementation = False )

_reassign_class_factories( )
