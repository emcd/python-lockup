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


# Initialization Dependencies:
#   factories -> _base
#   factories -> visibility
# Latent Dependencies:
#   factories -> exceptions -> factories
# pylint: disable=cyclic-import


from ._base import (
    intercept as _intercept,
    package_name as _package_name,
    provide_exception as _provide_exception,
)
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

    __module__ = _package_name

    __slots__ = ( )

    @_intercept
    def __new__( factory, name, bases, namespace ):
        return super( ).__new__( factory, name, bases, namespace )

    @_intercept
    def __setattr__( class_, name, value ):
        from .validators import validate_attribute_name
        validate_attribute_name( name, class_ )
        from .exceptions import create_attribute_immutability_exception
        raise create_attribute_immutability_exception( name, class_ )

    @_intercept
    def __delattr__( class_, name ):
        from .validators import (
            validate_attribute_name,
            validate_attribute_existence,
        )
        validate_attribute_name( name, class_ )
        validate_attribute_existence( name, class_ )
        from .exceptions import create_attribute_indelibility_exception
        raise create_attribute_indelibility_exception( name, class_ )

    @_intercept
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

    __module__ = _package_name

    @_intercept
    def __new__( factory, name, bases, namespace ):
        for aname in namespace:
            if aname in ( '__doc__', '__module__', '__qualname__', ): continue
            if _is_public_name( aname ): continue
            # Lazy import of 'create_class_attribute_rejection_exception' to
            # avoid cycle with use of internal namespace in the exceptions
            # module happy path at module initialization time.
            raise _provide_exception(
                'create_class_attribute_rejection_exception' )(
                    aname, namespace )
        def __new__( kind, *posargs, **nomargs ): # pylint: disable=unused-argument
            from .exceptions import (
                create_impermissible_instantiation_exception,
            )
            raise create_impermissible_instantiation_exception( kind )
        namespace[ '__new__' ] = __new__
        return super( ).__new__( factory, name, bases, namespace )

    @_intercept
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
    namespace = {
        '__module__': _package_name, '__qualname__': 'Namespace' }
    namespace.update( nomargs )
    return NamespaceClass( 'Namespace', ( ), namespace )
