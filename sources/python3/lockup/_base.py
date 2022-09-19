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


''' Package foundation. Internal constants and functions. '''


# Initialization Dependencies:
#   _base -> interception
# Latent Dependencies:
#   _base -> exceptionality -> exceptions -> class_factories -> _base
# pylint: disable=cyclic-import


from .interception import (
    create_interception_decorator as _create_interception_decorator,
)


# TODO: Reflect metaclass to Class.
class LatentExceptionController:
    ''' Presents uniform interface for exception control.

        Performs on-demand imports of our internal exception control
        functions. '''

    @staticmethod
    def apprehend_fugitive( exception, invocation ):
        ''' Apprehends fugitive exceptions at API boundary. '''
        from .exceptionality import our_fugitive_apprehender
        return our_fugitive_apprehender( exception, invocation )

    @staticmethod
    def provide_factory( name ):
        ''' Returns exception factory by name. '''
        from .exceptionality import our_exception_factory_provider
        return our_exception_factory_provider( name )

    def __setattr__( self, name, value ):
        from .validators import validate_attribute_name
        validate_attribute_name( self, name )
        raise self.provide_factory( 'attribute_immutability' )( name, self )

    def __delattr__( self, name ):
        from .validators import (
            validate_attribute_name,
            validate_attribute_existence,
        )
        validate_attribute_name( self, name )
        validate_attribute_existence( self, name, self )
        raise self.provide_factory( 'attribute_indelibility' )( name, self )


exception_controller = LatentExceptionController( )
intercept = _create_interception_decorator( exception_controller )
package_name = __package__.split( '.', maxsplit = 1 )[ 0 ]
