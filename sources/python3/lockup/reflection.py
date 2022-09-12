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


''' Class reflection facilities. '''


# Initialization Dependencies: (none)
# Latent Dependencies: (no cycles)


def reflect_class_factory_per_se( factory, assert_implementation = True ):
    ''' Turns a class factory class into the factory for itself.

        This technique is a way to overcome the problem of infinite regress
        when a class needs behaviors that it could otherwise only get from
        another class. Within this package, it is used to allow a class factory
        to enforce immutability upon itself, for example.

        If ``assert_implementation`` is true, then an exception will be raised
        if no reflector is implemented for the executing flavor of Python. '''
    from inspect import isclass as is_class
    from ._exceptionality import exception_controller
    if not is_class( factory ) or not issubclass( factory, type ):
        raise exception_controller.provide_factory( 'argument_validation' )(
            'factory', reflect_class_factory_per_se, "subclass of 'type'" )
    from sys import implementation as python_implementation
    python_name = python_implementation.name
    if python_name in ( # pragma: no branch
        'cpython', 'pyston',
    ): return _reflect_cpython_class_factory_per_se( factory )
    # TODO: pypy
    # Note: Update corresponding tests as Python flavors become supported.
    if assert_implementation: # pragma: no cover
        raise exception_controller.provide_factory( 'implementation_absence' )(
            reflect_class_factory_per_se,
            f"Python implementation: {python_name}" )
    return factory # pragma: no cover


def _reflect_cpython_class_factory_per_se( factory ): # pragma: no cover
    ''' Performs pointer surgery on Python object struct. '''
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
    f_pointer = id( factory )
    f_struct = PyObject.from_address( f_pointer )
    f_struct.ob_type = c_void_p( f_pointer )
    return factory


def _reflect_pypy_class_factory_per_se( factory ): # pragma: no cover
    ''' Performs pointer surgery and updates class cache. '''
    # TODO: Find the secret sauce to make PyPy honor the metaclass change.
    #       Need to investigate, in more detail, how type lookups work in PyPy.
    #       Possible code of interest:
    #         https://foss.heptapod.net/pypy/pypy/-/blob/branch/default/pypy/objspace/std/typeobject.py
    from ctypes import Structure, c_ssize_t, c_void_p
    #from pypyjit import releaseall
    #releaseall( )
    class PyObject( Structure ):
        ''' Structural representation of :c:struct:`PyObject`. '''
        _fields_ = tuple( (
            ( 'ob_refcnt', c_ssize_t ),
            ( 'ob_pypy_link', c_ssize_t ),
            ( 'ob_type', c_void_p )
        ) )
    # Although there are admonitions against relying upon 'id'
    # to get the address of an object in PyPy, the class address from 'id'
    # _seems_ stable and reliable.
    f_pointer = id( factory )
    f_struct = PyObject.from_address( f_pointer )
    f_struct.ob_type = c_void_p( f_pointer )
    #releaseall( )
