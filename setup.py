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


# Assert minimum Python version without using tool-specific machinery.
# Checking the Python version must be done in a backwards-compatible manner,
# so as to not trigger syntax exceptions in the checking logic.
# (Compatibility of this logic has been tested back to Python 2.6.)
required_version = 3, 7
error_message = 'Python {0}.{1} or higher required.'.format(
    required_version[ 0 ], required_version[ 1 ] )
from sys import version_info
from os import EX_UNAVAILABLE
version = version_info[ 0 ], version_info[ 1 ]
if required_version > version:
    print( error_message )
    raise SystemExit( EX_UNAVAILABLE )
del required_version, version, error_message, version_info


#from os import environ as psenv
#psenv[ 'DISTUTILS_DEBUG' ] = 'True'


def _setup_python_search_paths( ):
    from pathlib import Path
    from sys import path as python_search_paths
    project_path = Path( __file__ ).parent
    python_search_paths.insert(
        0, str( project_path / '.local' / 'sources' / 'python3' ) )
_setup_python_search_paths( )


# https://docs.python.org/3/distutils/setupscript.html#writing-the-setup-script
from setuptools import setup
from our_setuptools_shim import generate_nominative_arguments
setup( **generate_nominative_arguments( ) )
