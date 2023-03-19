# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
#                                                                             #
###############################################################################


''' Locates and executes entrypoint for development activity.

    By default, this module will attempt to download and extract its
    corresponding development support package from Github, if it does not
    already exist locally. To override this behavior, you can set the
    ``source_specifier`` module attribute to one of the following:

    * ``git:submodule:<path>``
      For coordinated development of the project and the development support
      package. The path is relative to the top of the project repository.

    * ``github``
      Zip archive of the head of the default branch of the development support
      project. Retrieved via the Github Repository Archive API:
        https://api.github.com/repos/OWNER/REPO/zipball/REF
      Archive updates automatically.

    * ``github:<release>``
      Zip archive of the given release of the development support project.
      Retrieved via the Github Repository Archive API:
        https://api.github.com/repos/OWNER/REPO/zipball/REF
      Does not update automatically; it is the responsibility of the project
      maintainer.

    * ``zipfile:<path>``
      Vendored Zip archive of the development support project. The path is
      relative to the top of the project repository. Does not update
      automatically; it is the responsibility of the project maintainer. '''


## Maintainer Variables

source_specifier = 'git:submodule:.local/scm-modules/python-devshim'


## Module Code

def assert_minimum_python_version( ):
    ''' Asserts minimum Python version.

        Checking the Python version must be done in a backwards-compatible
        manner, so as to not trigger syntax exceptions in the checking logic.
        (Compatibility of this logic has been tested back to Python 2.6.) '''
    required_version = 3, 7
    error_message = '\nERROR: Python {0}.{1} or higher required.\n'.format(
        required_version[ 0 ], required_version[ 1 ] )
    from sys import stderr, version_info
    version = version_info[ 0 ], version_info[ 1 ]
    if required_version > version:
        stderr.write( error_message ); stderr.flush( )
        raise SystemExit( 69 ) # EX_UNAVAILABLE

assert_minimum_python_version( )


from pathlib import Path


__version__ = '1.0a202301141418'
package_name = 'devshim'


try: source_specifier
except NameError: source_specifier = 'github'


def import_entrypoint( project_location ):
    ''' Imports development support entrypoint in isolation from other modules.

        Neither :py:data:`sys.path` or :py:data:`sys.modules` is modified by
        this operation. '''
    if 'identity' == source_specifier:
        return _import_entrypoint_from_fs( project_location )
    if source_specifier.startswith( 'git:submodule:' ):
        package_location_base = project_location.joinpath(
            source_specifier.split( ':', maxsplit = 2 )[ 2 ] ).resolve( )
        ensure_git_submodule( package_location_base )
        return _import_entrypoint_from_fs( package_location_base )
    if 'github' == source_specifier:
        return _import_entrypoint_from_github( project_location )
    if source_specifier.startswith( 'github:' ):
        return _import_entrypoint_from_github(
            project_location,
            git_ref = source_specifier.split( ':', maxsplit = 1 )[ 1 ] )
    if source_specifier.startswith( 'zipfile:' ):
        return _import_entrypoint_from_zipfile(
            project_location,
            project_location.joinpath(
                source_specifier.split( ':', maxsplit = 1 )[ 1 ] ).resolve( ) )
    raise ValueError( f"Invalid source specifier {source_specifier!r}." )

def _import_entrypoint_from_fs( package_location_base ):
    package_location_base /= 'sources/python3'
    if not package_location_base.exists( ):
        raise FileNotFoundError(
            f"No packages directory at '{package_location_base}'." )
    module_name = f"{package_name}.__main__"
    module_location = package_location_base.joinpath(
        *module_name.split( '.' ) ).with_suffix( '.py' )
    from importlib.util import module_from_spec, spec_from_file_location
    module_spec = spec_from_file_location( module_name, module_location )
    if None is module_spec:
        raise ImportError(
            f"Could not import module {module_name} "
            f"from {package_location_base}.",
            name = module_name, path = package_location_base )
    module = module_from_spec( module_spec )
    module_spec.loader.exec_module( module )
    return module

def _import_entrypoint_from_github( project_location, git_ref = None ):
    from datetime import timedelta as TimeDelta
    archives_location = Path( _view_environment_entry(
        ( 'archives', 'location' ),
        f"{project_location}/.local/caches/{package_name}/archives" ) )
    archive_location = archives_location / f"{package_name}.zip"
    if archive_location.is_file( ):
        if git_ref or not _is_dirent_older_than(
            archive_location, TimeDelta( days = 1 )
        ):
            return _import_entrypoint_from_zipfile(
                project_location, archive_location )
    archive_location.parent.mkdir( parents = True, exist_ok = True )
    github_retrieve_zipball( 'emcd/python-devshim', git_ref, archive_location )
    return _import_entrypoint_from_zipfile(
        project_location, archive_location, force = True )

# Note: Cannot use 'importlib' machinery with Zip archives for several reasons:
#       * 'zipimport' on Python 3.7 has broken support for the Zip format. For
#         more details, see:
#           https://stackoverflow.com/a/51821910/14833542
#           https://bugs.python.org/issue25711
#       * 'zipimport.load_module' walks the package to get a module, which
#         means that we cannot guarantee dependencies have been installed. Can
#         possibly mitigate with Python 3.10 'zipimport.find_spec'.
def _import_entrypoint_from_zipfile(
    project_location, archive_location, force = False
):
    repositories_location = Path( _view_environment_entry(
        ( 'repositories', 'location' ),
        f"{project_location}/.local/caches/{package_name}/repositories" ) )
    repository_location = repositories_location / package_name
    if not force and repository_location.is_dir( ):
        return _import_entrypoint_from_fs( repository_location )
    from contextlib import ExitStack as CMStack
    from shutil import move, rmtree
    from tempfile import TemporaryDirectory
    from zipfile import ZipFile
    _acquire_scribe( ).info(
        f"Extracting '{archive_location}' to '{repository_location}'." )
    with CMStack( ) as contexts:
        zipfile = contexts.enter_context( ZipFile( archive_location, 'r' ) )
        temporary_location = Path( contexts.enter_context(
            TemporaryDirectory( ) ) )
        source_name = Path( zipfile.namelist( )[ 0 ] ).parts[ 0 ]
        zipfile.extractall( path = temporary_location )
        if repository_location.exists( ): rmtree( repository_location )
        move( temporary_location / source_name, repository_location )
    return _import_entrypoint_from_fs( repository_location )


def ensure_git_submodule( location ):
    ''' Ensures validity of git submodule for package, if possible. '''
    valid = location.is_dir( )
    valid = valid and 0 < len( tuple( location.iterdir( ) ) )
    if not valid: valid = _clone_git_submodule( location )
    if valid: return
    raise FileNotFoundError(
        f"Missing or uninitialized Git submodule at '{location}'." )

def _clone_git_submodule( submodule_location ):
    ''' Clones Git submodule for package, if possible. '''
    from shutil import which
    git_location = which( 'git' )
    if not git_location: return False
    _acquire_scribe( ).info(
        f"Updating Git submodule at {submodule_location}." )
    from subprocess import run # nosec b404
    from sys import stderr
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit
    run( # nosec b603
        ( git_location,
          *'submodule update --init --recursive --'.split( ),
          str( submodule_location ) ),
        check = True, stdout = stderr )
    return True


def ensure_sanity( ):
    ''' Ensures sanity of the development support package.

        Includes installation of prerequisite dependencies, if necessary. '''
    project_location = Path( __file__ ).resolve( ).parent
    module = import_entrypoint( project_location )
    return module.ensure_sanity( project_location = project_location )


def github_retrieve_zipball( repository_qname, git_ref, destination ):
    ''' Retrieves zipball for Git repository and ref into destination. '''
    url = f"https://api.github.com/repos/{repository_qname}/zipball"
    headers = {
        'Accept': 'application/vnd.github+json',
        'X-GitHub-Api-Version': '2022-11-28',
    }
    if git_ref: url = "{url}/{git_ref}"
    _acquire_scribe( ).info( f"Attempting download from {url!r}." )
    http_retrieve_url( url, destination, headers = headers )


def http_retrieve_url( url, destination, headers = None ):
    ''' Retrieves URL into destination via Hypertext Transfer Protocol.

        The destination must be a :py:class:`pathlib.Path` object. '''
    from random import random
    from time import sleep
    from urllib.error import HTTPError as HttpError
    from urllib.request import Request as HttpRequest
    headers = headers or { }
    request = HttpRequest( url, headers = headers )
    scribe = _acquire_scribe( )
    attempts_count_max = 2
    for attempts_count in range( attempts_count_max + 1 ):
        try: return _http_retrieve_url( request, destination )
        except HttpError as exc:
            scribe.error( f"Failed to retrieve data from {url!r}." )
            # Exponential backoff with collision-breaking jitter.
            backoff_time = 2 ** attempts_count + 2 * random( ) # nosec: B311
            # https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml
            if exc.code in ( 301, 302, 307, 308 ):  # Redirects
                if 'Location' in exc.headers:
                    url = exc.headers[ 'Location' ]
                    return http_retrieve_url( url, destination, headers )
                raise
            if 404 == exc.code: raise               # Not Found
            if 429 == exc.code:                     # Too Many Requests
                backoff_time = float(
                    exc.headers.get( 'Retry-After', backoff_time ) )
                if 120 < backoff_time: raise # Do not wait too long.
            if attempts_count_max == attempts_count: raise
            scribe.info(
                f"Will attempt retrieval from {url!r} again "
                f"in {backoff_time} seconds." )
            sleep( backoff_time )
    raise RuntimeError(
        'Wut? Unexpectedly fell out of HTTP retrieval retry loop.' )

def _http_retrieve_url( request, destination ):
    from contextlib import ExitStack as ContextStack
    from urllib.request import urlopen as access_url
    contexts = ContextStack( )
    with contexts:
        # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected
        http_reader = contexts.enter_context( access_url( request ) )
        file = contexts.enter_context( destination.open( 'wb' ) )
        file.write( http_reader.read( ) )
        return destination


def main( ):
    ''' Entrypoint for development activity. '''
    project_location = Path( __file__ ).resolve( ).parent
    _configure_scribe( )
    module = import_entrypoint( project_location )
    module.main( project_location = project_location )


from logging import getLogger as _acquire_scribe


def _configure_scribe( ):
    record_level_name_default = 'INFO'
    record_level_name = _view_environment_entry(
        ( 'record', 'level' ), record_level_name_default )
    import logging
    valid_record_level = hasattr( logging, record_level_name )
    record_level = getattr(
        logging,
        record_level_name if valid_record_level
        else record_level_name_default )
    logging.basicConfig(
        format = "%(levelname)s\t%(message)s", level = record_level )
    logging.captureWarnings( True )
    scribe = _acquire_scribe( )
    scribe.debug( 'Logging initialized.' )
    if not valid_record_level:
        scribe.warning(
            f"Invalid log level name, {record_level_name!r}. "
            f"Using {record_level_name_default!r} instead." )
    return scribe


def _derive_environment_entry_name( *parts ):
    return '_'.join( map( str.upper, ( package_name, *parts ) ) )


def _is_dirent_older_than( path, then ):
    from datetime import datetime as DateTime, timezone as TimeZone
    when = ( DateTime.now( TimeZone.utc ) - then ).timestamp( )
    # Check against content modification time.
    return path.stat( ).st_mtime < when


def _view_environment_entry( parts, default = None ):
    from os import environ as current_process_environment
    name = _derive_environment_entry_name( *parts )
    return current_process_environment.get( name, default )


if __name__ in ( '<run_path>', '__main__' ): main( )
