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
import shlex
import subprocess
import sys
import os

from collections.abc import Mapping as AbstractDictionary
from functools import partial as partial_function
from itertools import chain
from os import environ as psenv
from pathlib import Path
from pprint import pprint
from sys import stderr
from types import SimpleNamespace


# If running in a Github Workflow,
# then use 'stdout' for properly interleaved output.
if 'CI' in psenv:
    eprint = print
    epprint = pprint
else:
    eprint = partial_function( print, file = stderr )
    epprint = partial_function( pprint, stream = stderr )


def _calculate_paths( ):
    project_path = Path( __file__ ).parent.parent
    local_path = project_path / '.local'
    paths_ = SimpleNamespace(
        artifacts = local_path / 'artifacts',
        caches = local_path / 'caches',
        configuration = local_path / 'configuration',
        local = local_path,
        project = project_path,
        scm_modules = local_path / 'scm-modules',
        scripts = local_path / 'scripts',
        sources = project_path / 'sources',
        state = local_path / 'state',
        tests = project_path / 'tests',
        venvs = local_path / 'virtual-environments',
    )
    paths_.common = _calculate_common_paths( paths_ )
    paths_.python3 = _calculate_python3_paths( paths_ )
    paths_.sphinx = _calculate_sphinx_paths( paths_ )
    return paths_


def _calculate_common_paths( paths_ ):
    # Note: Does not exist yet. Placeholder for a future refactor.
    common_path = paths_.scm_modules / 'emcd-common'
    return SimpleNamespace(
        sources = common_path / 'sources',
    )


def _calculate_python3_paths( paths_ ):
    return SimpleNamespace(
        scripts = paths_.scripts / 'python3',
        sources = paths_.sources / 'python3',
        tests = paths_.tests / 'python3',
        venvs = paths_.venvs / 'python3',
    )


def _calculate_sphinx_paths( paths_ ):
    return SimpleNamespace(
        caches = paths_.caches / 'sphinx',
        sources = paths_.sources / 'sphinx',
    )


paths = _calculate_paths( )


def ensure_directory( path ):
    ''' Ensures existence of directory, creating if necessary. '''
    path.mkdir( parents = True, exist_ok = True )
    return path


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
    with ( paths.project / '.tool-versions' ).open( ) as file:
        return regex.match( file.read( ) )[ 1 ].split( )


def derive_python_venv_path( context, version, python_path = None ):
    ''' Derives Python virtual environment path from version handle. '''
    python_path = python_path or detect_vmgr_python_path( context, version )
    abi_detector_path = paths.python3.scripts / 'report-abi.py'
    abi_tag = context.run(
        f"{python_path} {abi_detector_path} {version}",
        hide = 'stdout' ).stdout.strip( )
    return paths.python3.venvs / abi_tag


def derive_python_venv_variables( venv_path, variables = None ):
    ''' Derives environment variables from Python virtual environment path. '''
    variables = ( variables or psenv ).copy( )
    variables.pop( 'PYTHONHOME', None )
    variables[ 'PATH' ] = os.pathsep.join( (
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
    ensure_python_development_package( 'tomli' )
    from tomli import load
    with ( paths.configuration / 'pypackages.toml' ).open( 'rb' ) as file:
        return load( file )


def ensure_python_development_package( package_name ):
    ''' Ensures availability of development support package. '''
    cache_path = ensure_directory( paths.caches / 'packages' / 'python3' )
    if cache_path not in sys.path: sys.path.insert( 0, cache_path )
    subprocess.run(
        ( *shlex.split( 'pip install --upgrade --target' ),
          cache_path, package_name ),
        check = True, capture_output = True )
    # TODO: Verify package installation and return path to it.
