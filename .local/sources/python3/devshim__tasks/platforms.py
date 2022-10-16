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


''' Management of development platforms. '''


from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):

    import re

    from os import (
        environ as active_process_environment,
        name as os_class,
    )
    from shlex import split as split_command
    from subprocess import CalledProcessError as ProcessInvocationError

    from .base import (
        pep508_identify_python,
        render_boxed_title,
    )
    from devshim__base import (
        paths,
        standard_execute_external,
    )

    from lockup import reclassify_module


def install_python_builder( ):
    ''' Install Python builder utility for platform, if one exists. '''
    if 'posix' == __.os_class: install_python_builder_posix( )


def install_python_builder_posix( ):
    ''' Installs 'python-build' utility. '''
    environment = __.active_process_environment.copy( )
    environment.update( dict(
        PREFIX = __.paths.caches.utilities.python_build,
    ) )
    __.standard_execute_external(
        str( __.paths.scm_modules.aux.joinpath(
            'pyenv', 'plugins', 'python-build', 'install.sh' ) ),
        env = environment )


def freshen_python( context, original_version ):
    ''' Updates supported Python minor version to latest patch.

        This task requires Internet access and may take some time. '''
    __.render_boxed_title(
        'Freshen: Python Version', supplement = original_version )
    minors_regex = __.re.compile(
        r'''^(?P<prefix>\w+(?:\d+\.\d+)?-)?(?P<minor>\d+\.\d+)\..*$''' )
    groups = minors_regex.match( original_version ).groupdict( )
    minor_version = "{prefix}{minor}".format(
        prefix = groups.get( 'prefix' ) or '',
        minor = groups[ 'minor' ] )
    successor_version = __.standard_execute_external(
        ( *__.split_command( 'asdf latest python' ), minor_version )
    ).stdout.strip( )
    try:
        original_identifier = __.pep508_identify_python(
            version = original_version )
    # Version may not be installed.
    except __.ProcessInvocationError: original_identifier = None
    context.run( f"asdf install python {successor_version}", pty = True )
    # Do not erase packages fixtures for extant versions.
    successor_identifier = __.pep508_identify_python(
        version = successor_version )
    if original_identifier == successor_identifier: original_identifier = None
    return { original_version: successor_version }, original_identifier


__.reclassify_module( __name__ )
