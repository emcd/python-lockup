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
#   base -> interception
# Latent Dependencies:
#   base -> exceptions -> factories -> base


from .interception import (
    create_interception_decorator as _create_interception_decorator,
)


def provide_exception( name ):
    ''' Lazily imports exceptions to prevent dependency cycles. '''
    from . import exceptions
    return getattr( exceptions, name )

intercept = _create_interception_decorator( provide_exception )

package_name = __package__.split( '.', maxsplit = 1 )[ 0 ]
