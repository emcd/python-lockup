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

''' Project package management. '''


class __:

    from json import load as load_json
    from shlex import (
        split as split_command,
        quote as shell_quote,
    )
    from tempfile import NamedTemporaryFile
    from time import sleep
    from types import SimpleNamespace
    from urllib.error import URLError as UrlError
    from urllib.request import ( Request as HttpRequest, urlopen, )

    from .base import (
        generate_pip_requirements_text,
        on_tty,
        paths,
    )
    from our_base import (
        ensure_python_package,
        standard_execute_external,
    )


def calculate_python_packages_fixtures( environment ):
    ''' Calculates Python package fixtures, such as digests or URLs. '''
    fixtures = [ ]
    for entry in indicate_current_python_packages( environment ):
        requirement = entry.requirement
        fixture = dict( name = requirement.name )
        if 'editable' in entry.flags: continue
        if requirement.url: fixture.update( dict( url = requirement.url, ) )
        else:
            package_version = next( iter( requirement.specifier ) ).version
            fixture.update( dict(
                version = package_version,
                digests = tuple( map(
                    lambda s: f"sha256:{s}",
                    aggregate_pypi_release_digests(
                        requirement.name, package_version )
                ) )
            ) )
        fixtures.append( fixture )
    return fixtures


def record_python_packages_fixtures( identifier, fixtures ):
    ''' Records table of Python packages fixtures. '''
    __.ensure_python_package( 'tomli' )
    from tomli import load
    __.ensure_python_package( 'tomli-w' )
    from tomli_w import dump
    fixtures_path = __.paths.configuration.pypackages_fixtures
    if fixtures_path.exists( ):
        with fixtures_path.open( 'rb' ) as file: document = load( file )
    else: document = { }
    document[ identifier ] = fixtures
    with fixtures_path.open( 'wb' ) as file: dump( document, file )


def delete_python_packages_fixtures( identifier ):
    ''' Deletes table of Python packages fixtures. '''
    __.ensure_python_package( 'tomli' )
    from tomli import load
    __.ensure_python_package( 'tomli-w' )
    from tomli_w import dump
    fixtures_path = __.paths.configuration.pypackages_fixtures
    if not fixtures_path.exists( ): return
    with fixtures_path.open( 'rb' ) as file: document = load( file )
    if not identifier in document: return
    del document[ identifier ]
    with fixtures_path.open( 'wb' ) as file: dump( document, file )


pypi_release_digests_cache = { }
def aggregate_pypi_release_digests( name, version, index_url = '' ):
    ''' Aggregates hashes for release on PyPI. '''
    cache_index = ( index_url, name, version )
    digests = pypi_release_digests_cache.get( cache_index )
    if digests: return digests
    release_info = retrieve_pypi_release_information(
        name, version, index_url = index_url )
    digests = [
        package_info[ 'digests' ][ 'sha256' ]
        for package_info in release_info ]
    pypi_release_digests_cache[ cache_index ] = digests
    return digests


def retrieve_pypi_release_information( name, version, index_url = '' ): # pylint: disable=inconsistent-return-statements
    ''' Retrieves information about specific release on PyPI. '''
    index_url = index_url or 'https://pypi.org'
    # https://warehouse.pypa.io/api-reference/json.html#release
    request = __.HttpRequest(
        f"{index_url}/pypi/{name}/json",
        headers = { 'Accept': 'application/json', } )
    attempts_count_max = 2
    for attempts_count in range( attempts_count_max + 1 ):
        try:
            with __.urlopen( request ) as http_reader:
                return __.load_json( http_reader )[ 'releases' ][ version ]
        except ( KeyError, __.UrlError, ):
            if attempts_count_max == attempts_count: raise
            __.sleep( 2 ** attempts_count )


def install_python_packages( context, context_options, identifier = None ):
    ''' Installs required Python packages into virtual environment. '''
    raw, frozen, unpublished = __.generate_pip_requirements_text(
        identifier = identifier )
    context.run(
        'pip install --upgrade setuptools pip wheel',
        pty = __.on_tty, **context_options )
    if not identifier or not frozen:
        pip_options = [ ]
        if not identifier: pip_options.append( '--upgrade' )
        execute_pip_with_requirements(
            context, context_options, 'install', raw,
            pip_options = pip_options )
    else:
        pip_options = [ '--require-hashes' ]
        execute_pip_with_requirements(
            context, context_options, 'install', frozen,
            pip_options = pip_options )
    if unpublished:
        execute_pip_with_requirements(
            context, context_options, 'install', unpublished )
    # Pip cannot currently mix editable and digest-bound requirements,
    # so we must install editable packages separately. (As of 2022-02-06.)
    # https://github.com/pypa/pip/issues/4995
    context.run(
        'pip install --editable .', pty = __.on_tty, **context_options )


def indicate_current_python_packages( environment ):
    ''' Returns currently-installed Python packages. '''
    __.ensure_python_package( 'packaging' )
    from packaging.requirements import Requirement
    entries = [ ]
    for line in __.standard_execute_external(
        __.split_command( 'pip freeze' ), env = environment
    ).stdout.strip( ).splitlines( ):
        entry = __.SimpleNamespace( flags = [ ] )
        if line.startswith( '-e' ):
            entry.flags.append( 'editable' )
            # Replace '-e' with '{package_name}@'.
            line = ' '.join( (
                line.rsplit( '=', maxsplit = 1 )[ -1 ] + '@',
                line.split( ' ', maxsplit = 1 )[ 1 ]
            ) )
        entry.requirement = Requirement( line )
        entries.append( entry )
    return entries


def execute_pip_with_requirements(
    context, context_options, command, requirements, pip_options = None
):
    ''' Executes a Pip command with requirements. '''
    pip_options = pip_options or ( )
    # Unfortunately, Pip does not support reading requirements from stdin,
    # as of 2022-01-02. To workaround, we need to write and then read
    # a temporary file. More details: https://github.com/pypa/pip/issues/7822
    with __.NamedTemporaryFile( mode = 'w+' ) as requirements_file:
        requirements_file.write( requirements )
        requirements_file.flush( )
        context.run(
            "pip {command} {options} --requirement {requirements_file}".format(
                command = command,
                options = ' '.join( pip_options ),
                requirements_file = __.shell_quote( requirements_file.name ) ),
            pty = __.on_tty, **context_options )
