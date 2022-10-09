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


from collections.abc import Mapping as AbstractDictionary
from functools import partial as partial_function
from itertools import chain
from os import environ as psenv
from pathlib import Path
from re import match as regex_match
from shlex import split as split_command
from subprocess import run
from sys import (
    path as python_search_paths,
)
from types import SimpleNamespace


def _calculate_paths( ):
    project_path = Path( __file__ ).parent.parent.parent.parent
    local_path = project_path / '.local'
    paths_ = SimpleNamespace( local = local_path, project = project_path )
    paths_.artifacts = _calculate_artifacts_paths( paths_ )
    paths_.caches = _calculate_caches_paths( paths_ )
    paths_.configuration = _calculate_configuration_paths( paths_ )
    paths_.environments = local_path / 'environments'
    paths_.scm_modules = local_path / 'scm-modules'
    paths_.state = local_path / 'state'
    paths_.common = paths_.scm_modules / 'emcd-common'
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
        # Note: 'setuptools' hardcodes the eggs path.
        eggs = paths_.project / 'eggs',
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
    d_scripts_path = paths_.local / 'scripts'
    p_scripts_path = paths_.project / 'scripts'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = d_scripts_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = p_scripts_path / 'python3',
        ),
    )


def _calculate_sources_paths( paths_ ):
    d_sources_path = paths_.local / 'sources'
    p_sources_path = paths_.project / 'sources'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = d_sources_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = p_sources_path / 'python3',
            sphinx = p_sources_path / 'sphinx',
        ),
    )


def _calculate_tests_paths( paths_ ):
    d_tests_path = paths_.local / 'tests'
    p_tests_path = paths_.project / 'tests'
    return SimpleNamespace(
        d = SimpleNamespace(
            python3 = d_tests_path / 'python3',
        ),
        p = SimpleNamespace(
            python3 = p_tests_path / 'python3',
        ),
    )


paths = _calculate_paths( )


def identify_active_python( mode ):
    ''' Reports compatibility identifier for active Python. '''
    from devshim__python_identity import dispatch_table
    return dispatch_table[ mode ]( )


active_python_abi_label = identify_active_python( 'bdist-compatibility' )


standard_execute_external = partial_function(
    run, check = True, capture_output = True, text = True )


def ensure_python_support_packages( ):
    ''' Ensures availability of support packages to active Python. '''
    # Ensure Tomli so that 'pyproject.toml' can be read.
    # TODO: Remove this explicit dependency once Python 3.11 is baseline.
    _ensure_python_packages( ( 'tomli', ) )
    from tomli import load
    base_requirements = (
        indicate_python_packages( )[ 0 ][ 'development' ].get( 'base', [ ] ) )
    with paths.configuration.pyproject.open( 'rb' ) as file:
        construction_requirements = (
            load( file )[ 'build-system' ][ 'requires' ] )
    _ensure_python_packages( frozenset(
        ( *base_requirements, *construction_requirements ) ) )

def _ensure_python_packages( requirements ):
    ''' Ensures availability of packages to active Python. '''
    # Ignore if in an appropriate virtual environment.
    if active_python_abi_label == psenv.get( 'OUR_VENV_NAME' ): return
    # If 'pip' module is not available, then assume PEP 517 build in progress,
    # which should have already ensured packages from 'build-requires'.
    try: import pip # pylint: disable=unused-import
    except ImportError: return
    cache_path = ensure_directory(
        paths.caches.packages.python3 / active_python_abi_label )
    cache_path_ = str( cache_path )
    if cache_path_ not in python_search_paths:
        python_search_paths.insert( 0, cache_path_ )
    # Ignore packages which are already cached.
    in_cache_packages = frozenset(
        path.name for path in cache_path.glob( '*' )
        if path.suffix not in ( '.dist-info', ) )
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
    ''' Returns lists of Python package dependencies.

        First is raw list of dependencies.
        Second is list of dependency fixtures (fixed on digest). '''
    from tomli import load
    fixtures_path = paths.configuration.pypackages_fixtures
    if identifier and fixtures_path.exists( ):
        with fixtures_path.open( 'rb' ) as file:
            fixtures = load( file ).get( identifier, [ ] )
    else: fixtures = [ ]
    with paths.configuration.pypackages.open( 'rb' ) as file:
        simples = load( file )
    return simples, fixtures


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


def collapse_multilevel_dictionary( dictionary ):
    ''' Collapses a hierarchical dictionary into a list. '''
    # TODO: Need to handle format version number.
    #       Probably replace this function with something more specific.
    return tuple( chain.from_iterable(
        (   collapse_multilevel_dictionary( value )
            if isinstance( value, AbstractDictionary ) else value )
        for value in dictionary.values( ) ) )


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
