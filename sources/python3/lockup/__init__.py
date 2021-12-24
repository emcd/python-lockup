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


''' Immutable module class and namespace factory. '''


# https://www.python.org/dev/peps/pep-0396/
__version__ = '1.1rc1'


from . import exceptions
from .base import Class, NamespaceClass, create_namespace


class __( metaclass = NamespaceClass ):

    from inspect import ismodule as is_module
    from sys import modules
    from types import ModuleType as Module # type: ignore

    from .base import (
        InaccessibleAttribute,
        base_package_name,
        create_argument_validation_exception,
        create_attribute_immutability_exception,
        create_attribute_indelibility_exception,
        create_attribute_nonexistence_exception,
        intercept,
        is_operational_name, select_public_attributes,
        validate_attribute_existence,
        validate_attribute_name, )


class Module( __.Module, metaclass = Class ):
    ''' Module whose attributes are immutable except during module definition.

        Can replace the ``__class__`` attribute on an existing module.

        Non-public attributes of the module are concealed from :py:func:`dir`.
        Also, a copy of the module dictionary is returned when the ``__dict__``
        attribute is accessed; this is done to remove a backdoor by which
        attributes could be mutated.

        .. note::
           Copies of the module dictionary are mutable so as to not violate the
           internal expectations of Python as well as important packages,
           such as :py:mod:`doctest`. Ideally, these would be immutable,
           but cannot be as of this writing. '''

    @__.intercept
    def __getattribute__( self, name ):
        if '__dict__' == name: return dict( super( ).__getattribute__( name ) )
        try: return super( ).__getattribute__( name )
        except AttributeError as exc:
            raise __.create_attribute_nonexistence_exception(
                name, self ) from exc

    @__.intercept
    def __setattr__( self, name, value ):
        __.validate_attribute_name( name, self )
        raise __.create_attribute_immutability_exception( name, self )

    @__.intercept
    def __delattr__( self, name ):
        __.validate_attribute_name( name, self )
        __.validate_attribute_existence( name, self )
        raise __.create_attribute_indelibility_exception( name, self )

    @__.intercept
    def __dir__( self ): return __.select_public_attributes( __class__, self )


def reclassify_module( module ):
    ''' Assigns :py:class:`Module` as class for module.

        Takes either a module object or the name of a module
        in :py:data:`sys.modules`. If the module has already been reclassified,
        then nothing is done (i.e., the operation is idempotent). '''
    module_validity_error = __.create_argument_validation_exception(
        'module', reclassify_module,
        'module or name of module in Python loaded modules dictionary' )
    if isinstance( module, Module ): return
    if __.is_module( module ): pass
    elif isinstance( module, str ):
        module = __.modules.get( module )
        if None is module: raise module_validity_error
    else: raise module_validity_error
    module.__class__ = Module


reclassify_module( base ) # type: ignore # pylint: disable=undefined-variable
reclassify_module( exceptions )
reclassify_module( __name__ )
