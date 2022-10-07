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


''' Ensure correctness of package exceptions. '''


from pytest import mark

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from lockup import exceptions


@mark.parametrize(
    'exception_class, ancestor_class',
    (
        ( __.exceptions.Exception0, BaseException ),
        ( __.exceptions.InvalidOperation, __.exceptions.Exception0 ),
        ( __.exceptions.InvalidOperation, Exception ),
        ( __.exceptions.AbsentImplementation, __.exceptions.Exception0 ),
        ( __.exceptions.AbsentImplementation, NotImplementedError ),
        ( __.exceptions.ImpermissibleOperation,
          __.exceptions.InvalidOperation ),
        ( __.exceptions.ImpermissibleOperation, TypeError ),
        ( __.exceptions.ImpermissibleAttributeOperation,
          __.exceptions.ImpermissibleOperation ),
        ( __.exceptions.ImpermissibleAttributeOperation, AttributeError ),
        ( __.exceptions.InaccessibleAttribute,
          __.exceptions.InvalidOperation ),
        ( __.exceptions.InaccessibleAttribute, AttributeError ),
        ( __.exceptions.IncorrectData, __.exceptions.InvalidOperation ),
        ( __.exceptions.IncorrectData, TypeError ),
        ( __.exceptions.IncorrectData, ValueError ),
        ( __.exceptions.InvalidState, __.exceptions.Exception0 ),
        ( __.exceptions.InvalidState, RuntimeError ),
        ( __.exceptions.FugitiveException, __.exceptions.InvalidState ),
    )
)
def test_011_ancestry( exception_class, ancestor_class ):
    ''' Exception class is subclass of ancestor class. '''
    assert issubclass( exception_class, ancestor_class )


# TODO: Validate exception labels functionality.
