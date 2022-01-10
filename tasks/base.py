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


''' Constants and utilities for project maintenance tasks. '''


import re

from collections.abc import Mapping as AbstractDictionary
from functools import partial as partial_function
from itertools import chain
from os import environ as psenv, pathsep
from pathlib import Path
from pprint import pprint
from sys import path as python_search_paths, stderr

project_path = Path( __file__ ).parent.parent
python_search_paths.insert(
    0, str( project_path / '.local' / 'sources' / 'python3' ) )
from our_base import (
    ensure_python_package,
    paths,
)


# If running in a Github Workflow,
# then use 'stdout' for properly interleaved output.
if 'CI' in psenv:
    eprint = print
    epprint = pprint
else:
    eprint = partial_function( print, file = stderr )
    epprint = partial_function( pprint, stream = stderr )


def derive_python_venv_execution_options(
        context, venv_path = None, variables = None
):
    ''' Derives flags for Python virtual environment in execution context. '''
    if None is venv_path:
        version = psenv.get( 'ASDF_PYTHON_VERSION' )
        if None is version:
            version = next( iter( indicate_python_versions_support( ) ) )
        venv_path = derive_python_venv_path( context, version )
    return dict(
        env = derive_python_venv_variables( venv_path, variables = variables ),
        replace_env = True )


def indicate_python_versions_support( ):
    ''' Returns supported Python versions. '''
    regex = re.compile( r'''^python\s+(.*)$''', re.MULTILINE )
    with paths.configuration.asdf.open( ) as file:
        return regex.match( file.read( ) )[ 1 ].split( )


def derive_python_venv_path( context, version, python_path = None ):
    ''' Derives Python virtual environment path from version handle. '''
    python_path = python_path or detect_vmgr_python_path( context, version )
    abi_detector_path = paths.scripts.d.python3 / 'report-abi.py'
    abi_tag = context.run(
        f"{python_path} {abi_detector_path} {version}",
        hide = 'stdout' ).stdout.strip( )
    return paths.environments / abi_tag


def derive_python_venv_variables( venv_path, variables = None ):
    ''' Derives environment variables from Python virtual environment path. '''
    variables = ( variables or psenv ).copy( )
    variables.pop( 'PYTHONHOME', None )
    variables[ 'PATH' ] = pathsep.join( (
        str( venv_path / 'bin' ), variables[ 'PATH' ] ) )
    variables[ 'VIRTUAL_ENV' ] = str( venv_path )
    return variables


def detect_vmgr_python_path( context, version ):
    ''' Detects Python path using version manager handle. '''
    installation_path = Path( context.run(
        f"asdf where python {version}", hide = 'stdout' ).stdout.strip( ) )
    return installation_path / 'bin' / 'python'


def generate_pip_requirements( folio = None ):
    ''' Generates Pip requirements list from packages folio.

        Uses the complete folio from local configuration by default. '''
    folio = collapse_multilevel_dictionary(
        folio or indicate_python_package_dependencies( ) )
    # TODO: Handle structured entries.
    return '\n'.join( folio )


def collapse_multilevel_dictionary( dictionary ):
    ''' Collapses a hierarchical dictionary into a list. '''
    return tuple( chain.from_iterable(
        (   collapse_multilevel_dictionary( value )
            if isinstance( value, AbstractDictionary ) else value )
        for value in dictionary.values( ) ) )


def indicate_python_package_dependencies( ):
    ''' Returns dictionary of Python package dependencies. '''
    ensure_python_package( 'tomli' )
    from tomli import load
    with paths.configuration.pypackages.open( 'rb' ) as file:
        return load( file )
