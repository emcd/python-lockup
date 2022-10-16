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


''' Setuptools configuration and support. '''


def _configure( ):
    from pathlib import Path
    project_path = Path( __file__ ).parent
    from importlib.util import module_from_spec, spec_from_file_location
    module_spec = spec_from_file_location(
        '_develop', project_path / 'develop.py' )
    module = module_from_spec( module_spec )
    module_spec.loader.exec_module( module )
    module.configure_auxiliary( project_path )
    if False: # pylint: disable=using-constant-test
        from os import environ as current_process_environment
        current_process_environment[ 'DISTUTILS_DEBUG' ] = 'True'

_configure( )


# Overridden Setuptools Command Attributes
#   https://stackoverflow.com/a/66163350/14833542
#   Want to write to proper locations regardless of how Setuptools is invoked.


from setuptools.command.build import build as _BuildCommand
class BuildCommand( _BuildCommand ): # pylint: disable=too-many-ancestors
    ''' With overridden 'build_base' attribute. '''
    # https://github.com/pypa/wheel/issues/306#issuecomment-522529825

    def initialize_options( self ):
        ''' Override 'build_base' attribute. '''
        _BuildCommand.initialize_options( self )
        from devshim__base import paths
        self.build_base = str( paths.caches.setuptools )


from setuptools.command.egg_info import egg_info as _EggInfoCommand
class EggInfoCommand( _EggInfoCommand ):
    ''' With overridden 'egg_base' attribute. '''
    # https://github.com/pypa/setuptools/issues/1347#issuecomment-707979218
    # https://github.com/pypa/setuptools/milestone/3

    def initialize_options( self ):
        ''' Override 'egg_base' attribute. '''
        _EggInfoCommand.initialize_options( self )
        from devshim__base import paths
        self.egg_base = str( paths.caches.setuptools ) # pylint: disable=attribute-defined-outside-init


from setuptools.command.sdist import sdist as _SdistCommand
class SdistCommand( _SdistCommand ): # pylint: disable=too-many-ancestors
    ''' With overridden 'dist_dir' attribute. '''

    def initialize_options( self ):
        ''' Override 'dist_dir' attribute. '''
        _SdistCommand.initialize_options( self )
        from devshim__base import paths
        self.dist_dir = str( paths.artifacts.sdists )


from wheel.bdist_wheel import bdist_wheel as _BdistWheelCommand
class BdistWheelCommand( _BdistWheelCommand ):
    ''' With overridden 'dist_dir' attribute. '''

    def initialize_options( self ):
        ''' Override 'dist_dir' attribute. '''
        _BdistWheelCommand.initialize_options( self )
        from devshim__base import paths
        self.dist_dir = str( paths.artifacts.wheels )


def _generate_nominative_arguments( ):
    ''' Generates nominative arguments to 'setuptools.setup'. '''
    return dict(
        install_requires = _generate_installation_requirements( ),
    )


def _generate_installation_requirements( ):
    ''' Generates installation requirements from local configuration. '''
    from devshim__base import (
        extract_python_package_requirements,
        indicate_python_packages,
    )
    return extract_python_package_requirements(
        indicate_python_packages( )[ 0 ], 'installation' )


# https://docs.python.org/3/distutils/setupscript.html#writing-the-setup-script
from setuptools import setup
setup(
    cmdclass = {
        'bdist_wheel': BdistWheelCommand,
        'build': BuildCommand,
        'egg_info': EggInfoCommand,
        'sdist': SdistCommand,
    },
    **_generate_nominative_arguments( )
)
