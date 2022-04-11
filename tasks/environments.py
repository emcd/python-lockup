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

''' Management of virtual environments. '''


class __:

    from .base import (
        derive_venv_context_options,
        derive_venv_path,
        detect_vmgr_python_path,
        pep508_identify_python,
        render_boxed_title,
    )
    from .packages import (
        calculate_python_packages_fixtures,
        install_python_packages,
        record_python_packages_fixtures,
    )
    from our_base import (
        ensure_directory,
    )


def build_python_venv( context, version, overwrite = False ):
    ''' Creates virtual environment for requested Python version. '''
    __.render_boxed_title( f"Build: Python Virtual Environment ({version})" )
    python_path = __.detect_vmgr_python_path( version )
    venv_path = __.ensure_directory( __.derive_venv_path(
        version, python_path ) )
    venv_options = [ ]
    if overwrite: venv_options.append( '--clear' )
    venv_options_str = ' '.join( venv_options )
    context.run(
        f"{python_path} -m venv {venv_options_str} {venv_path}", pty = True )
    context_options = __.derive_venv_context_options( venv_path )
    __.install_python_packages( context, context_options )
    fixtures = __.calculate_python_packages_fixtures(
        context_options[ 'env' ] )
    identifier = __.pep508_identify_python( version = version )
    __.record_python_packages_fixtures( identifier, fixtures )
