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


''' Concealment and immutability of module attributes.

    .. code-block:: python

      >>> import math
      >>> math.pi = math.e
      >>> f"Oh no! π is {math.pi}"
      'Oh no! π is 2.718281828459045'
      >>> math.pi = 4 * math.atan( 1 )
      >>> import lockup
      >>> lockup.reclassify_module( math )
      >>> math.pi = math.e
      Traceback (most recent call last):
      ...
      lockup.exceptions.ImpermissibleAttributeOperation: Attempt to assign immutable attribute 'pi' on module 'math'.
      >>> math.pi
      3.141592653589793
    ''' # pylint: disable=line-too-long


# Initialization Dependencies:
#   module -> _base
#   module -> exceptions
#   module -> factories
#   module -> validators
#   module -> visibility
# Latent Dependencies: (no cycles)


from .factories import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from types import ModuleType as Module # type: ignore

    from . import _base as base
    from ._base import intercept
    from .exceptions import (
        create_attribute_immutability_exception,
        create_attribute_indelibility_exception,
        create_attribute_nonexistence_exception,
    )
    from .factories import Class
    from .validators import (
        validate_attribute_existence,
        validate_attribute_name,
    )
    from .visibility import select_public_attributes


class Module( __.Module, metaclass = __.Class ):
    ''' Module whose attributes are immutable except during module definition.

        Can replace the ``__class__`` attribute on an existing module.

        A copy of the module dictionary is returned when the ``__dict__``
        attribute is accessed; this is done to remove a backdoor by which
        attributes could be mutated.

        .. note::
           Copies of the module dictionary are mutable so as to not violate the
           internal expectations of Python as well as important packages,
           such as :py:mod:`doctest`. Ideally, these would be immutable,
           but cannot be as of this writing. '''

    # Note: Cannot wrap the '__getattribute__' method with an interceptor
    #       because the import machinery may throw 'AttributeError' as a normal
    #       part of operation and the 'exceptions' module in this package will
    #       be imported to check the exception class, which will lead to
    #       infinite recursion, as its class is our 'Module' class after being
    #       reclassified. Also, there is a performance hit with wrapping this
    #       particular method, because it is on the hot path for module
    #       attribute access. And, it is mostly proof against exception leaks.
    def __getattribute__( self, name ):
        if '__dict__' == name: return dict( super( ).__getattribute__( name ) )
        try: return super( ).__getattribute__( name )
        except AttributeError as exc:
            raise __.create_attribute_nonexistence_exception(
                name, self ) from exc

    @__.intercept # type: ignore
    def __setattr__( self, name, value ):
        __.validate_attribute_name( name, self )
        raise __.create_attribute_immutability_exception( name, self )

    @__.intercept # type: ignore
    def __delattr__( self, name ):
        __.validate_attribute_name( name, self )
        __.validate_attribute_existence( name, self )
        raise __.create_attribute_indelibility_exception( name, self )

    @__.intercept # type: ignore
    def __dir__( self ): return __.select_public_attributes( __class__, self )


def reclassify_module( module ):
    ''' Assigns :py:class:`Module` as class for module.

        Takes either a module object or the name of a module
        in :py:data:`sys.modules`. If the module has already been reclassified,
        then nothing is done (i.e., the operation is idempotent). '''
    if isinstance( module, Module ): return
    if isinstance( module, str ):
        from sys import modules
        module = modules.get( module )
    from inspect import ismodule as is_module
    if None is module or not is_module( module ):
        from .exceptions import create_argument_validation_exception
        raise create_argument_validation_exception(
            'module', reclassify_module,
            'module or name of module in Python loaded modules dictionary' )
    module.__class__ = Module


reclassify_module( __.base )
