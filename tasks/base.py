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
        sources = project_path / 'sources',
        state = local_path / 'state',
        tests = project_path / 'tests',
    )
    paths_.python3 = _calculate_python3_paths( paths_ )
    paths_.sphinx = _calculate_sphinx_paths( paths_ )
    return paths_


def _calculate_python3_paths( paths_ ):
    return SimpleNamespace(
        sources = paths_.sources / 'python3',
        tests = paths_.tests / 'python3',
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


def derive_python_venv_variables( venv_path, variables = None ):
    ''' Derives environment variables from Python virtual environment path. '''
    variables = variables or psenv.copy( )
    variables.pop( 'PYTHONHOME', None )
    variables[ 'PATH' ] = "{venv_path}/bin:{original_path}".format(
        venv_path = venv_path, original_path = variables[ 'PATH' ] )
    variables[ 'VIRTUAL_ENV' ] = str( venv_path )
    return variables
