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

''' Reports Python compatibility identifier.

    May be ABI compatibility identifier for binary distributions
    or PEP 508 environment identifier for package installation manifests. '''


import platform
import sys

from argparse import ArgumentParser


cpu_architecture = platform.machine( )
implementation_name = sys.implementation.name
system_type = platform.system( ).lower( )


def main( ):
    cli_parser = ArgumentParser( )
    cli_parser.add_argument( '--mode',
        default = 'bdist-compatibility', metavar = 'MODE',
        choices = ( 'bdist-compatibility', 'pep508-environment', )
    )
    cli_arguments = cli_parser.parse_args( )
    if 'bdist-compatibility' == cli_arguments.mode:
        report_bdist_compatibility_identifier( )
    elif 'pep508-environment' == cli_arguments.mode:
        report_pep508_environment_identifier( )


def report_bdist_compatibility_identifier( ):
    ''' Reports summary identifier for binary distribution compatibility. '''
    print( '--'.join( (
        calculate_python_abi_identifier( ),
        system_type,
        calculate_system_abi_identifier( ),
        cpu_architecture
    ) ) )


def calculate_python_abi_identifier( ):
    ''' Python implementation name, version, and extra ABI differentiators. '''
    return '-'.join( (
        implementation_name,
        format_version( sys.version_info, 2 ),
        *calculate_python_abi_extras( ) ) )


def calculate_python_abi_extras( ):
    ''' Special builds and variant implementation version. '''
    python_abi_extras = [ ]
    if 'cpython' == implementation_name:
        if hasattr( sys, 'getobjects' ):
            python_abi_extras.append( 'trace_refs' )
    elif 'pypy' == implementation_name:
        python_abi_extras.append(
            format_version( sys.pypy_version_info, 2 ) )
    elif 'pyston' == implementation_name:
        python_abi_extras.append(
            format_version( sys.pyston_version_info, 2 ) )
    return python_abi_extras


def calculate_system_abi_identifier( ):
    ''' System library linkage and virtual machine information. '''
    if system_type not in ( 'java', 'windows', ):
        return '-'.join( platform.libc_ver( ) )
    elif 'java' == system_type:
        # TODO: Implement.
        raise NotImplementedError
    elif 'windows' == system_type:
        # TODO: Implement.
        raise NotImplementedError


def report_pep508_environment_identifier( ):
    ''' Reports complete identifier for Python package constraints.

        Identifiers chosen in accordance with `PEP 508 environment markers
        <https://www.python.org/dev/peps/pep-0508/#environment-markers>`. '''
    print( '--'.join( (
        calculate_pep508_python_identifier( ), system_type, cpu_architecture
    ) ) )


def calculate_pep508_python_identifier( ):
    ''' Python implementation name and version and general version. '''
    return '-'.join( filter( None, (
        implementation_name,
        format_version( sys.version_info ),
        calculate_pep508_implementation_version( ) ) ) )


def calculate_pep508_implementation_version( ):
    ''' Variant implementation version. '''
    if 'pypy' == implementation_name:
        return format_version( sys.pypy_version_info )
    elif 'pyston' == implementation_name:
        return format_version( sys.pyston_version_info )


def format_version( info, specificity = 'full' ):
    ''' Formats standard named tuple for version into text. '''
    # Full specificity algorithm adapted from
    # https://www.python.org/dev/peps/pep-0508/#environment-markers
    if 'full' == specificity:
        version = '.'.join( map( str, info[ : 3 ] ) )
        release_level = info.releaselevel
        if 'final' != release_level:
            return "{version}{release_level}{serial}".format(
                version = version,
                release_level = release_level[ 0 ],
                serial = info.serial )
        return version
    return '.'.join( map( str, info[ : specificity ] ) )


if '__main__' == __name__: main( )
