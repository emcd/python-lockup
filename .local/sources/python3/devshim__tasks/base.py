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


from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):

    import re

    from functools import partial as partial_function
    from os import (
        F_OK, R_OK, X_OK,
        access as test_fs_access, environ as psenv, pathsep,
    )
    from pathlib import Path
    from pprint import pprint
    from shlex import split as split_command
    from sys import stderr

    from invoke import Exit

    from devshim__base import (
        collapse_multilevel_dictionary,
        identify_python,
        indicate_python_packages,
        paths,
        standard_execute_external,
    )

    from lockup import create_namespace, reclassify_module


# If running in a Github Workflow,
# then use 'stdout' for properly interleaved output.
if 'CI' in __.psenv:
    eprint = print
    epprint = __.pprint
else:
    eprint = __.partial_function( print, file = __.stderr )
    epprint = __.partial_function( __.pprint, stream = __.stderr )

# Flag if streams are attached to a TTY.
# Can use flag to suppress ANSI SGR codes for some programs.
on_tty = __.stderr.isatty( )


def assert_sanity( ):
    ''' Assert that operational environment is sane. '''


def pep508_identify_python( version = None ):
    ''' Calculates PEP 508 identifier for Python version. '''
    python_path = detect_vmgr_python_path( version = version )
    return __.identify_python(
        'pep508-environment', python_path = python_path )


def test_package_executable(
    executable_name, process_environment = None, proper_package_name = None
):
    ''' Checks if executable from package is in environment.

        Is a proxy for determining if a package is installed. '''
    from os import environ as current_process_environment
    process_environment = process_environment or current_process_environment
    venv_path = process_environment.get( 'VIRTUAL_ENV' )
    if venv_path and is_executable_in_venv(
        executable_name, venv_path = venv_path
    ): return True
    from shutil import which
    search_path = process_environment.get( 'PATH' )
    if search_path and which( executable_name, path = search_path ):
        return True
    if not proper_package_name:
        proper_package_name = executable_name.capitalize( )
    eprint( f"{proper_package_name} not available. Skipping." )
    return False


def is_executable_in_venv( name, venv_path = None, version = None ):
    ''' Checks if file is executable from virtual environment.

        Preferable over :py:func:`shutil.which` since it will not erroneously
        pick up shims, such as Asdf uses. '''
    venv_path = __.Path( venv_path or derive_venv_path( version = version ) )
    for path in ( venv_path / 'bin' ).iterdir( ):
        if name != path.name: continue
        if __.test_fs_access( path, __.F_OK | __.R_OK | __.X_OK ): return True
    return False


def derive_venv_context_options(
    venv_path = None, version = None, variables = None
):
    ''' Derives flags for Python virtual environment in execution context. '''
    venv_path = __.Path( venv_path or derive_venv_path( version = version ) )
    return dict(
        env = derive_venv_variables( venv_path, variables = variables ),
        replace_env = True )


def derive_venv_path( version = None, python_path = None ):
    ''' Derives Python virtual environment path from version handle. '''
    if None is python_path:
        if version: python_path = detect_vmgr_python_path( version = version )
        elif 'VIRTUAL_ENV' in __.psenv and 'OUR_VENV_NAME' in __.psenv:
            venv_path = __.Path( __.psenv[ 'VIRTUAL_ENV' ] )
            if venv_path.name == __.psenv[ 'OUR_VENV_NAME' ]: return venv_path
    if None is python_path: python_path = detect_vmgr_python_path( )
    abi_label = __.identify_python(
        'bdist-compatibility', python_path = python_path )
    return __.paths.environments / abi_label


def derive_venv_variables( venv_path, variables = None ):
    ''' Derives environment variables from Python virtual environment path. '''
    variables = ( variables or __.psenv ).copy( )
    variables.pop( 'PYTHONHOME', None )
    variables[ 'PATH' ] = __.pathsep.join( (
        str( venv_path / 'bin' ), variables[ 'PATH' ] ) )
    variables[ 'VIRTUAL_ENV' ] = str( venv_path )
    variables[ 'OUR_VENV_NAME' ] = venv_path.name
    return variables


def detect_vmgr_python_path( version = None ):
    ''' Detects Python path using handle from version manager. '''
    version = version or detect_vmgr_python_version( )
    installation_path = __.Path( __.standard_execute_external(
        ( *__.split_command( 'asdf where python' ), version )
    ).stdout.strip( ) )
    return installation_path / 'bin' / 'python'


def detect_vmgr_python_version( ):
    ''' Detects Python handle selected by version manager. '''
    # TODO: If in venv, then get active Python version.
    return next( iter( indicate_python_versions_support( ) ) )


def indicate_python_versions_support( ):
    ''' Returns supported Python versions. '''
    version = __.psenv.get( 'ASDF_PYTHON_VERSION' )
    if None is not version: return ( version, )
    regex = __.re.compile( r'''^python\s+(.*)$''', __.re.MULTILINE )
    with __.paths.configuration.asdf.open( ) as file:
        return regex.match( file.read( ) )[ 1 ].split( )


def generate_pip_requirements_text( identifier = None ):
    ''' Generates Pip requirements lists from local configuration. '''
    # https://pip.pypa.io/en/stable/reference/requirements-file-format/
    # https://pip.pypa.io/en/stable/topics/repeatable-installs/
    simples, fixtures = __.indicate_python_packages( identifier = identifier )
    # Pip cannot currently mix frozen and unfrozen requirements,
    # so we must split them out. (As of 2022-02-06.)
    # https://github.com/pypa/pip/issues/6469
    raw, frozen, unpublished = [ ], [ ], [ ]
    for fixture in map( lambda d: __.create_namespace( **d ), fixtures ):
        name = fixture.name
        if hasattr( fixture, 'url' ):
            unpublished.append( f"{name}@ {fixture.url}" )
        elif hasattr( fixture, 'digests' ):
            options = ' \\\n    '.join(
                f"--hash {digest}" for digest in fixture.digests )
            frozen.append( f"{name}=={fixture.version} \\\n    {options}" )
    raw.extend( __.collapse_multilevel_dictionary( simples ) )
    return '\n'.join( raw ), '\n'.join( frozen ), '\n'.join( unpublished )


def render_boxed_title( title, supplement = None ):
    ''' Renders box around title to diagnostic stream. '''
    if None is supplement: specific_title = title
    else: specific_title = f"{title} ({supplement})"
    eprint( format_boxed_title( specific_title ) )


def format_boxed_title( title ):
    ''' Formats box around title as string. '''
    columns_count = int( __.psenv.get( 'COLUMNS', 79 ) )
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
    if 'GPG_TTY' in __.psenv: return
    raise __.Exit(
        "ERROR: Environment variable 'GPG_TTY' is not set. "
        "Task cannot prompt for GPG secret key passphrase." )


def unlink_recursively( path ):
    ''' Pure Python implementation of ``rm -rf``, essentially.

        Different than :py:func:`shutil.rmtree` in that it will also
        delete a regular file or symlink as the top-level target
        and it will silently succeed if the top-level target is missing. '''
    if not path.exists( ): return
    if not path.is_dir( ):
        path.unlink( )
        return
    dirs_stack = [ path ]
    for child_path in path.rglob( '*' ):
        if child_path.is_dir( ) and not child_path.is_symlink( ):
            dirs_stack.append( child_path )
            continue
        child_path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )


__.reclassify_module( __name__ )
