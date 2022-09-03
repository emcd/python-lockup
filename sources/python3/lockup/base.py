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


''' Package foundation. Mostly internal classes and functions. '''


# Initialization Dependencies:
#   base -> interception
# Latent Dependencies:
#   base -> exceptions -> base


from .interception import (
    create_interception_decorator as _create_interception_decorator,
)


def _provide_exception( name ):
    ''' Lazily imports exceptions to prevent dependency cycles. '''
    from . import exceptions
    return getattr( exceptions, name )


# TODO: Privatize after move to new modules.
intercept = _create_interception_decorator( _provide_exception )
package_name = __package__.split( '.', maxsplit = 1 )[ 0 ]


#========================== Nomenclatural Utilities ==========================#


def calculate_label( object_, attribute_label = None ):
    ''' Produces human-comprehensible label, based on classification. '''
    from inspect import isclass as is_class, ismodule as is_module
    if is_module( object_ ):
        return calculate_module_label( object_, attribute_label )
    if is_class( object_ ):
        return calculate_class_label( object_, attribute_label )
    return calculate_instance_label( object_, attribute_label )

def calculate_class_label( classes, attribute_label = None ):
    ''' Produces human-comprehensible label for class or tuple of classes.

        Each provided class may be a class object or namespace dictionary
        that is present during class creation. '''
    from collections.abc import Mapping as Dictionary
    from inspect import isclass as is_class
    if is_class( classes ) or isinstance( classes, Dictionary ):
        classes = ( classes, )
    label = ' or '.join( map(
        lambda class_: "class '{}'".format(
            module_qualify_class_name( class_ ) ), classes ) )
    if None is not attribute_label: return f"{attribute_label} on {label}"
    return label

def calculate_module_label( module, attribute_label = None ):
    ''' Produces human-comprehensible label for module. '''
    from inspect import ismodule as is_module
    if not is_module( module ):
        from .exceptions import create_argument_validation_exception
        raise create_argument_validation_exception(
            'module', calculate_module_label, 'module' )
    label = f"module '{module.__name__}'"
    if None is not attribute_label: return f"{attribute_label} on {label}"
    return label

def calculate_instance_label( object_, attribute_label = None ):
    ''' Produces human-comprehensible label for instance of class. '''
    class_mqname = module_qualify_class_name( type( object_ ) )
    label = f"instance of class '{class_mqname}'"
    if None is not attribute_label: return f"{attribute_label} on {label}"
    return label

def calculate_invocable_label( invocable ):
    ''' Produces human-comprehensible label for invocable object.

        An invocable object may be a function, bound method, class,
        or invocable instance of a class. '''
    from .validators import validate_argument_invocability
    validate_argument_invocability(
        invocable, 'invocable', calculate_invocable_label )
    from inspect import isclass as is_class, isroutine as is_routine
    if is_routine( invocable ): return _calculate_routine_label( invocable )
    if is_class( invocable ): return calculate_class_label( invocable )
    if hasattr( invocable, '__call__' ):
        return "invocable {label}".format(
            label = calculate_instance_label( invocable ) )
    return _calculate_attribute_label(
        invocable, 'invocable attribute' ) # pragma: no cover

def _calculate_routine_label( routine ):
    ''' Produces human-comprehensible label for routine. '''
    # We assume that decorations have had 'functools.wraps' applied,
    # because inspecting '__closure__' cells is guesswork that we avoid.
    qname = routine.__qualname__
    module_label = f"module '{routine.__module__}'"
    import inspect
    if '<lambda>' == qname: return f"lambda from {module_label}"
    if inspect.ismethod( routine ):
        attribute_label = calculate_instance_label(
            routine.__self__, f"method '{routine.__name__}'" )
    else: attribute_label = _calculate_attribute_label( routine, 'function' )
    if inspect.isgeneratorfunction( routine ):
        attribute_label = f"generator {attribute_label}"
    elif inspect.isasyncgenfunction( routine ):
        attribute_label = f"async generator {attribute_label}"
    elif inspect.iscoroutinefunction( routine ):
        attribute_label = f"async {attribute_label}"
    if inspect.isbuiltin( routine ):
        attribute_label = f"builtin {attribute_label}"
    return attribute_label

def _calculate_attribute_label( attribute, label_base ):
    ''' Produces human-comprehensible label for attribute. '''
    mname = attribute.__module__
    name, qname = attribute.__name__, attribute.__qualname__
    alabel = f"{label_base} '{name}'"
    if name == qname: return f"{alabel} on module '{mname}'"
    return "{alabel} on class '{mname}.{class_qname}'".format(
        alabel = alabel, mname = mname,
        class_qname = qname.rsplit( '.', maxsplit = 1 )[ 0 ] )

def calculate_argument_label( name, invocation_signature ):
    ''' Produces human-comprehensible label for argument. '''
    # TODO: Implement argument validation.
    species = invocation_signature.parameters[ name ].kind
    position = next( # pragma: no branch
        position for position, name_
        in enumerate( invocation_signature.parameters ) if name_ == name )
    from inspect import Parameter as Variate
    if Variate.POSITIONAL_ONLY is species:
        return f"positional argument #{position}"
    if Variate.POSITIONAL_OR_KEYWORD is species:
        return f"argument '{name}' (position #{position})"
    if Variate.VAR_POSITIONAL is species:
        return f"sequence of extra positional arguments '{name}'"
    if Variate.VAR_KEYWORD is species:
        return f"dictionary of extra nominative arguments '{name}'"
    from .exceptions import InvalidState # pragma: no cover
    raise InvalidState


def module_qualify_class_name( class_ ):
    ''' Concatenates module name and qualified name of class.

        Also supports class namespace dictionaries. '''
    from inspect import isclass as is_class
    if is_class( class_ ): return f"{class_.__module__}.{class_.__qualname__}"
    try:
        module_name = class_[ '__module__' ]
        class_qname = class_[ '__qualname__' ]
        return f"{module_name}.{class_qname}"
    except ( KeyError, TypeError, ): pass
    from .exceptions import create_argument_validation_exception
    raise create_argument_validation_exception(
        'class_', module_qualify_class_name,
        'class or class namespace dictionary' )


def is_python_identifier( name ):
    ''' Is object a legal Python identifier? Excludes Python keywords. '''
    from keyword import iskeyword as is_keyword
    return (    isinstance( name, str )
            and name.isidentifier( ) and not is_keyword( name ) )


def is_public_name( name ):
    ''' Returns ``True`` if name is user-public.

        A user-public name does not begin with an underscore (``_``). '''
    return is_python_identifier( name ) and _is_public_name( name )

def _is_public_name( name ): return not name.startswith( '_' )

def is_operational_name( name ):
    ''' Returns ``True`` if name is operational.

        An operational name begins and ends
        with a double underscore (``__``). '''
    return is_python_identifier( name ) and _is_operational_name( name )

def _is_operational_name( name ):
    return (
            4 < len( name )
        and name.startswith( '__' ) and name.endswith( '__' )
        and '_' != name[ 2 ] and '_' != name[ -3 ] )

def is_public_or_operational_name( name ):
    ''' Returns ``True`` if name is user-public or operational.

        See :py:func:`is_public_name` and :py:func:`is_operational_name`
        for details. '''
    return (
            is_python_identifier( name )
        and ( _is_public_name( name ) or _is_operational_name( name ) ) )


@intercept
def select_public_attributes(
    class_, object_, *, includes = ( ), excludes = ( )
):
    ''' Selects all attributes with user-public names on object.

        Can optionally include specific attributes that would not be selected
        under normal operation and can exclude specific attributes that would
        selected under normal operation. '''
    from inspect import isclass as is_class
    names = (
          # Slotted object might not have '__dict__' attribute.
          getattr( object_, '__dict__', { } ).keys( )
          # Slots may be empty but still show in object's directory anyway.
        | frozenset( getattr( class_, '__slots__', ( ) ) )
          # What do we inherit?
        | frozenset( super( class_, object_ ).__dir__( *(
            # Classes in 'type' family bind '__dir__' differently.
            ( object_, )
            if is_class( object_ ) and issubclass( object_, type )
            else ( ) ) ) ) )
    return (
        name for name in names
        if      name not in excludes
            and ( name in includes or is_public_name( name ) ) )


#============================ Primal Class Factory ===========================#


class Class( type ):
    ''' Produces classes which have immutable attributes.

        Non-public attributes of each class are concealed from :py:func:`dir`.

        .. note::
           Only class attributes are immutable. Instances of immutable classes
           will have mutable attributes without additional intervention beyond
           the scope of this package. '''

    __module__ = package_name

    __slots__ = ( )

    @intercept
    def __new__( factory, name, bases, namespace ):
        return super( ).__new__( factory, name, bases, namespace )

    @intercept
    def __setattr__( class_, name, value ):
        from .validators import validate_attribute_name
        validate_attribute_name( name, class_ )
        from .exceptions import create_attribute_immutability_exception
        raise create_attribute_immutability_exception( name, class_ )

    @intercept
    def __delattr__( class_, name ):
        from .validators import (
            validate_attribute_name,
            validate_attribute_existence,
        )
        validate_attribute_name( name, class_ )
        validate_attribute_existence( name, class_ )
        from .exceptions import create_attribute_indelibility_exception
        raise create_attribute_indelibility_exception( name, class_ )

    @intercept
    def __dir__( class_ ): return select_public_attributes( __class__, class_ )


#============================ Additional Factories ===========================#


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

    __module__ = package_name

    @intercept
    def __new__( factory, name, bases, namespace ):
        for aname in namespace:
            if aname in ( '__doc__', '__module__', '__qualname__', ): continue
            if is_public_name( aname ): continue
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

    @intercept
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
        '__module__': package_name, '__qualname__': 'Namespace' }
    namespace.update( nomargs )
    return NamespaceClass( 'Namespace', ( ), namespace )
