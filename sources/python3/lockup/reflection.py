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


''' Class reflection facilities.

    The type of :py:class:`type` is :py:class:`type`:

    >>> type( type ).__name__
    'type'

    You can imbue a class with similar behavior, if necessary:

    >>> class Class( type ): pass
    ...
    >>> type( Class ).__name__
    'type'
    >>> import lockup.reflection
    >>> lockup.reflection.reassign_class_factory( Class, Class, assert_implementation = False )  # doctest: +SKIP
    ...
    >>> type( Class ).__name__  # doctest: +SKIP
    'Class'

    The above technique is used internally within this package itself.

    .. note::
       This function only works on some flavors of Python, such as the
       reference implementation (CPython) and Pyston, at present. You can still
       use this package on other flavors of Python, but the reflection
       operation may not be implemented. ''' # pylint: disable=line-too-long


# Initialization Dependencies: (none)
# Latent Dependencies: (no cycles)


def reassign_class_factory( class_, factory, assert_implementation = True ):
    ''' Assigns new class factory (metaclass) to class.

        This technique is a way to overcome the problem of infinite regress
        when a class needs behaviors that it could otherwise only get from
        another class. Within this package, it is used to allow a class factory
        to enforce immutability upon itself, for example.

        If ``assert_implementation`` is true, then an exception will be raised
        if no reflector is implemented for the executing flavor of Python. '''
    from inspect import isclass as is_class
    from .exceptionality import our_exception_factory_provider
    if not is_class( class_ ):
        raise our_exception_factory_provider( 'argument_validation' )(
            'class_', reassign_class_factory, 'class' )
    if not is_class( factory ) or not issubclass( factory, type ):
        raise our_exception_factory_provider( 'argument_validation' )(
            'factory', reassign_class_factory, "subclass of 'type'" )
    from sys import implementation as python_implementation
    python_name = python_implementation.name
    if python_name in ( # pragma: no branch
        'cpython', 'pyston',
    ): return _reassign_cpython_class_factory( class_, factory )
    # TODO: pypy
    # Note: Update corresponding tests as Python flavors become supported.
    if assert_implementation: # pragma: no cover
        raise our_exception_factory_provider( 'implementation_absence' )(
            reassign_class_factory, f"Python implementation: {python_name}" )
    return factory # pragma: no cover


def _reassign_cpython_class_factory( class_, factory ): # pragma: no cover
    ''' CPython et al.: Assigns new class factory to class. '''
    from ctypes import Structure, c_ssize_t, c_void_p
    import sys
    # Detect if compiled with the 'TRACE_REFS' macro.
    trace_refs = hasattr( sys, 'getobjects' )
    class PyObject( Structure ):
        ''' Structural representation of :c:struct:`PyObject`. '''
        _fields_ = tuple( filter( None, (
            ( '_ob_next', c_void_p ) if trace_refs else None,
            ( '_ob_prev', c_void_p ) if trace_refs else None,
            ( 'ob_refcnt', c_ssize_t ),
            ( 'ob_type', c_void_p )
        ) ) )
    _perform_c_struct_surgery( PyObject, class_, factory )
    return class_


def _reassign_pypy_class_factory( class_, factory ): # pragma: no cover
    ''' PyPy: Assigns new class factory to class. '''
    # TODO: Find the secret sauce to make PyPy honor the metaclass change.
    #       Need to investigate, in more detail, how type lookups work in PyPy.
    #       Possible code of interest:
    #         https://foss.heptapod.net/pypy/pypy/-/blob/branch/default/pypy/objspace/std/typeobject.py
    from ctypes import Structure, c_ssize_t, c_void_p
    #from pypyjit import releaseall
    #releaseall( )
    class PyObject( Structure ):
        ''' Structural representation of :c:struct:`PyObject`. '''
        _fields_ = (
            ( 'ob_refcnt', c_ssize_t ),
            ( 'ob_pypy_link', c_ssize_t ),
            ( 'ob_type', c_void_p )
        )
    # Although there are admonitions against relying upon 'id'
    # to get the address of an object in PyPy, the class address from 'id'
    # _seems_ stable and reliable.
    _perform_c_struct_surgery( PyObject, class_, factory )
    #releaseall( )
    return class_


def _perform_c_struct_surgery( struct_class, class_, factory ):
    ''' Performs pointer and refernece count surgery on C structs. '''
    from ctypes import c_void_p
    nf_pointer = id( factory )
    o_struct = struct_class.from_address( id( class_ ) )
    of_pointer = o_struct.ob_type
    o_struct.ob_type = c_void_p( nf_pointer )
    nf_struct = struct_class.from_address( nf_pointer )
    nf_struct.ob_refcnt += 1 # pylint: disable=no-member
    of_struct = struct_class.from_address( of_pointer )
    of_struct.ob_refcnt -= 1 # pylint: disable=no-member
