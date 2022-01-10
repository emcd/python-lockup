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


from pathlib import Path
from shlex import split as split_command
from subprocess import run
from sys import path as python_search_paths
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
    return SimpleNamespace(
        SELF = caches_path,
        # Note: 'setuptools' hardcodes the eggs path.
        eggs = paths_.project / 'eggs',
        hypothesis = caches_path / 'hypothesis',
        packages = SimpleNamespace(
            python3 = packages_path / 'python3',
        ),
        sphinx = caches_path / 'sphinx',
    )


def _calculate_configuration_paths( paths_ ):
    configuration_path = paths_.local / 'configuration'
    return SimpleNamespace(
        asdf = paths_.project / '.tool-versions',
        bumpversion = configuration_path / 'bumpversion.cfg',
        mypy = configuration_path / 'mypy.ini',
        pre_commit = configuration_path / 'pre-commit.yaml',
        pypackages = configuration_path / 'pypackages.toml',
        pyproject = paths_.project / 'pyproject.toml',
        # TODO: Remove setuptools configuration once migration is finished.
        setuptools = paths_.project / 'setup.cfg',
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


def ensure_directory( path ):
    ''' Ensures existence of directory, creating if necessary. '''
    path.mkdir( parents = True, exist_ok = True )
    return path


def ensure_python_package( package_name ):
    ''' Ensures local availability of Python package. '''
    cache_path = ensure_directory( paths.caches.packages.python3 )
    if cache_path not in python_search_paths:
        python_search_paths.insert( 0, cache_path )
    run(
        ( *split_command( 'pip install --upgrade --target' ),
          cache_path, package_name ),
        check = True, capture_output = True )
    # TODO: Verify package installation and return path to it.
