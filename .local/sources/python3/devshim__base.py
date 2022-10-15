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


from functools import partial as partial_function
from shlex import split as split_command
from subprocess import run
from types import SimpleNamespace


standard_execute_external = partial_function(
    run, check = True, capture_output = True, text = True )


def _configure( ):
    ''' Configure development support. '''
    from pathlib import Path
    # TODO: Correct auxiliary path derivation after repository split.
    auxiliary_path = Path( __file__ ).parent.parent.parent.parent
    from os import environ as current_process_environment
    from types import MappingProxyType as DictionaryProxy
    configuration_ = DictionaryProxy( dict(
        auxiliary_path = auxiliary_path,
        project_path = Path( current_process_environment.get(
            '_DEVSHIM_PROJECT_PATH', auxiliary_path ) )
    ) )
    return configuration_

configuration = _configure( )


def _calculate_paths( ):
    paths_ = SimpleNamespace(
        # TODO: Drop '.local' from auxiliary path after repository split.
        auxiliary = configuration[ 'auxiliary_path' ] / '.local',
        project = configuration[ 'project_path' ] )
    paths_.local = paths_.project / '.local'
    paths_.artifacts = _calculate_artifacts_paths( paths_ )
    paths_.caches = _calculate_caches_paths( paths_ )
    paths_.configuration = _calculate_configuration_paths( paths_ )
    paths_.environments = paths_.local / 'environments'
    # TODO: Split SCM modules paths between auxiliary and project local.
    paths_.scm_modules = paths_.local / 'scm-modules'
    paths_.state = paths_.local / 'state'
    paths_.scripts = _calculate_scripts_paths( paths_ )
    paths_.sources = _calculate_sources_paths( paths_ )
    paths_.tests = _calculate_tests_paths( paths_ )
    return paths_


def _calculate_artifacts_paths( paths_ ):
    artifacts_path = paths_.local / 'artifacts'
    html_path = artifacts_path / 'html'
    return SimpleNamespace(
        SELF = artifacts_path,
        sdists = artifacts_path / 'sdists',
        sphinx_html = html_path / 'sphinx',
        sphinx_linkcheck = artifacts_path / 'sphinx-linkcheck',
        wheels = artifacts_path / 'wheels',
    )


def _calculate_caches_paths( paths_ ):
    caches_path = paths_.local / 'caches'
    packages_path = caches_path / 'packages'
    platforms_path = caches_path / 'platforms'
    utilities_path = caches_path / 'utilities'
    return SimpleNamespace(
        SELF = caches_path,
        hypothesis = caches_path / 'hypothesis',
        packages = SimpleNamespace(
            python3 = packages_path / 'python3',
        ),
        platforms = SimpleNamespace(
            python3 = platforms_path / 'python3',
        ),
        setuptools = caches_path / 'setuptools',
        sphinx = caches_path / 'sphinx',
        utilities = SimpleNamespace(
            python_build = utilities_path / 'python-build',
        ),
    )


def _calculate_configuration_paths( paths_ ):
    configuration_path = paths_.local / 'configuration'
    return SimpleNamespace(
        asdf = paths_.project / '.tool-versions',
        bumpversion = configuration_path / 'bumpversion.cfg',
        pre_commit = configuration_path / 'pre-commit.yaml',
        pypackages = configuration_path / 'pypackages.toml',
        pypackages_fixtures = configuration_path / 'pypackages.fixtures.toml',
        pyproject = paths_.project / 'pyproject.toml',
    )


def _calculate_scripts_paths( paths_ ):
    auxiliary_path = paths_.auxiliary / 'scripts'
    project_path = paths_.project / 'scripts'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = auxiliary_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = project_path / 'python3',
        ),
    )


def _calculate_sources_paths( paths_ ):
    auxiliary_path = paths_.auxiliary / 'sources'
    project_path = paths_.project / 'sources'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = auxiliary_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = project_path / 'python3',
            sphinx = project_path / 'sphinx',
        ),
    )


def _calculate_tests_paths( paths_ ):
    auxiliary_path = paths_.auxiliary / 'tests'
    project_path = paths_.project / 'tests'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = auxiliary_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = project_path / 'python3',
        ),
    )


paths = _calculate_paths( )


def identify_active_python( mode ):
    ''' Reports compatibility identifier for active Python. '''
    from devshim__python_identity import dispatch_table
    return dispatch_table[ mode ]( )


active_python_abi_label = identify_active_python( 'bdist-compatibility' )


def ensure_python_support_packages( ):
    ''' Ensures availability of support packages to active Python. '''
    # Ensure Tomli so that 'pyproject.toml' can be read.
    # TODO: Python 3.11: Remove this explicit dependency.
    _ensure_python_packages( ( 'tomli', ) )
    from tomli import load
    base_requirements = extract_python_package_requirements(
        indicate_python_packages( )[ 0 ], 'development.base' )
    with paths.configuration.pyproject.open( 'rb' ) as file:
        construction_requirements = (
            load( file )[ 'build-system' ][ 'requires' ] )
    _ensure_python_packages( frozenset(
        ( *base_requirements, *construction_requirements ) ) )


def extract_python_package_requirements( specifications, domain = None ):
    ''' Extracts Python packages requirements from specifications.

        If the ``domain`` argument is given, then only requirements from that
        domain are extracted. Otherwise, the requirements across all domains
        are extracted. '''
    # TODO: Raise error on unsupported format version.
    if 1 != specifications.get( 'format-version', 1 ): pass
    from itertools import chain
    valid_apex_domains = (
        'installation', 'optional-installation', 'development', )
    domains = ( domain, ) if domain else valid_apex_domains
    requirements = [ ]
    for domain_ in domains:
        if 'installation' == domain_:
            requirements.extend( map(
                _extract_python_package_requirement,
                specifications.get( domain, [ ] ) ) )
        else:
            apex_domain, *subdomains = domain_.split( '.' )
            # TODO: Raise error if apex domain is not a valid.
            apex_specifications = specifications.get( apex_domain, { } )
            if 0 == len( subdomains ):
                requirements.extend( map(
                    _extract_python_package_requirement,
                    chain.from_iterable( apex_specifications.values( ) ) ) )
            elif 1 == len( subdomains ):
                subdomain = subdomains[ 0 ]
                requirements.extend( map(
                    _extract_python_package_requirement,
                    apex_specifications.get( subdomain, [ ] ) ) )
            # TODO: Raise more appropriate error.
            else: raise RuntimeError( f"Invalid domain: {domain}" )
    return tuple( requirements )


def _extract_python_package_requirement( specification ):
    ''' Extracts Python package requirement from specification. '''
    if isinstance( specification, str ): return specification
    from collections.abc import Mapping as Dictionary
    if isinstance( specification, Dictionary ):
        # TODO: Validate that requirement entry exists.
        return specification[ 'requirement' ]
    # TODO: Raise error about invalid state if this is reached.
    raise RuntimeError


def _ensure_python_packages( requirements ):
    ''' Ensures availability of packages to active Python. '''
    from os import environ as cpe
    # Ignore if in an appropriate virtual environment.
    if active_python_abi_label == cpe.get( 'OUR_VENV_NAME' ): return
    # If 'pip' module is not available, then assume PEP 517 build in progress,
    # which should have already ensured packages from 'build-requires'.
    try: import pip # pylint: disable=unused-import
    except ImportError: return
    cache_path = ensure_directory(
        paths.caches.packages.python3 / active_python_abi_label )
    cache_path_ = str( cache_path )
    from sys import path as python_search_paths
    if cache_path_ not in python_search_paths:
        python_search_paths.insert( 0, cache_path_ )
    # Ignore packages which are already cached.
    in_cache_packages = frozenset(
        path.name for path in cache_path.glob( '*' )
        if path.suffix not in ( '.dist-info', ) )
    from re import match as regex_match
    def requirement_to_name( requirement ):
        return regex_match(
            r'^([\w\-]+)(.*)$', requirement ).group( 1 ).replace( '-', '_' )
    installable_requirements = tuple(
        requirement for requirement in requirements
        if requirement_to_name( requirement ) not in in_cache_packages )
    if installable_requirements:
        standard_execute_external(
            ( *split_command( 'pip install --upgrade --target' ),
              cache_path_, *installable_requirements ) )


def indicate_python_packages( identifier = None ):
    ''' Returns Python package dependencies.

        First return value is contents of packages specifications file.
        Second return value is list of dependency fixtures for the given
        platform identifier. Will be empty if none is given. '''
    from tomli import load
    fixtures_path = paths.configuration.pypackages_fixtures
    if identifier and fixtures_path.exists( ):
        with fixtures_path.open( 'rb' ) as file:
            fixtures = load( file ).get( identifier, [ ] )
    else: fixtures = [ ]
    with paths.configuration.pypackages.open( 'rb' ) as file:
        specifications = load( file )
    return specifications, fixtures


def ensure_directory( path ):
    ''' Ensures existence of directory, creating if necessary. '''
    path.mkdir( parents = True, exist_ok = True )
    return path


ensure_python_support_packages( )


def assert_sanity( ):
    ''' Assert that operational environment is sane. '''


def identify_python( mode, python_path ):
    ''' Reports compatibility identifier for Python at given path. '''
    detector_path = paths.scripts.d.python3 / 'identify-python.py'
    return standard_execute_external(
        ( python_path, detector_path, '--mode', mode ) ).stdout.strip( )


def discover_project_version( ):
    ''' Returns project version, as parsed from local configuration. '''
    return discover_project_information( )[ 'version' ]


def discover_project_information( ):
    ''' Discovers information about project from local configuration. '''
    from tomli import load
    with paths.configuration.pyproject.open( 'rb' ) as file:
        tables = load( file )
    information = tables[ 'project' ]
    information.update( tables[ 'tool' ][ 'setuptools' ] )
    information.update( tables[ 'tool' ][ 'SELF' ] )
    return information

project_name = discover_project_information( )[ 'name' ]
