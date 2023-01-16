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


''' Entrypoint for development activity.

    The actual "brain" lives in the corresponding package. The sole purpose of
    this entrypoint is to find this brain and engage it. The following sequence
    of actions happens during the search:

    * Entrypoint looks for an isolated cache of essential Python packages that
      it may have previously created. If it does not find this cache or if it
      is missing Pip, then it creates the cache and bootstraps Pip into it. If
      other essential packages are missing from the cache, it then uses Pip to
      install those into the cache.

    * Entrypoint detects if it is operating within the confines of a Git
      repository. If yes, then it scans for any submodules which may have its
      brain. If it finds such a submodule, it attempts to update it,
      initializing it if necessary. Then it adds the expected path within the
      submodule to its Python module search path and attempts to import the
      package. If the import is success, then engagement of the brain occurs.

    * If no Git module is detected, then entrypoint detects if its brain is
      available on the Python module search path by attempting to import it. If
      the import is successful and the minimum required package version is
      satisfied, then engagement of the brain occurs.

    * If requisite package was not able to be imported, then entrypoint
      attempts to make an isolated installation of its brain using the
      bootstrapped Pip.

    Note that any installations performed by the entrypoint are isolated and
    non-intrusive, meaning that they will not "pollute" the system Python
    installation or any user-local Python installations, such as might be
    managed by 'asdf', 'pre-commit', 'pyenv', or 'tox'.

    The only universal requirement for the entrypoint is that is run via a
    Python interpreter of the minimum requisite version. If it cannot find a
    suitable cache of necessary packages, then it will also need Internet
    access to populate the cache. Neither 'git' nor 'pip' is required to
    operate the entrypoint. '''


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


import typing as _typ

from collections.abc import (
    Mapping as AbstractDictionary,
    Sequence as AbstractSequence,
)
from contextlib import contextmanager as context_manager
from datetime import (
    datetime as DateTime, timedelta as TimeDelta, timezone as TimeZone, )
from functools import partial as partial_function
from os import environ as current_process_environment
from pathlib import Path
from re import compile as regex_compile
from shlex import split as split_command
from types import MappingProxyType as DictionaryProxy


pypi_package_name = 'devshim'
package_name = pypi_package_name.replace( '-', '_' )
__version__ = '1.0a202301141418'
repository_name = f"python-{pypi_package_name}"


class Exit( SystemExit ):
    ''' Signal for process exit. '''

    labels: _typ.Mapping
    message: str

    def __init__( self, exit_specifier = 0, message = '', labels = None ):
        # TODO: Reconsider whether side effects are desirable in initializer.
        # Creation of this signal must succeed.
        try: scribe = _data.scribe
        except: # pylint: disable=bare-except
            scribe = lambda *posargs, **nomargs: None
        exit_codes = _provide_exit_codes( )
        from numbers import Integral
        if isinstance( exit_specifier, Integral ):
            exit_code = int( exit_specifier )
        elif exit_specifier not in exit_codes:
            scribe.warning( f"Invalid exit code name {exit_specifier!r}." )
            exit_code = exit_codes[ 'general failure' ]
        else: exit_code = exit_codes[ exit_specifier ]
        super( ).__init__( exit_code )
        self.message = str( message )
        if None is labels: labels = { }
        if not isinstance( labels, AbstractDictionary ):
            scribe.warning( f"Invalid exception labels {labels!r}." )
            labels = { }
        self.labels = labels
        if 0 == exit_code: scribe.info( message )
        # TODO: Python 3.8: stacklevel = 2
        else: scribe.critical( message, stack_info = True )

def _provide_exit_codes( ):
    # Standardized on recommended BSD exit codes across all platforms.
    # Windows seems to have no standard for application exit codes
    # and its list of system error codes is massive. (And error codes are not
    # necessarily exit codes.) Cannot rely on "constants" from Python standard
    # library 'os' modules as they are mostly not cross-platform.
    # Can also use custom codes between 1 and 63 for failures, as necessary.
    # References:
    #   https://docs.python.org/3/library/os.html#os.EX_OK
    #   https://www.freebsd.org/cgi/man.cgi?query=sysexits&apropos=0&sektion=0&manpath=FreeBSD+4.3-RELEASE&format=html
    #   https://tldp.org/LDP/abs/html/exitcodes.html
    #   https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes?redirectedfrom=MSDN#system-error-codes
    return DictionaryProxy( {
        'absent entity':        69, # EX_UNAVAILABLE
        'general failure':      1,
        'invalid data':         65, # EX_DATAERR
        'invalid state':        70, # EX_SOFTWARE
        'invalid usage':        64, # EX_USAGE
        'success':              0,  # EX_OK
    } )


def calculate_cache_identifier( ):
    ''' Calculates cache identifier from Python version and platform ID.

        Needs to be unique to not collide with other Python installations
        sharing the same file system. Needs to be shell-safe for use in paths
        and environment variables. Needs to be sensitive to Python or OS
        upgrades to ensure goodness of cache. A hex-encoded cryptographic
        digest of the raw Python version text, the platform uname, and the
        version of this program  meets these requirements handily. '''
    from hashlib import sha256
    from platform import uname
    from sys import version
    hasher = sha256( )
    hasher.update( ''.join( ( version, *uname( ), __version__ ) ).encode( ) )
    return hasher.hexdigest( )


def derive_caches_location( label ):
    ''' Derives cache location according to platform and cache identifier. '''
    # Cannot assume that we can import 'platformdirs', so we emulate the
    # relevant portion of that package.
    from sys import platform
    if 'win32' == platform:
        # TODO: Use query for 'CSIDL_LOCAL_APPDATA'.
        location = Path(
            current_process_environment.get( 'LOCALAPPDATA', '' ).strip( )
            or Path.home( ) / 'AppData/Local' ) / package_name
    elif 'darwin' == platform: location = Path.home( ) / 'Library/Caches'
    # TODO? Android support.
    else:
        location = Path(
            current_process_environment.get( 'XDG_CACHE_HOME', '' ).strip( )
            or Path.home( ) / '.cache' )
    cache_identifier = calculate_cache_identifier( )
    location = location / package_name / label / cache_identifier
    _data.scribe.debug( f"Caches Location: {location}" )
    _add_environment_entry( ( label, 'caches', 'location' ), location )
    return location


def derive_class_fqname( class_ ):
    ''' Derives fully-qualified class name from class object. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    from inspect import isclass as is_class
    if not is_class( class_ ):
        raise Exit(
            'invalid data',
            f"Cannot fully-qualified class name for non-class {class_!r}." )
    return '.'.join( ( class_.__module__, class_.__qualname__ ) )


def discover_repository_apex_directory( ):
    ''' Discovers apex directory of repository.

        In essence, this emulates ``git rev-parse --show-toplevel``,
        but without using that command, which we do not wish to assume is
        available to us. '''
    # TODO? Consider other repository type markers, if bridged to Git.
    from os.path import pathsep
    if 'GIT_WORK_TREE' in current_process_environment:
        return Path( 'GIT_WORK_TREE' ).resolve( strict = True )
    location = Path( ).resolve( )
    ceilings = frozenset( (
        Path.home( ), Path( location.root ),
        *(  Path( ceiling ).resolve( )
            for ceiling in filter(
                None,
                current_process_environment
                .get( 'GIT_CEILING_DIRECTORIES', '' ).split( pathsep ) ) ) ) )
    while location not in ceilings:
        if ( location / '.git' ).exists( ): return location
        location = location.parent
    raise FileNotFoundError


def discover_repository_records_directory( ):
    ''' Discovers records directory of repository. '''
    # Note: 'FileNotFoundError' exceptions are allowed to propagate by design.
    apex_location = _data.locations.repository_apex
    records_location = (
        Path(
            current_process_environment.get( 'GIT_DIR' )
            or ( apex_location / '.git' ) )
        .resolve( strict = True ) )
    # Account for indirection file in submodules.
    if records_location.is_file( ):
        with records_location.open( encoding = 'utf-8' ) as file:
            for line in file:
                if not line.startswith( 'gitdir: ' ): continue
                records_location = (
                    ( apex_location / line.split( ': ' )[ -1 ].strip( ) )
                    .resolve( strict = True ) )
                break
    if not records_location.is_dir( ): raise FileNotFoundError
    return records_location


def ensure_artifacts_cache( label ):
    ''' Ensures directory for retrieved artifacts exists. '''
    location = getattr( _data.locations.caches, label ) / 'artifacts'
    location.mkdir( exist_ok = True, parents = True )
    return location


def ensure_directory( path ):
    ''' Ensures existence of directory, creating if necessary. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    path.mkdir( parents = True, exist_ok = True )
    return path


def ensure_main_packages( configuration_location ):
    ''' Ensures installation dependencies for package are in cache. '''
    _ensure_pre_packages( )
    with imports_from_cache( ensure_packages_cache( 'pre' ) ):
        from packaging.requirements import Requirement
        from tomli import load
    with configuration_location.open( 'rb' ) as file:
        configuration = load( file )
    # Note: Development dependencies are not processed here.
    #       Those are installed by the brain into virtual environments.
    # TODO? Support for optional dependencies.
    requirements = tuple(
        ( Requirement( requirement ).name, requirement ) for requirement
        in configuration[ 'project' ][ 'dependencies' ] )
    ensure_packages( ensure_packages_cache( 'main' ), requirements )


def ensure_packages( packages_location, requirements ):
    ''' Ensure all packages in cohort exist and are recent. '''
    if is_dirent_older_than( packages_location, TimeDelta( days = 1 ) ):
        return _ensure_packages( packages_location, requirements )
    # In-cache package installation directories can be anything. E.g.,
    # 'beautifulsoup4' -> 'bs4'. Names of in-cache distinfo directories start
    # with the names of packages with hyphens converted to underscores. E.g.,
    # 'pre-commit' -> 'pre_commit'. Aside from parsing the 'top-level.txt'
    # files in the distinfo directories to discover package installation
    # directories and verifying them, we are forced to perform O(m*n) iteration
    # to match package names. Our only succor in this situation is that we can
    # stop iteration at first cache miss.
    distinfo_names = tuple(
        location.name for location in packages_location.glob( '*.dist-info' ) )
    for name, _ in requirements:
        # Need hyphen at end to disambiguate matches in case one package name
        # is a truncation of another one.
        name_ = "{name}-".format( name = name.replace( '-', '_' ) )
        for distinfo_name in distinfo_names:
            if distinfo_name.startswith( name_ ): break
        else: return _ensure_packages( packages_location, requirements )

def _ensure_packages( location, requirements ):
    install_packages(
        location, tuple( requirement for _, requirement in requirements ) )


def ensure_packages_cache( label ):
    ''' Ensures directory for Python packages exists. '''
    location = getattr( _data.locations.caches, label ) / 'packages'
    location.mkdir( exist_ok = True, parents = True )
    return location


def execute_python_subprocess(
    command_specification, packages_location = None, **nomargs
):
    ''' Executes command with same executable as active interpreter.

        Also adds special packages cache to :envvar:`PYTHONPATH`. '''
    from os.path import pathsep
    from sys import executable as python_location
    command_specification = _normalize_command_specification(
        command_specification )
    if None is packages_location:
        packages_location = ensure_packages_cache( 'pre' )
    process_environment = current_process_environment.copy( )
    process_environment[ 'PYTHONPATH' ] = pathsep.join( (
        str( packages_location ),
        *process_environment.get( 'PYTHONPATH', '' ).split( pathsep ) ) )
    env_specifier = nomargs.get( 'env', { } )
    env_specifier.update( process_environment )
    nomargs[ 'env' ] = env_specifier
    return execute_subprocess(
        ( ( python_location, *command_specification ) ), **nomargs )


def execute_subprocess( command_specification, **nomargs ):
    ''' Executes command in subprocess. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    command_specification = _normalize_command_specification(
        command_specification )
    from subprocess import run # nosec: B404
    from sys import stderr
    scribe = _data.scribe
    options = dict( text = True )
    options.update( nomargs )
    # Sanitize options.
    for option in ( 'check', ): nomargs.pop( option, None )
    if not options.get( 'capture_output', False ):
        options[ 'stdout' ] = stderr
    if { 'stdout', 'stderr' } & options.keys( ):
        options.pop( 'capture_output', None )
    scribe.debug( f"Executing {command_specification!r} with {options!r}." )
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit
    return run( command_specification, check = True, **options ) # nosec: B603


def http_retrieve_url( url, destination = None, headers = None ): # pylint: disable=too-many-statements
    ''' Retrieves URL into destination via Hypertext Transfer Protocol.

        The destination may be a path-like object, an object with a ``write``
        method, such as an open stream, or a callable which consumes a stream
        from an object with a ``read`` method. The callable must take two
        positional arguments, which will be the HTTP reader object and the
        context stack that ensures proper resource cleanup. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    from http import HTTPStatus as HttpStatus
    from random import random
    from time import sleep
    from urllib.error import HTTPError as HttpError
    from urllib.request import Request as HttpRequest
    destination = _normalize_retrieval_destination( destination )
    headers = headers or { } # TODO: Validate headers.
    request = HttpRequest( url, headers = headers )
    attempts_count_max = 2
    for attempts_count in range( attempts_count_max + 1 ):
        try: return _http_retrieve_url( request, destination )
        except HttpError as exc:
            _data.scribe.error( f"Failed to retrieve data from {url!r}." )
            # Exponential backoff with collision-breaking jitter.
            backoff_time = 2 ** attempts_count + 2 * random( ) # nosec: B311
            if HttpStatus.TEMPORARY_REDIRECT.value == exc.code:
                url = exc.headers[ 'Location' ]
                _data.scribe.debug( f"Temporary redirect to {url!r}." )
                return http_retrieve_url( url, destination, headers )
            if HttpStatus.PERMANENT_REDIRECT.value == exc.code:
                url = exc.headers[ 'Location' ]
                _data.scribe.warning( f"Permanent redirect to {url!r}." )
                return http_retrieve_url( url, destination, headers )
            if HttpStatus.NOT_FOUND.value == exc.code: raise
            if HttpStatus.TOO_MANY_REQUESTS.value == exc.code:
                backoff_time = float(
                    exc.headers.get( 'Retry-After', backoff_time ) )
                if 120 < backoff_time: raise # Do not wait too long.
            if attempts_count_max == attempts_count: raise
            _data.scribe.info(
                f"Will attempt retrieval from {url!r} again "
                f"in {backoff_time} seconds." )
            sleep( backoff_time )
    raise Exit( 'invalid state' )

def _http_retrieve_url( request, destination ):
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    from contextlib import ExitStack as ContextStack
    from urllib.request import urlopen as access_url
    contexts = ContextStack( )
    with contexts:
        # nosemgrep: python.lang.security.audit.dynamic-urllib-use-detected
        http_reader = contexts.enter_context( access_url( request ) )
        if None is destination: return http_reader.read( )
        if callable( destination ): return destination( http_reader, contexts )
        if isinstance( destination, Path ):
            file = contexts.enter_context( destination.open( 'wb' ) )
            file.write( http_reader.read( ) )
        elif callable( getattr( destination, 'write', None ) ):
            destination.write( http_reader.read( ) )
        return destination


def import_module( packages_location, module_name ):
    ''' Imports module without alteration to search paths or registry. '''
    from importlib.util import module_from_spec, spec_from_file_location
    module_location = packages_location.joinpath( *module_name.split( '.' ) )
    if module_location.is_dir( ): module_location /= '__init__.py'
    else: module_location = module_location.with_suffix( '.py' )
    module_spec = spec_from_file_location( module_name, module_location )
    if None is module_spec:
        raise ImportError(
            f"Could not import module {module_name} "
            f"from {packages_location}.",
            name = module_name, path = packages_location )
    module = module_from_spec( module_spec )
    module_spec.loader.exec_module( module )
    return module


@context_manager
def imports_from_cache( location ):
    ''' Manages imports via cache location. '''
    # TODO? Fix importer to maintain its own modules registry and search paths.
    #       May need to create custom import hook and insert it into first slot
    #       of import hooks.
    # XXX: Temporarily modify modules search paths.
    from site import addsitedir
    from sys import path as modules_search_paths
    addsitedir( str( location ) ) # Ensure '.pth' files are processed.
    modules_search_paths.insert( 0, str( location ) )
    yield
    modules_search_paths.remove( str( location ) )


def install_packages( location, requirements ):
    ''' Installs Python packages into drectory. '''
    if isinstance( requirements, Path ):
        requirements = ( '--requirement', requirements )
    elif isinstance( requirements, str ):
        requirements = ( requirements, )
    _data.scribe.info( f"Installing Python packages to '{location}'." )
    # Force reinstall to help ensure sanity.
    execute_python_subprocess(
        ( _ensure_pip( ), 'install', '--target', location,
          '--force-reinstall', '--upgrade', '--upgrade-strategy=eager',
          *requirements ) )


def is_dirent_older_than( path, then ):
    ''' Is file system entity older than delta time from now? '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    if isinstance( then, DateTime ): when = then.timestamp( )
    elif isinstance( then, TimeDelta ):
        when = ( DateTime.now( TimeZone.utc ) - then ).timestamp( )
    else:
        raise Exit(
            'invalid data',
            f"Expected time delta or absolute datetime; received {then!r}" )
    # Windows apparently does not track file metadata change time (ctime);
    # instead file birth time is substituted for ctime on that platform.
    # Therefore, we rely on file content modification time (mtime).
    # This provides the desired behavior in nearly all cases anyway.
    return path.stat( ).st_mtime < when


def produce_accretive_cacher( calculators_provider ):
    ''' Produces object which computes and caches values.

        The ``calculators_provider`` argument must return a dictionary of cache
        entry names with nullary invocables as the correspondent values. Each
        invocable is a calculator which produces a value to populate the cache.
        Any attribute name not in the dictionary results in an
        :py:exc:`AttributeError`. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    cache = { }
    validate_cache_calculators_provider( calculators_provider )
    calculators = DictionaryProxy( calculators_provider( ) )

    class AccretiveCacher:
        ''' Computes values on demand and caches them. '''

        __slots__ = ( )

        def __getattr__( self, name ):
            if name not in calculators: raise AttributeError
            if name not in cache: cache[ name ] = calculators[ name ]( )
            return cache[ name ]

        def __setattr__( self, name, value ):
            raise Exit(
                'invalid state',
                "Cannot assign attributes on cacher object." )

        def __delattr__( self, name ):
            raise Exit(
                'invalid state',
                "Cannot remove attributes from cacher object." )

    return AccretiveCacher( )


def summon_git_repository_configuration( ):
    ''' Returns configuration object for Git repository. '''
    _ensure_pre_packages( )
    # Note: 'FileNotFoundError' exceptions are allowed to propagate by design.
    configuration_location = _data.locations.repository_records / 'config'
    if not configuration_location.is_file( ): raise FileNotFoundError
    with imports_from_cache( ensure_packages_cache( 'pre' ) ):
        from dulwich.config import ConfigFile # pylint: disable=import-error
    return ConfigFile.from_path( str( configuration_location ) )


def summon_git_submodules_configuration( ):
    ''' Returns configuration object for submodules of Git repository. '''
    _ensure_pre_packages( )
    # Note: 'FileNotFoundError' exceptions are allowed to propagate by design.
    configuration_location = _data.locations.repository_apex / '.gitmodules'
    if not configuration_location.is_file( ): raise FileNotFoundError
    with imports_from_cache( ensure_packages_cache( 'pre' ) ):
        from dulwich.config import ConfigFile # pylint: disable=import-error
    return ConfigFile.from_path( str( configuration_location ) )


def validate_cache_calculators_provider( provider ):
    ''' Validates provider of calculators for accretive cacher. '''
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    if not callable( provider ):
        raise Exit(
            'invalid data',
            f"Calculators provider for accretive cache must be invocable." )
    # TODO: Further validate calculators provider.
    return provider


def main( ):
    ''' Entrypoint for development activity. '''
    _configure_base_scribe( )
    prepare( _data.locations.repository_apex )
    with imports_from_cache( ensure_packages_cache( 'main' ) ):
        from invoke import Collection, Program # pylint: disable=import-error
        from devshim import tasks # pylint: disable=import-error
        Program( namespace = Collection.from_module( tasks ) ).run( )


def prepare( project_location ):
    ''' Locates and prepares development support modules. '''
    _add_environment_entry( ( 'project', 'location' ), project_location )
    _acquire_cranial_matter( )


def _acquire_cranial_matter( ):
    species, location = _locate_cranial_matter( )
    if 'remote' == species: location = _data.locations.repository_apex
    elif 'submodule' == species: _ensure_git_submodule( location )
    if species in ( 'remote', 'submodule', ):
        _ensure_me_as_editable_wheel( location )
        # Installing editable wheel also installs dependencies.
        # However, we want to ensure that the dependencies are up-to-date.
        ensure_main_packages( location / 'pyproject.toml' )
    elif 'package' == species:
        try:
            import devshim # pylint: disable=unused-import
            # TODO? Check for sufficient version. If not, then install.
        except ImportError: _install_me( )


def _acquire_scribe( ):
    ''' Gets package logger. '''
    import logging
    return logging.getLogger( package_name )


def _add_environment_entry( parts, value ):
    ''' Inserts entry into current process environment.

        Entry name is derived from parts and package name. '''
    name = _derive_environment_variable_name( *parts )
    current_process_environment[ name ] = str( value )
    return name


def _clone_git_submodule( submodule_location ):
    ''' Clones Git submodule for package, if possible. '''
    # Note: At the time of this writing (2023-01-14), Dulwich does not have
    #       support for initializing Git submodules. So, we fallback to 'git',
    #       if it is available.
    from shutil import which
    git_location = which( 'git' )
    if not git_location: return False
    _data.scribe.info( f"Updating Git submodule at {submodule_location}." )
    execute_subprocess(
        ( git_location,
          *split_command( 'submodule update --init --recursive --' ),
          submodule_location ) )
    return True


def _configure_base_scribe( ):
    ''' Configures logging system and root logger. '''
    import logging
    record_level_evariable_name = (
        _derive_environment_variable_name( 'record', 'level' ) )
    record_level_name_default = 'INFO'
    record_level_name = current_process_environment.get(
        record_level_evariable_name, record_level_name_default )
    valid_record_level = hasattr( logging, record_level_name )
    record_level = getattr(
        logging,
        record_level_name if valid_record_level
        else record_level_name_default )
    logging.basicConfig(
        format = "%(levelname)s\t%(message)s", level = record_level )
    logging.captureWarnings( True )
    _add_environment_entry( ( 'record', 'level' ), record_level_name )
    scribe = logging.getLogger( )
    scribe.debug( 'Logging initialized.' )
    if not valid_record_level:
        scribe.warning(
            f"Invalid log level name, {record_level_name!r}. "
            f"Using {record_level_name_default!r} instead." )
    return scribe


def _derive_environment_variable_name( *parts ):
    ''' Derives environment variable name from parts and package name. '''
    return '_'.join( map( str.upper, ( package_name, *parts ) ) )


def _ensure_git_submodule( location ):
    ''' Ensures validity of git submodule for package, if possible. '''
    valid = location.is_dir( )
    valid = valid and 0 < len( tuple( location.iterdir( ) ) )
    if not valid: valid = _clone_git_submodule( location )
    if valid: return
    raise Exit(
        'invalid state',
        f"Please initialize the Git submodule at '{location}'." )


def _ensure_me_as_editable_wheel( project_location ):
    packages_location = ensure_packages_cache( 'main' )
    distinfo_location = (
        packages_location / f"{package_name}-{__version__}.dist-info" )
    if distinfo_location.exists( ): return
    execute_python_subprocess(
        ( _ensure_pip( ), 'install', '--editable', project_location,
          '--force-reinstall', '--upgrade', '--upgrade-strategy=eager',
          #'--no-deps', '-vvv',
          '--target', packages_location, ) )


def _ensure_pip( ):
    artifacts_location = ensure_artifacts_cache( 'pre' )
    location = artifacts_location / 'pip.pyz'
    if location.exists( ):
        if not is_dirent_older_than( location, TimeDelta( days = 1 ) ):
            return location
    _retrieve_pip( location )
    return location


def _ensure_pre_packages( ):
    ensure_packages(
        ensure_packages_cache( 'pre' ),
        (   ( 'dulwich',    'dulwich~=0.20.50' ),
            ( 'packaging',  'packaging~=22.0' ),
            ( 'tomli',      'tomli~=2.0' ),
        ) )


def _extract_git_remotes_urls( ):
    configuration = _data.configurations.git_repository
    remotes = { }
    for section in configuration.sections( ):
        if b'remote' != section[ 0 ]: continue
        for item in configuration.items( section ):
            if b'url' != item[ 0 ]: continue
            name = section[ 1 ].decode( )
            remotes[ name ] = item[ 1 ].decode( )
            break
    return DictionaryProxy( remotes )


def _extract_git_submodules_urls( ):
    try: configuration = _data.configurations.git_submodules
    except FileNotFoundError: return DictionaryProxy( { } )
    repository_location = _data.locations.repository_apex
    from dulwich.config import parse_submodules # pylint: disable=import-error
    submodules = { }
    for location, url, _ in parse_submodules( configuration ):
        submodules[ repository_location / location.decode( ) ] = url.decode( )
    return DictionaryProxy( submodules )


def _install_me( ):
    ''' Installs package associated with this program. '''
    # TODO? Prompt user for confirmation since this is intrusive.
    execute_python_subprocess(
        ( _ensure_pip( ), 'install', '--user',
          '--force-reinstall', '--upgrade', '--upgrade-strategy=eager',
          pypi_package_name ) )


_our_repository_regex = regex_compile(
    rf'''^.*github.com(?:[:/])[^/]+/{repository_name}(?:.git)?''' )
def _locate_cranial_matter( ):
    try:
        remotes = _extract_git_remotes_urls( )
        submodules = _extract_git_submodules_urls( )
    except FileNotFoundError as exc:
        cwd = Path( ).resolve( )
        raise Exit(
            'invalid usage',
            f"No Git repository detected at {cwd!r} or above." ) from exc
    for name, url in remotes.items( ):
        if _our_repository_regex.match( url ): return 'remote', name
    for location, url in submodules.items( ):
        if _our_repository_regex.match( url ): return 'submodule', location
    return 'package', None


def _normalize_command_specification( command_specification ):
    if isinstance( command_specification, str ):
        return split_command( command_specification )
    # Ensure strings are being passed as arguments.
    # Although 'subprocess.run' can accept path-like objects on all platforms,
    # as of Python 3.8, there may be non-path-like objects as arguments that
    # need to be converted to strings. So, we always convert.
    if isinstance( command_specification, AbstractSequence ):
        return tuple( map( str, command_specification ) )
    raise Exit(
        'invalid data',
        f"Invalid command specification {command_specification!r}" )


def _normalize_retrieval_destination( destination ):
    # NOTE: Similar implementation exists in package.
    #       Improvements should be reflected in both places.
    if isinstance( destination, str ): destination = Path( destination )
    if isinstance( destination, Path ) and not destination.exists( ):
        destination.parent.mkdir( exist_ok = True, parents = True )
    if not any( (
        None is destination,
        isinstance( destination, Path ),
        callable( getattr( destination, 'write', None ) ),
        callable( destination )
    ) ):
        raise Exit(
            'invalid data',
            "Cannot use instance of {class_name!r} "
            "as retrieval destination.".format(
                class_name = derive_class_fqname( type( destination ) ) ) )
    return destination


def _provide_calculators( ):
    return dict(
        configurations = (
            lambda: produce_accretive_cacher( _provide_configurations ) ),
        locations = (
            lambda: produce_accretive_cacher( _provide_locations ) ),
        scribe = _acquire_scribe,
    )


def _provide_configurations( ):
    return dict(
        git_repository = summon_git_repository_configuration,
        git_submodules = summon_git_submodules_configuration,
    )


def _provide_locations( ):
    return dict(
        caches = lambda: produce_accretive_cacher( lambda: dict(
            main = partial_function( derive_caches_location, 'main' ),
            pre = partial_function( derive_caches_location, 'pre' ),
        ) ),
        repository_apex = discover_repository_apex_directory,
        repository_records = discover_repository_records_directory,
    )


def _retrieve_pip( location ):
    url = f"https://bootstrap.pypa.io/pip/{location.name}"
    _data.scribe.info( f"Retrieving Pip from {url!r}." )
    http_retrieve_url( url, location )


_data = produce_accretive_cacher( _provide_calculators )
__getattr__ = _data.__getattr__


if '__main__' == __name__: main( )
