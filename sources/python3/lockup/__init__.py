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
__version__ = '0.1.0a202011180739'


from . import exceptions
from .base import NamespaceFactory, PrimalClassFactory


class __( metaclass = NamespaceFactory ):

    from inspect import ismodule as is_module
    from sys import modules
    from types import ModuleType as Module

    from .base import (
        InaccessibleAttribute,
        base_package_name,
        create_argument_validation_exception,
        create_attribute_concealment_exception,
        create_attribute_immutability_exception,
        create_attribute_indelibility_exception,
        create_attribute_nonexistence_exception,
        intercept,
        is_operational_name, select_public_attributes,
        validate_attribute_existence,
        validate_attribute_name, )


class Module( __.Module, metaclass = PrimalClassFactory ):
    ''' Module whose attributes cannot be mutated outside of its definition.

        Also:

        * Conceals private attributes from :py:func:`dir`.
        * Denies direct access to private attributes
          outside of its definition. '''

    @__.intercept
    def __getattribute__( self, name ):
        # Note: Ideally, we would return a 'DictionaryProxy' here,
        #       but that breaks various expectations for a true 'dict'.
        if '__dict__' == name: return dict( super( ).__getattribute__( name ) )
        # Short-circuit lookup for auxiliary functions we want to use here.
        if '__' == name: return super( ).__getattribute__( name )
        try:
            # Operational attributes are fine.
            if __.is_operational_name( name ):
                return super( ).__getattribute__( name )
            # Concealed attributes should be... concealed.
            if name.startswith( '_' ):
                raise __.create_attribute_concealment_exception( name, self )
            return super( ).__getattribute__( name )
        # Explicitly forward 'InaccessibleAttribute'
        # to prevent infinite recursion on 'AttributeError'.
        except __.InaccessibleAttribute: raise
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


reclassify_module( base )   # pylint: disable=undefined-variable
reclassify_module( exceptions )
reclassify_module( __name__ )
