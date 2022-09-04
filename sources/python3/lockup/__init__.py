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


''' Supports attribute concealment and immutability. '''


# https://www.python.org/dev/peps/pep-0396/
__version__ = '2.0a202209040105'


from . import (
    exceptions, factories, interception, module, reflection, validators,
)
from .factories import Class, NamespaceClass, create_namespace
from .interception import create_interception_decorator
from .module import Module, reclassify_module


# If Python implementation does not support class reflection,
# we can still provide functionality without the extra protection.
reflection.reflect_class_factory_per_se( Class, assert_implementation = False )


reclassify_module( exceptions )
reclassify_module( factories )
reclassify_module( interception )
reclassify_module( module )
reclassify_module( reflection )
reclassify_module( validators )
reclassify_module( __name__ )
