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


''' Test Fixtures: Invocable Objects '''


from lockup import NamespaceClass as _NamespaceClass
class __( metaclass = _NamespaceClass ):
    ''' Internal namespace. '''

    from functools import wraps


def _decorator( invocable ):
    ''' Decorator used for testing wrapped functions. '''
    @__.wraps( invocable )
    def envelop_execution( *posargs, **nomargs ):
        ''' Completely transparent function wrapper. '''
        return invocable( *posargs, **nomargs )
    return envelop_execution

class InvocableObject:
    ''' Produces invocable instances. '''

    def __call__( self ): return self

    def a_method( self ):
        ''' For testing bound methods on an instance. '''
        return self

    @_decorator
    def decorated_method( self ):
        ''' For testing decorated bound methods of an instance. '''
        return self

    class Inner:
        ''' Nested class for '__qualname__' testing. '''

        def generator( self ):
            ''' For testing generator methods. '''
            yield self

        async def agenerator( self ):
            ''' For testing async generator methods. '''
            yield self

        async def coroutine( self ):
            ''' For testing async methods. '''
            return self
