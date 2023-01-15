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


''' Assert basic characteristics of package and all modules therein. '''


from importlib import import_module
from itertools import chain, repeat
from pathlib import Path

from pytest import mark, raises
from hypothesis import given, settings as ht_settings_maker
from hypothesis.strategies import from_regex


package_name = 'lockup'
package = import_module( package_name )


ht_settings = ht_settings_maker( print_blob = True )


def _scan_module_attributes( module ):
    # TODO? Retrieve base class attributes too.
    module_class = type( module )
    return sorted( set( chain(
        getattr( module, '__dict__', { } ).keys( ),
        getattr( module, '__slots__', ( ) ),
        getattr( module_class, '__dict__', { } ).keys( ),
        getattr( module_class, '__slots__', ( ) ),
    ) ) )


# pylint: disable=invalid-name


def test_001_package_public_interface( ):
    ''' Package directory only exposes public interface. '''
    assert not any( map( lambda a: a.startswith( '_' ), dir( package ) ) )


@given( from_regex( r'[\w][\w\d]*', fullmatch = True ) )
@ht_settings
def test_002_package_immutable_vs_assignment( attribute_name ):
    ''' Package is immutable versus attribute assignment. '''
    with raises( Exception ): setattr( package, attribute_name, True )


@mark.parametrize( 'attribute_name', _scan_module_attributes( package ) )
def test_003_package_immutable_vs_reassignment( attribute_name ):
    ''' Package is immutable versus attribute reassignment. '''
    with raises( Exception ): setattr( package, attribute_name, True )


@mark.parametrize( 'attribute_name', _scan_module_attributes( package ) )
def test_004_package_immutable_vs_deletion( attribute_name ):
    ''' Package is immutable versus attribute deletion. '''
    with raises( Exception ): delattr( package, attribute_name )


module_names = tuple( chain(
    (   path.stem for path in Path( package.__file__ ).parent.glob( '*.py' )
        if '__init__.py' != path.name ),
    (   path.name for path in Path( package.__file__ ).parent.glob( '*' )
        if '__pycache__' != path.name and path.is_dir( ) ) ) )

attributes_by_module = tuple( chain.from_iterable(
    tuple( zip(
        repeat( module_name ),
        _scan_module_attributes(
            # nosemgrep: python.lang.security.audit.non-literal-import
            import_module( f".{module_name}", package_name ) ) ) )
    for module_name in module_names ) )


@mark.parametrize( 'module_name', module_names )
def test_011_module_public_interface( module_name ):
    ''' Module directory only exposes public interface. '''
    # nosemgrep: python.lang.security.audit.non-literal-import
    module = import_module( f".{module_name}", package_name )
    assert not any( map( lambda a: a.startswith( '_' ), dir( module ) ) )

# Note: The following tests are probably overkill. Ensuring that the root
#       module of the package is protected should be sufficient.

#@mark.parametrize( 'module_name', module_names )
#@given( from_regex( r'[\w][\w\d]*', fullmatch = True ) )
#@ht_settings
#def test_012_module_immutable_vs_assignment( module_name, attribute_name ):
#    ''' Module is immutable versus attribute assignment. '''
#    module = import_module( f".{module_name}", package_name )
#    with raises( Exception ): setattr( module, attribute_name, True )


#@mark.parametrize( 'module_name,attribute_name', attributes_by_module )
#def test_013_module_immutable_vs_reassignment( module_name, attribute_name ):
#    ''' Module is immutable versus attribute reassignment. '''
#    module = import_module( f".{module_name}", package_name )
#    with raises( Exception ): setattr( module, attribute_name, True )


#@mark.parametrize( 'module_name,attribute_name', attributes_by_module )
#def test_014_module_immutable_vs_deletion( module_name, attribute_name ):
#    ''' Module is immutable versus attribute deletion. '''
#    module = import_module( f".{module_name}", package_name )
#    with raises( Exception ): delattr( module, attribute_name )
