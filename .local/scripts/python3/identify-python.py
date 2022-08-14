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

''' Reports Python compatibility identifier. '''


def main( ):
    _setup_python_search_paths( )
    from argparse import ArgumentParser
    from devshim__python_identity import dispatch_table
    cli_parser = ArgumentParser( )
    cli_parser.add_argument( '--mode',
        default = 'bdist-compatibility', metavar = 'MODE',
        choices = dispatch_table.keys( )
    )
    cli_arguments = cli_parser.parse_args( )
    print( dispatch_table[ cli_arguments.mode ]( ) )


def _setup_python_search_paths( ):
    from pathlib import Path
    from sys import path as python_search_paths
    common_path = Path( __file__ ).parent.parent.parent
    python_search_paths.insert( 0, str( common_path / 'sources' / 'python3' ) )


if '__main__' == __name__: main( )
