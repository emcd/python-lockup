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
#   _base -> _exceptionality -> exceptions -> class_factories -> _base
# pylint: disable=cyclic-import


from .interception import (
    create_interception_decorator as _create_interception_decorator,
)


def provide_exception_controller( ):
    ''' Late-imports and returns exception controller. '''
    from ._exceptionality import exception_controller
    return exception_controller

intercept = _create_interception_decorator( provide_exception_controller )


package_name = __package__.split( '.', maxsplit = 1 )[ 0 ]
