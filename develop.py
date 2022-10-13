# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
#                                                                             #
###############################################################################


''' Entrypoint for development activity.

    Bootstraps basic development environment as necessary. '''


def assert_minimum_python_version( ):
    ''' Asserts minimum Python version in a version-agnostic manner.

        Checking the Python version must be done in a backwards-compatible
        manner, so as to not trigger syntax exceptions in the checking logic.
        (Compatibility of this logic has been tested back to Python 2.6.) '''
    required_version = 3, 7
    error_message = '\nERROR: Python {0}.{1} or higher required.\n'.format(
        required_version[ 0 ], required_version[ 1 ] )
    from sys import stderr, version_info
    version = version_info[ 0 ], version_info[ 1 ]
    if required_version > version:
        stderr.write( error_message ); stderr.flush( )
        raise SystemExit( 69 ) # EX_UNAVAILABLE

assert_minimum_python_version( )


# TODO: Ensure that Git submodules are cloned.


def setup_python_search_paths( ):
    ''' Allows Python to locate modules for development support. '''
    from base64 import standard_b64encode as b64encode
    from os import environ as cpe
    from pathlib import Path
    from pickle import dumps as pickle
    from sys import path as python_search_paths
    project_path = Path( __file__ ).parent
    # TODO: Switch to SCM modules path after refactor.
    python_search_paths.insert(
        0, str( project_path / '.local' / 'sources' / 'python3' ) )
    cpe[ '_DEVSHIM_CONFIGURATION' ] = b64encode( pickle( dict(
        project_path = project_path,
    ) ) ).decode( )

setup_python_search_paths( )


from devshim__base import assert_sanity as _assert_sanity
_assert_sanity( )


def main( ):
    ''' Entrypoint for development activity. '''
    from invoke import Collection, Program
    import devshim__tasks
    program = Program( namespace = Collection.from_module( devshim__tasks ) )
    program.run( )


from lockup import reclassify_module as _reclassify_module
_reclassify_module( __name__ )


if '__main__' == __name__: main( )
