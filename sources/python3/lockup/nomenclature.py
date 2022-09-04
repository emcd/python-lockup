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


# Initialization Dependencies:
#   nomenclature -> base
# Latent Dependencies:
#   nomenclature -> exceptions -> nomenclature
#   nomenclature -> validators -> nomenclature
# pylint: disable=cyclic-import


from .base import intercept as _intercept


# TODO: Wrap all functions with interceptors.
# TODO: Make semi-private validation-free versions of the functions
#       for performance.

@_intercept
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
    if is_routine( invocable ): return calculate_routine_label( invocable )
    if is_class( invocable ): return calculate_class_label( invocable )
    if hasattr( invocable, '__call__' ):
        return "invocable {label}".format(
            label = calculate_instance_label( invocable ) )
    return calculate_attribute_label(
        invocable, 'invocable attribute' ) # pragma: no cover

def calculate_routine_label( routine ):
    ''' Produces human-comprehensible label for routine. '''
    # TODO: Implement argument validation.
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
    # TODO: Implement argument validation.
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
