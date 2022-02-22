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

from functools import partial as partial_function
from os import environ as psenv, pathsep
from pathlib import Path
from pprint import pprint
from shlex import split as split_command
from sys import path as python_search_paths, stderr
from types import SimpleNamespace

from invoke import Exit

project_path = Path( __file__ ).parent.parent
python_search_paths.insert(
    0, str( project_path / '.local' / 'sources' / 'python3' ) )
from our_base import (
    collapse_multilevel_dictionary,
    identify_python,
    indicate_python_packages,
    paths,
    standard_execute_external,
)


# If running in a Github Workflow,
# then use 'stdout' for properly interleaved output.
if 'CI' in psenv:
    eprint = print
    epprint = pprint
else:
    eprint = partial_function( print, file = stderr )
    epprint = partial_function( pprint, stream = stderr )

# Flag if streams are attached to a TTY.
# Can use flag to suppress ANSI SGR codes for some programs.
on_tty = stderr.isatty( )


def derive_venv_context_options(
    venv_path = None, version = None, variables = None
):
    ''' Derives flags for Python virtual environment in execution context. '''
    venv_path = venv_path or derive_venv_path( version )
    return dict(
        env = derive_venv_variables( venv_path, variables = variables ),
        replace_env = True )


def derive_venv_path( version = None, python_path = None ):
    ''' Derives Python virtual environment path from version handle. '''
    if None is python_path:
        if version: python_path = detect_vmgr_python_path( version )
        elif 'VIRTUAL_ENV' in psenv and 'OUR_VENV_NAME' in psenv:
            venv_path = Path( psenv[ 'VIRTUAL_ENV' ] )
            if venv_path.name == psenv[ 'OUR_VENV_NAME' ]: return venv_path
    if None is python_path: python_path = detect_vmgr_python_path( )
    abi_label = identify_python(
        'bdist-compatibility', python_path = python_path )
    return paths.environments / abi_label


def derive_venv_variables( venv_path, variables = None ):
    ''' Derives environment variables from Python virtual environment path. '''
    variables = ( variables or psenv ).copy( )
    variables.pop( 'PYTHONHOME', None )
    variables[ 'PATH' ] = pathsep.join( (
        str( venv_path / 'bin' ), variables[ 'PATH' ] ) )
    variables[ 'VIRTUAL_ENV' ] = str( venv_path )
    variables[ 'OUR_VENV_NAME' ] = venv_path.name
    return variables


def detect_vmgr_python_path( version = None ):
    ''' Detects Python path using handle from version manager. '''
    version = version or detect_vmgr_python_version( )
    installation_path = Path( standard_execute_external(
        ( *split_command( 'asdf where python' ), version ) ).stdout.strip( ) )
    return installation_path / 'bin' / 'python'


def detect_vmgr_python_version( ):
    ''' Detects Python handle selected by version manager. '''
    return next( iter( indicate_python_versions_support( ) ) )


def indicate_python_versions_support( ):
    ''' Returns supported Python versions. '''
    version = psenv.get( 'ASDF_PYTHON_VERSION' )
    if None is not version: return ( version, )
    regex = re.compile( r'''^python\s+(.*)$''', re.MULTILINE )
    with paths.configuration.asdf.open( ) as file:
        return regex.match( file.read( ) )[ 1 ].split( )


def generate_pip_requirements_text( identifier = None ):
    ''' Generates Pip requirements lists from local configuration. '''
    # https://pip.pypa.io/en/stable/reference/requirements-file-format/
    # https://pip.pypa.io/en/stable/topics/repeatable-installs/
    simples, fixtures = indicate_python_packages( identifier = identifier )
    # Pip cannot currently mix frozen and unfrozen requirements,
    # so we must split them out. (As of 2022-02-06.)
    # https://github.com/pypa/pip/issues/6469
    raw, frozen, unpublished = [ ], [ ], [ ]
    for fixture in map( lambda d: SimpleNamespace( **d ), fixtures ):
        name = fixture.name
        if hasattr( fixture, 'url' ):
            unpublished.append( f"{name}@ {fixture.url}" )
        elif hasattr( fixture, 'digests' ):
            options = ' \\\n    '.join(
                f"--hash {digest}" for digest in fixture.digests )
            frozen.append( f"{name}=={fixture.version} \\\n    {options}" )
    raw.extend( collapse_multilevel_dictionary( simples ) )
    return '\n'.join( raw ), '\n'.join( frozen ), '\n'.join( unpublished )


def render_boxed_title( title ):
    ''' Renders box around title. '''
    columns_count = int( psenv.get( 'COLUMNS', 79 ) )
    icolumns_count = columns_count - 2
    content_template = (
        '\N{BOX DRAWINGS DOUBLE VERTICAL}{fill}'
        '\N{BOX DRAWINGS DOUBLE VERTICAL}' )
    return '\n'.join( (
        '',
        '\N{BOX DRAWINGS DOUBLE DOWN AND RIGHT}{fill}'
        '\N{BOX DRAWINGS DOUBLE DOWN AND LEFT}'.format(
            fill = '\N{BOX DRAWINGS DOUBLE HORIZONTAL}' * icolumns_count ),
        content_template.format( fill = ' ' * icolumns_count ),
        content_template.format( fill = title.center( icolumns_count ) ),
        content_template.format( fill = ' ' * icolumns_count ),
        '\N{BOX DRAWINGS DOUBLE UP AND RIGHT}{fill}'
        '\N{BOX DRAWINGS DOUBLE UP AND LEFT}'.format(
            fill = '\N{BOX DRAWINGS DOUBLE HORIZONTAL}' * icolumns_count ),
        '', ) )


# TODO: Check for cached passphrase as an alternative.
def assert_gpg_tty( ):
    ''' Ensures the the 'GPG_TTY' environment variable is set. '''
    if 'GPG_TTY' in psenv: return
    raise Exit(
        "ERROR: Environment variable 'GPG_TTY' is not set. "
        "Task cannot prompt for GPG secret key passphrase." )
