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


''' Shim layer for TOML configurations into Setuptools. '''


from devshim__base import (
    indicate_python_packages,
)


def generate_nominative_arguments( ):
    ''' Generates nominative arguments to 'setuptools.setup'. '''
    return dict(
        install_requires = generate_installation_requirements( ),
    )


def generate_installation_requirements( ):
    ''' Generates installation requirements from local configuration. '''
    simples, _ = indicate_python_packages( )
    return simples.get( 'installation', [ ] )