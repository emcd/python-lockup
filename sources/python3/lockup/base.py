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


# Note: This module contains a number of cyclic dependencies
#       between various definitions, which will either manifest as
#       undefined references or infinite recursion,
#       if module initialization leaves the "happy path".
#       This "fragility" comes from the nature of early bootstrapping.
#       Be cautious when introducing changes and be sure to test them well.
#       The module is highly robust once its initialization is complete.


base_package_name = __package__.split( '.', maxsplit = 1 )[ 0 ]


from sys import ( # pylint: disable=unused-import
    implementation as python_implementation,
    version_info as python_version,
)
from types import MappingProxyType as DictionaryProxy


class __:

    from collections.abc import Collection, Mapping as Dictionary
    from functools import wraps
    import inspect
    from inspect import (
        Parameter as Variate, Signature,
        isclass as is_class, isfunction as is_function, ismodule as is_module,
        isroutine as is_routine,
        signature as scan_signature, )
    from keyword import iskeyword as is_keyword
    from sys import modules


def intercept( invocation ):
    ''' Decorator to intercept fugitive exceptions.

        Fugitive exceptions are ones which are not expected
        to cross an API boundary. '''
    validate_argument_invocability( invocation, 'invocation', intercept )
    signature = __.scan_signature( invocation )
    @__.wraps( invocation )
    def interception_invoker( *things, **sundry ):
        # Validate that arguments correspond to function signature.
        try: signature.bind( *things, **sundry )
        except TypeError as exc:
            raise create_invocation_validation_exception(
                invocation, exc ) from exc
        try: return invocation( *things, **sundry )
        except ( InvalidState, InvalidOperation, ): raise
        # Prevent escape of impermissible exceptions.
        except BaseException as exc:
            raise FugitiveException from exc # pylint: disable=broad-except
    return interception_invoker


#============================ Internal Validaters ============================#


def validate_argument_invocability( argument, name, invocation ):
    ''' Validates argument as an invocable object, such as a function. '''
    if callable( argument ): return argument
    raise create_argument_validation_exception( name, invocation, 'invocable' )

def validate_attribute_name( name, context ):
    ''' Validates attribute name as Python identifier. '''
    if is_python_identifier( name ): return name
    label = calculate_label( context, f"attribute '{name}'" )
    raise InaccessibleAttribute( f"Illegal name for {label}." )

def validate_attribute_existence( name, context ):
    ''' Validates attribute exists on context object. '''
    if hasattr( context, name ): return name
    raise create_attribute_nonexistence_exception( name, context )


#======================== Internal Exception Factories =======================#


def create_argument_validation_exception(
    name, invocation, expectation_label
):
    ''' Creates error with context about invalid argument. '''
    signature = __.scan_signature( invocation )
    argument_label = _calculate_argument_label( name, signature )
    invocation_label = calculate_invocable_label( invocation )
    if not isinstance( expectation_label, str ):
        expectation_label = calculate_label( expectation_label )
    return IncorrectData(
        f"Invalid {argument_label} to {invocation_label}: "
        f"must be {expectation_label}" )

def create_attribute_nonexistence_exception( name, context ):
    ''' Creates error with context about nonexistent attribute. '''
    label = calculate_label( context, f"attribute '{name}'" )
    return InaccessibleAttribute(
        f"Attempt to access nonexistent {label}." )

def create_attribute_immutability_exception(
    name, context, action = 'assign'
):
    ''' Creates error with context about immutable attribute. '''
    label = calculate_label( context, f"attribute '{name}'" )
    return ImpermissibleAttributeOperation(
        f"Attempt to {action} immutable {label}." )

def create_attribute_indelibility_exception( name, context ):
    ''' Creates error with context about indelible attribute. '''
    label = calculate_label( context, f"attribute '{name}'" )
    return ImpermissibleAttributeOperation(
        f"Attempt to delete indelible {label}." )

def create_class_attribute_rejection_exception( name, class_ ):
    ''' Creates error with context about class attribute rejection. '''
    label = calculate_class_label( class_, f"attribute '{name}'" )
    return ImpermissibleOperation(
        f"Rejection of extant definition of {label}." )

def create_impermissible_instantiation_exception( class_ ):
    ''' Creates error with context about impermissible instantiation. '''
    label = calculate_class_label( class_ )
    return ImpermissibleOperation(
        f"Impermissible instantiation of {label}." )

def create_invocation_validation_exception( invocation, cause ):
    ''' Creates error with context about invalid invocation. '''
    label = calculate_invocable_label( invocation )
    return IncorrectData(
        f"Incompatible arguments for invocation of {label}: {cause}" )


#========================== Nomenclatural Utilities ==========================#


def calculate_label( object_, attribute_label = None ):
    ''' Produces human-comprehensible label, based on classification. '''
    if __.is_module( object_ ):
        return calculate_module_label( object_, attribute_label )
    if __.is_class( object_ ):
        return calculate_class_label( object_, attribute_label )
    return calculate_instance_label( object_, attribute_label )

def calculate_class_label( classes, attribute_label = None ):
    ''' Produces human-comprehensible label for class or tuple of classes.

        Each provided class may be a class object or namespace dictionary
        that is present during class creation. '''
    if __.is_class( classes ) or isinstance( classes, __.Dictionary ):
        classes = ( classes, )
    label = ' or '.join( map(
        lambda class_: "class '{}'".format(
            module_qualify_class_name( class_ ) ), classes ) )
    if None is not attribute_label: return f"{attribute_label} on {label}"
    return label

def calculate_module_label( module, attribute_label = None ):
    ''' Produces human-comprehensible label for module. '''
    if not __.is_module( module ):
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
    validate_argument_invocability(
        invocable, 'invocable', calculate_invocable_label )
    if __.is_routine( invocable ):
        return _calculate_routine_label( invocable )
    if __.is_class( invocable ):
        return calculate_class_label( invocable )
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
    if '<lambda>' == qname: return f"lambda from {module_label}"
    if __.inspect.ismethod( routine ):
        attribute_label = calculate_instance_label(
            routine.__self__, f"method '{routine.__name__}'" )
    else: attribute_label = _calculate_attribute_label( routine, 'function' )
    if __.inspect.isgeneratorfunction( routine ):
        attribute_label = f"generator {attribute_label}"
    elif __.inspect.isasyncgenfunction( routine ):
        attribute_label = f"async generator {attribute_label}"
    elif __.inspect.iscoroutinefunction( routine ):
        attribute_label = f"async {attribute_label}"
    if __.inspect.isbuiltin( routine ):
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

def _calculate_argument_label( name, invocation_signature ):
    ''' Produces human-comprehensible label for argument. '''
    species = invocation_signature.parameters[ name ].kind
    position = next( # pragma: no branch
        position for position, name_
        in enumerate( invocation_signature.parameters ) if name_ == name )
    if __.Variate.POSITIONAL_ONLY is species:
        return f"positional argument #{position}"
    if __.Variate.POSITIONAL_OR_KEYWORD is species:
        return f"argument '{name}' (position #{position})"
    if __.Variate.VAR_POSITIONAL is species:
        return f"sequence of extra positional arguments '{name}'"
    if __.Variate.VAR_KEYWORD is species:
        return f"dictionary of extra nominative arguments '{name}'"
    raise InvalidState # pragma: no cover


def module_qualify_class_name( class_ ):
    ''' Concatenates module name and qualified name of class.

        Also supports class namespace dictionaries. '''
    if __.is_class( class_ ):
        return f"{class_.__module__}.{class_.__qualname__}"
    try:
        module_name = class_[ '__module__' ]
        class_qname = class_[ '__qualname__' ]
        return f"{module_name}.{class_qname}"
    except ( KeyError, TypeError, ): pass
    raise create_argument_validation_exception(
        'class_', module_qualify_class_name,
        'class or class namespace dictionary' )


def is_python_identifier( name ):
    ''' Is object a legal Python identifier? Excludes Python keywords. '''
    return (    isinstance( name, str )
            and name.isidentifier( ) and not __.is_keyword( name ) )


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
    names = (
          # Slotted object might not have '__dict__' attribute.
          getattr( object_, '__dict__', { } ).keys( )
          # Slots may be empty but still show in object's directory anyway.
        | frozenset( getattr( class_, '__slots__', ( ) ) )
          # What do we inherit?
        | frozenset( super( class_, object_ ).__dir__( *(
            # Classes in 'type' family bind '__dir__' differently.
            ( object_, )
            if __.is_class( object_ ) and issubclass( object_, type )
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

    __module__ = base_package_name

    __slots__ = ( )

    @intercept
    def __new__( factory, name, bases, namespace ):
        return super( ).__new__( factory, name, bases, namespace )

    @intercept
    def __setattr__( class_, name, value ):
        validate_attribute_name( name, class_ )
        raise create_attribute_immutability_exception( name, class_ )

    @intercept
    def __delattr__( class_, name ):
        validate_attribute_name( name, class_ )
        validate_attribute_existence( name, class_ )
        raise create_attribute_indelibility_exception( name, class_ )

    @intercept
    def __dir__( class_ ): return select_public_attributes( __class__, class_ )


if python_implementation.name in ( 'cpython', ): # pragma: no branch

    def _make_god_unto_itself( factory ):
        ''' Turns a class factory class into the factory for itself. '''
        if not issubclass( factory, type ):
            raise InvalidState # pragma: no cover
        from ctypes import Structure, c_ssize_t, c_void_p, pythonapi
        # Detect whether CPython is compiled with the 'TRACE_REFS' macro.
        try: pythonapi._Py_ForgetReference # pylint: disable=protected-access
        except AttributeError: trace_refs = False
        else: trace_refs = True
        class PyObject( Structure ):
            ''' Structural representation of :c:struct:`PyObject`. '''
            _fields_ = tuple( filter( None, (
                ( '_ob_next', c_void_p ) if trace_refs else None,
                ( '_ob_prev', c_void_p ) if trace_refs else None,
                ( 'ob_refcnt', c_ssize_t ),
                ( 'ob_type', c_void_p )
            ) ) )
        f_pointer = id( factory )
        f_struct = PyObject.from_address( f_pointer )
        f_struct.ob_type = c_void_p( f_pointer )

    _make_god_unto_itself( Class )

# TODO: Find the secret sauce to make PyPy honor the metaclass change.
#       Need to investigate, in more detail, how type lookups work in PyPy.
#       Possible code of interest:
#         https://foss.heptapod.net/pypy/pypy/-/blob/branch/default/pypy/objspace/std/typeobject.py
#elif 'pypy' == python_implementation.name: # pragma: no branch
#
#    def _make_god_unto_itself( factory ):
#        if not issubclass( factory, type ):
#            raise InvalidState # pragma: no cover
#        from ctypes import Structure, c_ssize_t, c_void_p
#        #from pypyjit import releaseall
#        #releaseall( )
#        class PyObject( Structure ):
#            ''' Structural representation of :c:struct:`PyObject`. '''
#            _fields_ = tuple( (
#                ( 'ob_refcnt', c_ssize_t ),
#                ( 'ob_pypy_link', c_ssize_t ),
#                ( 'ob_type', c_void_p )
#            ) )
#        # Although there are admonitions against relying upon 'id'
#        # to get the address of an object in PyPy, the class address from 'id'
#        # _seems_ stable and reliable.
#        f_pointer = id( factory )
#        f_struct = PyObject.from_address( f_pointer )
#        f_struct.ob_type = c_void_p( f_pointer )
#        #releaseall( )
#
#    _make_god_unto_itself( Class )


#================================= Exceptions ================================#

# Note: Normally, we would define exceptions in a separate module.
#       However, due to bootstrapping constraints which are fairly unique
#       to this package, we define them in this module
#       and set their apparent module to a different module.


# pylint: disable=too-many-ancestors


class Exception0( BaseException, metaclass = Class ):
    ''' Base for all exceptions in the package. '''

    __module__ = f"{base_package_name}.exceptions"

    def __init__( self, *things, tags = None, **sundry ):
        self.tags = (
            DictionaryProxy( tags ) if isinstance( tags, __.Dictionary )
            else DictionaryProxy( { } ) )
        super( ).__init__( *things, **sundry )


#------------------------------ Object Interface -----------------------------#


class InvalidOperation( Exception0, Exception ):
    ''' Complaint about invalid operation. '''

    __module__ = f"{base_package_name}.exceptions"


class ImpermissibleOperation( InvalidOperation, TypeError ):
    ''' Complaint about impermissible operation. '''

    __module__ = f"{base_package_name}.exceptions"


class ImpermissibleAttributeOperation(
    ImpermissibleOperation, AttributeError
):
    ''' Complaint about impermissible attribute operation.

        Cannot use :py:exc:`ImpermissibleOperation` because some packages,
        such as Sphinx Autodoc, expect an :py:exc:`AttributeError`. '''

    __module__ = f"{base_package_name}.exceptions"


class InaccessibleEntity( InvalidOperation ):
    ''' Complaint about attempt to retrieve inaccessible entity. '''

    __module__ = f"{base_package_name}.exceptions"


class InaccessibleAttribute( InaccessibleEntity, AttributeError ):
    ''' Complaint about attempt to retrieve inaccessible attribute.

        Cannot use :py:exc:`InaccessibleEntity` because some Python internals
        expect an :py:exc:`AttributeError`. '''

    __module__ = f"{base_package_name}.exceptions"


class IncorrectData( InvalidOperation, TypeError, ValueError ):
    ''' Complaint about incorrect data for invocation or operation. '''

    __module__ = f"{base_package_name}.exceptions"


#------------------------------- Internal State ------------------------------#


class InvalidState( Exception0, Exception ):
    ''' Alert about invalid internal state in the package.

        Owner of problem: maintainers of this package. '''

    __module__ = f"{base_package_name}.exceptions"

    def __init__( self, supplement = None ):
        # TODO: Add issue tracker information to message.
        super( ).__init__( ' '.join( filter( None, (
            f"Invalid internal state encountered "
            f"in package '{base_package_name}'.",
            supplement,
            f"Please report this error to the package maintainers." ) ) ) )


class FugitiveException( InvalidState, RuntimeError ):
    ''' Alert about fugitive exception intercepted at API boundary.

        An fugitive exception is one which is not intended
        to be reported across the package API boundary.
        Fugitive exceptions include Python built-ins,
        such as :py:exc:`IndexError`. '''

    __module__ = f"{base_package_name}.exceptions"


# pylint: enable=too-many-ancestors


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

    __module__ = base_package_name

    @intercept
    def __new__( factory, name, bases, namespace ):
        for aname in namespace:
            if aname in ( '__doc__', '__module__', '__qualname__', ): continue
            if is_public_name( aname ): continue
            raise create_class_attribute_rejection_exception(
                aname, namespace )
        def __new__( kind, *posargs, **nomargs ): # pylint: disable=unused-argument
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
        '__module__': base_package_name, '__qualname__': 'Namespace' }
    namespace.update( nomargs )
    return NamespaceClass( 'Namespace', ( ), namespace )
