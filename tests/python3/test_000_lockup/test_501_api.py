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


''' Ensure elements of package API. '''


from pytest import mark

from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    import lockup


def test_101_ensure_public_attributes( ):
    ''' Only expected public attributes are presented. '''
    expected_attributes = (
        'Class',
        'ExceptionController',
        'Module',
        'NamespaceClass',
        'class_factories',
        'create_interception_decorator',
        'create_namespace',
        'exception_factories',
        'exceptionality',
        'exceptions',
        'interception',
        'module',
        'nomenclature',
        'reclassify_module',
        'reflection',
        'validators',
        'visibility',
    )
    assert expected_attributes == tuple( dir( __.lockup ) )


@mark.parametrize(
    'module_name',
    (
        'class_factories',
        'exception_factories',
        'exceptionality',
        'exceptions',
        'interception',
        'module',
        'nomenclature',
        'reflection',
        'validators',
        'visibility',
    )
)
def test_111_validate_public_module_classification( module_name ):
    ''' Public modules are of the proper class. '''
    assert isinstance(
        getattr( __.lockup, module_name ),
        __.lockup.Module )
