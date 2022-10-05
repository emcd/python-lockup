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


''' Nomenclatural utilities. '''


# Latent Dependencies:
#   nomenclature -> exceptionality -> nomenclature
# pylint: disable=cyclic-import


def calculate_apex_package_name( source ):
    ''' Calculates name of apex package from module object or package name. '''
    from inspect import ismodule as is_module
    if is_module( source ): package_name = source.__package__
    elif isinstance( source, str ): package_name = source
    else:
        raise _provide_exception_factory( 'argument_validation' )(
            'source', calculate_apex_package_name,
            'module object or complete package name' )
    return package_name.split( '.', maxsplit = 1 )[ 0 ]


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
    if not attribute_label: return label
    if not isinstance( attribute_label, str ):
        raise _provide_exception_factory( 'argument_validation' )(
            'attribute_label', calculate_class_label, 'string' )
    return f"{attribute_label} on {label}"


def calculate_module_label( module, attribute_label = None ):
    ''' Produces human-comprehensible label for module. '''
    from inspect import ismodule as is_module
    if not is_module( module ):
        raise _provide_exception_factory( 'argument_validation' )(
            'module', calculate_module_label, 'module' )
    label = f"module '{module.__name__}'"
    if not attribute_label: return label
    if not isinstance( attribute_label, str ):
        raise _provide_exception_factory( 'argument_validation' )(
            'attribute_label', calculate_module_label, 'string' )
    return f"{attribute_label} on {label}"


def calculate_instance_label( object_, attribute_label = None ):
    ''' Produces human-comprehensible label for instance of class. '''
    class_mqname = module_qualify_class_name( type( object_ ) )
    label = f"instance of class '{class_mqname}'"
    if not attribute_label: return label
    if not isinstance( attribute_label, str ):
        raise _provide_exception_factory( 'argument_validation' )(
            'attribute_label', calculate_instance_label, 'string' )
    return f"{attribute_label} on {label}"


def calculate_invocable_label( invocable ):
    ''' Produces human-comprehensible label for invocable object.

        An invocable object may be a function, bound method, class,
        or invocable instance of a class. '''
    if not callable( invocable ):
        raise _provide_exception_factory( 'argument_validation' )(
            'invocable', calculate_invocable_label, 'invocable object' )
    from inspect import isclass as is_class, isroutine as is_routine
    if is_routine( invocable ): return calculate_routine_label( invocable )
    if is_class( invocable ): return calculate_class_label( invocable )
    if hasattr( invocable, '__call__' ):
        return "invocable {label}".format(
            label = calculate_instance_label( invocable ) )
    return calculate_attribute_label(
        invocable, 'invocable attribute' ) # pragma: no cover


def calculate_routine_label( routine ):
    ''' Produces human-comprehensible label for routine. '''
    if not callable( routine ):
        raise _provide_exception_factory( 'argument_validation' )(
            'routine', calculate_routine_label, 'routine' )
    argument_label = calculate_argument_label(
        'routine', calculate_routine_label )
    if not hasattr( routine, '__module__' ): # pragma: no cover
        raise _provide_exception_factory( 'attribute_nonexistence' )(
            '__module__', routine, extra_context = argument_label )
    if not hasattr( routine, '__name__' ): # pragma: no cover
        raise _provide_exception_factory( 'attribute_nonexistence' )(
            '__name__', routine, extra_context = argument_label )
    # We assume that decorations have had 'functools.wraps' applied,
    # because inspecting '__closure__' cells is guesswork that we avoid.
    qname = routine.__qualname__
    module_label = f"module '{routine.__module__}'"
    import inspect
    if '<lambda>' == qname: return f"lambda from {module_label}"
    if inspect.ismethod( routine ):
        attribute_label = calculate_instance_label(
            routine.__self__, f"method '{routine.__name__}'" )
    else: attribute_label = calculate_attribute_label( routine, 'function' )
    if inspect.isgeneratorfunction( routine ):
        attribute_label = f"generator {attribute_label}"
    elif inspect.isasyncgenfunction( routine ):
        attribute_label = f"async generator {attribute_label}"
    elif inspect.iscoroutinefunction( routine ):
        attribute_label = f"async {attribute_label}"
    if inspect.isbuiltin( routine ):
        attribute_label = f"builtin {attribute_label}"
    return attribute_label


def calculate_attribute_label( attribute, label_base ):
    ''' Produces human-comprehensible label for attribute. '''
    argument_label = calculate_argument_label(
        'attribute', calculate_attribute_label )
    if not hasattr( attribute, '__module__' ): # pragma: no cover
        raise _provide_exception_factory( 'attribute_nonexistence' )(
            '__module__', attribute, extra_context = argument_label )
    if not hasattr( attribute, '__name__' ): # pragma: no cover
        raise _provide_exception_factory( 'attribute_nonexistence' )(
            '__name__', attribute, extra_context = argument_label )
    if not hasattr( attribute, '__qualname__' ): # pragma: no cover
        raise _provide_exception_factory( 'attribute_nonexistence' )(
            '__qualname__', attribute, extra_context = argument_label )
    if not isinstance( label_base, str ):
        raise _provide_exception_factory( 'argument_validation' )(
            'label_base', calculate_attribute_label, 'string' )
    mname = attribute.__module__
    name, qname = attribute.__name__, attribute.__qualname__
    alabel = f"{label_base} '{name}'"
    if name == qname: return f"{alabel} on module '{mname}'"
    return "{alabel} on class '{mname}.{class_qname}'".format(
        alabel = alabel, mname = mname,
        class_qname = qname.rsplit( '.', maxsplit = 1 )[ 0 ] )


def calculate_argument_label( name, signature ):
    ''' Produces human-comprehensible label for argument. '''
    from inspect import Signature, signature as scan_signature
    if callable( signature ): signature = scan_signature( signature )
    elif not isinstance( signature, Signature ):
        raise _provide_exception_factory( 'argument_validation' )(
            'signature', calculate_argument_label,
            "instance of class 'inspect.Signature' or invocable object" )
    if not isinstance( name, str ) or name not in signature.parameters:
        raise _provide_exception_factory( 'argument_validation' )(
            'name', calculate_argument_label, 'name of valid argument' )
    species = signature.parameters[ name ].kind
    from inspect import Parameter as Variate
    if Variate.POSITIONAL_ONLY is species:
        position = _locate_argument_position( name, signature )
        return f"positional argument #{position}"
    if Variate.POSITIONAL_OR_KEYWORD is species:
        position = _locate_argument_position( name, signature )
        return f"argument '{name}' (position #{position})"
    if Variate.VAR_POSITIONAL is species:
        return f"sequence of extra positional arguments '{name}'"
    if Variate.KEYWORD_ONLY is species:
        return f"argument '{name}'"
    if Variate.VAR_KEYWORD is species:
        return f"dictionary of extra nominative arguments '{name}'"
    raise _provide_exception_factory( 'invalid_state' )( # pragma: no cover
        f"No recognition of argument species '{species}'.", __package__ )

def _locate_argument_position( name, signature ):
    ''' Locates position of argument in signature of invocable. '''
    return next( # pragma: no branch
        position for position, name_
        in enumerate( signature.parameters ) if name_ == name )


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
    raise _provide_exception_factory( 'argument_validation' )(
        'class_', module_qualify_class_name,
        'class or class namespace dictionary' )


def is_python_identifier( name ):
    ''' Is object a legal Python identifier? Excludes Python keywords. '''
    from keyword import iskeyword as is_keyword
    return (    isinstance( name, str )
            and name.isidentifier( )
            and not is_keyword( name ) )


def _provide_exception_factory( name ):
    ''' Provides package-internal exception factory. '''
    from .exceptionality import our_exception_factory_provider
    return our_exception_factory_provider( name )
