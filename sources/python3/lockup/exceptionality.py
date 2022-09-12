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


''' Facilities for exception production and control. '''


# Exception Controller
#   pass to:
#       interceptor factory
#       validators

# Interceptor factory and validators can take nullary function
# which returns exception controller for cases where deferred importation /
# latent evaluation is required.


from .class_factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from .class_factories import Class


class ExceptionController( metaclass = __.Class ):
    ''' Presents uniform interface for exception control. '''

    def __init__( self, factory_provider, fugitive_apprehender ):
        # TODO: Validate arguments.
        self.provide_factory = factory_provider
        self.apprehend_fugitive = fugitive_apprehender

    # TODO: Protect against attribute mutation and deletion
    #       after initialization.
