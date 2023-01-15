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


def _prepare( ):
    if False: # pylint: disable=using-constant-test
        from os import environ as current_process_environment
        current_process_environment[ 'DISTUTILS_DEBUG' ] = 'True'
    from pathlib import Path
    project_location = Path( __file__ ).parent
    from importlib.util import module_from_spec, spec_from_file_location
    module_spec = spec_from_file_location(
        '_develop', project_location / 'develop.py' )
    module = module_from_spec( module_spec )
    module_spec.loader.exec_module( module )
    module.prepare( project_location )
    # Only want our main cache on the modules search path long enough to ensure
    # successful import of our own sources to assist in build preparation. Do
    # not want to see build helper or its dependencies during actual build of
    # package or anytime afterwards (such as virtual environment construction)
    # as this can lead to conflicts.
    with module.imports_from_cache(
        module.ensure_packages_cache( 'main' )
    ):
        from devshim.data import paths # pylint: disable=import-error
    return paths

_paths = _prepare( )


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
        self.build_base = str( _paths.caches.setuptools )


from setuptools.command.egg_info import egg_info as _EggInfoCommand
class EggInfoCommand( _EggInfoCommand ):
    ''' With overridden 'egg_base' attribute. '''
    # https://github.com/pypa/setuptools/issues/1347#issuecomment-707979218
    # https://github.com/pypa/setuptools/milestone/3

    def initialize_options( self ):
        ''' Override 'egg_base' attribute. '''
        _EggInfoCommand.initialize_options( self )
        self.egg_base = str( _paths.caches.setuptools ) # pylint: disable=attribute-defined-outside-init


from setuptools.command.sdist import sdist as _SdistCommand
class SdistCommand( _SdistCommand ): # pylint: disable=too-many-ancestors
    ''' With overridden 'dist_dir' attribute. '''

    def initialize_options( self ):
        ''' Override 'dist_dir' attribute. '''
        _SdistCommand.initialize_options( self )
        self.dist_dir = str( _paths.artifacts.sdists )


from wheel.bdist_wheel import bdist_wheel as _BdistWheelCommand
class BdistWheelCommand( _BdistWheelCommand ):
    ''' With overridden 'dist_dir' attribute. '''

    def initialize_options( self ):
        ''' Override 'dist_dir' attribute. '''
        _BdistWheelCommand.initialize_options( self )
        self.dist_dir = str( _paths.artifacts.wheels ) # pylint: disable=attribute-defined-outside-init


# https://docs.python.org/3/distutils/setupscript.html#writing-the-setup-script
from setuptools import setup
setup(
    cmdclass = {
        'bdist_wheel': BdistWheelCommand,
        'build': BuildCommand,
        'egg_info': EggInfoCommand,
        'sdist': SdistCommand,
    },
)
