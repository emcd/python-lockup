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


''' Shim layer for TOML configurations into setuptools. '''

# https://docs.python.org/3/distutils/setupscript.html#writing-the-setup-script
# https://setuptools.pypa.io/en/latest/userguide/declarative_config.html
# https://setuptools.readthedocs.io/en/latest/references/keywords.html


from collections.abc import (
    Sequence as AbstractSequence,
)
from pathlib import Path
from types import MappingProxyType as DictionaryProxy

from setuptools import find_packages

from our_base import (
    collapse_multilevel_dictionary,
    discover_project_information,
    indicate_python_packages,
    paths,
)


def concatenate_with_spaces( data ):
    ''' Concatenates list elements into space-separated string. '''
    assert not isinstance( data, str ) and isinstance( data, AbstractSequence )
    return ( ' '.join( data ), )


def extract_license( license_info ):
    ''' Extracts license information as separate string arguments. '''
    return license_info.get( 'text' ), license_info.get( 'file' )


def transform_contributor( contributor ):
    ''' Transforms contributor specification into name and email address. '''
    # Note: Python Core Metadata and PEP 621 are at odds on author and
    #       maintainer. We choose Python Core Metadata, which matches
    #       Setuptools.
    # https://www.python.org/dev/peps/pep-0621/#authors-maintainers
    # https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/#author
    # https://packaging.python.org/en/latest/specifications/core-metadata/#author
    # https://packaging.python.org/en/latest/specifications/core-metadata/#author-email
    # https://packaging.python.org/en/latest/specifications/core-metadata/#maintainer
    # https://packaging.python.org/en/latest/specifications/core-metadata/#maintainer-email
    return contributor.get( 'name' ), contributor.get( 'email' )


def transform_long_description( description ):
    ''' Transforms long description to be suitable for 'setuptools.setup'. '''
    # Note: PEP 621 'readme' is deficient in functionality, compared to
    #       Setuptools 'long_description' "file:" semantics, which allows
    #       multiple files to be concatenated into a single long description.
    #       We choose an implementation that matches Setuptools.
    # https://www.python.org/dev/peps/pep-0621/#readme
    # https://github.com/pypa/setuptools/blob/c65e3380b0a18c92a0fc2d2b770b17cfaaec054b/setuptools/config.py#L340-L368
    if isinstance( description, str ): return description, None
    if not description: return None, None
    content_type = description.get( 'content-type' )
    if not content_type:
        content_type = mime_types.get(
            Path( next( iter( description[ 'files' ] ) ) ).suffix.lower( ),
            'text/plain' )
    manifest = '\n\n'.join(
        Path( path ).open( encoding = 'utf-8' ).read( )
        for path in description[ 'files' ] )
    return manifest, content_type


mime_types = DictionaryProxy( {
    'md':   'text/markdown',
    'rst':  'text/x-rst',
} )


# https://packaging.python.org/guides/distributing-packages-using-setuptools/#setup-args
# https://github.com/pypa/setuptools/blob/00fbad0f93ffdba0a4d5c3f2012fd7c3de9af04d/setuptools/dist.py#L163-L221
# Some inspiration taken from PyProject Setuptools:
#   https://github.com/TheCleric/ppsetuptools/blob/main/ppsetuptools/ppsetuptools.py
_converters = {
    'author':          (
        ( 'author', 'author_email', ),
        transform_contributor
    ),
    'classifiers':      ( ( 'classifiers', ), None ),
    'description':      ( ( 'description', ), None ),
    # https://packaging.python.org/en/latest/specifications/core-metadata/#download-url
    'download-url':     ( ( 'download_url', ), None ),
    # https://packaging.python.org/en/latest/specifications/core-metadata/#home-page
    'home-url':         ( ( 'url', ), None ),
    'keywords':         ( ( 'keywords', ), concatenate_with_spaces ),
    'license':          ( ( 'license', 'license_files', ), extract_license ),
    'long-description':           (
        ( 'long_description', 'long_description_content_type', ),
        transform_long_description
    ),
    'maintainer':      (
        ( 'maintainer', 'maintainer_email', ),
        transform_contributor
    ),
    'name':             ( ( 'name', ), None ),
    'requires-python':  ( ( 'python_requires', ), None ),
    'urls':             ( ( 'project_urls', ), None ),
    'version':          ( ( 'version', ), None ),
}
def generate_nominative_arguments( ):
    ''' Generates nominative arguments to 'setuptools.setup'. '''
    sources_path = paths.sources.p.python3.relative_to( paths.project )
    return dict(
        install_requires = generate_installation_requirements( ),
        package_dir = { '': str( sources_path ) },
        # https://setuptools.pypa.io/en/latest/userguide/package_discovery.html
        packages = find_packages( where = str( sources_path ), include = '*' ),
        **convert_project_information( )
    )


def convert_project_information( ):
    ''' Converts information about project from local configuration.

        Project information is converted into a dictionary,
        which can be used as nominative arguments to 'setup.setuptools'. '''
    information = discover_project_information( )
    arguments = { }
    for index, specification in _converters.items( ):
        if index not in information: continue
        value = information[ index ]
        argument_names, converter = specification
        converter = converter or ( lambda x: ( x, ) )
        arguments.update( {
            argument_name: argument for argument_name, argument
            in zip( argument_names, converter( value ) ) if argument } )
    return arguments


def generate_installation_requirements( ):
    ''' Generates installation requirements from local configuration. '''
    simples, _ = indicate_python_packages( )
    return collapse_multilevel_dictionary( simples[ 'installation' ] )
