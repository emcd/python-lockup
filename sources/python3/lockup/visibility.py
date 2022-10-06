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


''' Functions for controlling and determining attribute visibility. '''


from inspect import isclass as _is_class

from .nomenclature import is_python_identifier as _is_python_identifier


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
            if _is_class( object_ ) and issubclass( object_, type )
            else ( ) ) ) ) )
    return (
        name for name in names
        if      name not in excludes
            and ( name in includes or is_public_name( name ) ) )


def is_public_or_operational_name( name ):
    ''' Returns ``True`` if name is user-public or operational.

        See :py:func:`is_public_name` and :py:func:`is_operational_name`
        for details. '''
    return (
            _is_python_identifier( name )
        and ( _is_public_name( name ) or _is_operational_name( name ) ) )

def is_operational_name( name ):
    ''' Returns ``True`` if name is operational.

        An operational name begins and ends
        with a double underscore (``__``). '''
    return _is_python_identifier( name ) and _is_operational_name( name )

def _is_operational_name( name ):
    return (
            4 < len( name )
        and name.startswith( '__' ) and name.endswith( '__' )
        and '_' != name[ 2 ] and '_' != name[ -3 ] )

def is_public_name( name ):
    ''' Returns ``True`` if name is user-public.

        A user-public name does not begin with an underscore (``_``). '''
    return _is_python_identifier( name ) and _is_public_name( name )

def _is_public_name( name ): return not name.startswith( '_' )
