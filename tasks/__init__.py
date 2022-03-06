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

''' Project maintenance tasks, executed via :command:`invoke`.

    `Invoke Documentation <http://docs.pyinvoke.org/en/stable/index.html>`_

    Only relies on Python standard library and Invoke and TOML modules to
    minimize dependencies, since it can be used to prepare development
    environments. '''


import re

from contextlib import ExitStack as CMStack
from itertools import chain
from json import load as load_json
from os import environ as psenv
from pathlib import Path
from shlex import (
    split as split_command,
    quote as shell_quote,
)
from shutil import which
from sys import stderr
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from types import SimpleNamespace
from urllib.error import URLError as UrlError
from urllib.parse import urlparse
from urllib.request import ( Request as HttpRequest, urlopen, )
from venv import create as create_venv

from invoke import Context, Exit, Failure, call, task

from .base import (
    assert_gpg_tty,
    derive_venv_context_options,
    derive_venv_path,
    detect_vmgr_python_path,
    eprint, epprint,
    generate_pip_requirements_text,
    indicate_python_versions_support,
    on_tty,
    paths,
    render_boxed_title,
    unlink_recursively,
)
from our_base import (
    discover_project_version,
    ensure_directory,
    ensure_python_package,
    identify_python,
    indicate_python_packages,
    project_name,
    standard_execute_external,
)


# https://www.sphinx-doc.org/en/master/man/sphinx-build.html
sphinx_options = f"-j auto -d {paths.caches.sphinx} -n -T"
# https://github.com/pypa/wheel/issues/306#issuecomment-522529825
setuptools_build_command = f"build --build-base {paths.caches.setuptools}"


@task
def install_git_hooks( context ):
    ''' Installs hooks to check goodness of code changes before commit. '''
    render_boxed_title( 'Install: Git Pre-Commit Hooks' )
    context.run(
        f"pre-commit install --config {paths.configuration.pre_commit} "
        f"--install-hooks", pty = True, **derive_venv_context_options( ) )


@task
def install_pythons( context ):
    ''' Installs each supported Python version.

        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Install: Python Releases' )
    context.run( 'asdf install python', pty = True )


@task( pre = ( install_pythons, ) )
def build_python_venvs( context ):
    ''' Creates virtual environment for each supported Python version. '''
    for version in indicate_python_versions_support( ):
        build_python_venv( context, version )


@task
def build_python_venv( context, version, overwrite = False ):
    ''' Creates virtual environment for requested Python version. '''
    render_boxed_title( f"Build: Python Virtual Environment ({version})" )
    python_path = detect_vmgr_python_path( version )
    venv_path = ensure_directory( derive_venv_path( version, python_path ) )
    venv_options = [ ]
    if overwrite: venv_options.append( '--clear' )
    venv_options_str = ' '.join( venv_options )
    context.run(
        f"{python_path} -m venv {venv_options_str} {venv_path}", pty = True )
    context_options = derive_venv_context_options( venv_path )
    install_python_packages( context, context_options )
    fixtures = calculate_python_packages_fixtures( context_options )
    identifier = identify_python(
        'pep508-environment',
        python_path = which(
            'python', path = context_options[ 'env' ][ 'PATH' ] ) )
    record_python_packages_fixtures( identifier, fixtures )


@task( pre = ( build_python_venvs, install_git_hooks, ) )
def bootstrap( context ): # pylint: disable=unused-argument
    ''' Bootstraps the development environment and utilities. '''


@task
def clean_pycaches( context ): # pylint: disable=unused-argument
    ''' Removes all caches of compiled CPython bytecode. '''
    render_boxed_title( 'Clean: Python Caches' )
    anchors = ( paths.sources.p.python3, paths.tests.p.python3, )
    # TODO? Use 'shutil.rmtree' instead.
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '__pycache__/*' ), anchors
    ) ): path.unlink( )
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '__pycache__' ), anchors
    ) ): path.rmdir( )


@task
def clean_tool_caches( context ): # pylint: disable=unused-argument
    ''' Clears the caches used by code generation and testing utilities. '''
    render_boxed_title( 'Clean: Tool Caches' )
    # TODO? Simplify by using a single .gitignore in paths.caches.
    anchors = paths.caches.SELF.glob( '*' )
    gitignore_paths = set( paths.caches.SELF.glob( '*/.gitignore' ) )
    dirs_stack = [ ]
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '*' ), anchors
    ) ):
        if path in gitignore_paths: continue
        if path.is_dir( ) and not path.is_symlink( ):
            dirs_stack.append( path )
            continue
        path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )
    unlink_recursively( paths.caches.eggs )


@task
def clean_pythons_packages( context ):
    ''' Removes unused Python packages in all virtual environments. '''
    for version in indicate_python_versions_support( ):
        clean_python_packages( context, version )


@task
def clean_python_packages( context, version = None ):
    ''' Removes unused Python packages in virtual environment. '''
    render_boxed_title( 'Clean: Unused Python Packages', supplement = version )
    context_options = derive_venv_context_options( version = version )
    identifier = identify_python(
        'pep508-environment',
        python_path = which(
            'python', path = context_options[ 'env' ][ 'PATH' ] ) )
    _, fixtures = indicate_python_packages( identifier = identifier )
    requested = frozenset( fixture[ 'name' ] for fixture in fixtures )
    installed = frozenset(
        entry.requirement.name
        for entry in indicate_current_python_packages( context_options ) )
    requirements_text = '\n'.join( installed - requested - { project_name } )
    if not requirements_text: return
    execute_pip_with_requirements(
        context, context_options, 'uninstall', requirements_text,
        pip_options = ( '--yes', ) )


def execute_pip_with_requirements(
    context, context_options, command, requirements, pip_options = None
):
    ''' Executes a Pip command with requirements.

        (This task requires Internet access and may take some time. '''
    pip_options = pip_options or ( )
    # Unfortunately, Pip does not support reading requirements from stdin,
    # as of 2022-01-02. To workaround, we need to write and then read
    # a temporary file. More details: https://github.com/pypa/pip/issues/7822
    with NamedTemporaryFile( mode = 'w+' ) as requirements_file:
        requirements_file.write( requirements )
        requirements_file.flush( )
        context.run(
            "pip {command} {options} --requirement {requirements_file}".format(
                command = command,
                options = ' '.join( pip_options ),
                requirements_file = shell_quote( requirements_file.name ) ),
            pty = on_tty, **context_options )



@task( pre = ( clean_pythons_packages, clean_pycaches, clean_tool_caches, ) )
def clean( context ): # pylint: disable=unused-argument
    ''' Cleans all caches. '''


@task
def check_python_packages_security( context, version = None ):
    ''' Checks for security issues in utilized packages and tools.

        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Lint: Package Security', supplement = version )
    context_options = derive_venv_context_options( version = version )
    context.run( f"safety check", pty = on_tty, **context_options )


@task
def freshen_asdf( context ):
    ''' Asks Asdf to update itself.

        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Freshen: Version Manager' )
    context.run( 'asdf update', pty = on_tty )
    context.run( 'asdf plugin update python', pty = on_tty )


@task( pre = ( freshen_asdf, ) )
def freshen_pythons( context ):
    ''' Updates each supported Python minor version to latest patch.

        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Freshen: Python Versions' )
    minors_regex = re.compile(
        r'''^(?P<prefix>\w+(?:\d+\.\d+)?-)?(?P<minor>\d+\.\d+)\..*$''' )
    latest_versions = [ ]
    for version in indicate_python_versions_support( ):
        groups = minors_regex.match( version ).groupdict( )
        minor_version = "{prefix}{minor}".format(
            prefix = groups.get( 'prefix' ) or '',
            minor = groups[ 'minor' ] )
        latest_version = context.run(
            f"asdf latest python {minor_version}",
            hide = 'stdout' ).stdout.strip( )
        context.run( f"asdf install python {latest_version}", pty = True )
        latest_versions.append( latest_version )
    # Can only update local versions after they are installed.
    context.run( "asdf local python {versions}".format(
        versions = ' '.join( latest_versions ) ), pty = True )


@task
def freshen_pythons_packages( context ):
    ''' Updates Python packages in all virtual environments. '''
    for version in indicate_python_versions_support( ):
        freshen_python_packages( context, version )


@task
def freshen_python_packages( context, version = None ):
    ''' Updates Python packages in virtual environment. '''
    render_boxed_title(
        'Freshen: Python Package Versions', supplement = version )
    context_options = derive_venv_context_options( version = version )
    identifier = identify_python(
        'pep508-environment',
        python_path = which(
            'python', path = context_options[ 'env' ][ 'PATH' ] ) )
    install_python_packages( context, context_options )
    fixtures = calculate_python_packages_fixtures( context_options )
    record_python_packages_fixtures( identifier, fixtures )
    check_python_packages_security( context, version = version )
    test( context, version = version )


def calculate_python_packages_fixtures( context_options ):
    ''' Calculates Python package fixtures, such as digests or URLs. '''
    fixtures = [ ]
    for entry in indicate_current_python_packages( context_options ):
        requirement = entry.requirement
        fixture = dict( name = requirement.name )
        if 'editable' in entry.flags: continue
        if requirement.url: fixture.update( dict( url = requirement.url, ) )
        else:
            package_version = next( iter( requirement.specifier ) ).version
            fixture.update( dict(
                version = package_version,
                digests = tuple( map(
                    lambda s: f"sha256:{s}",
                    aggregate_pypi_release_digests(
                        requirement.name, package_version )
                ) )
            ) )
        fixtures.append( fixture )
    return fixtures


def install_python_packages( context, context_options, identifier = None ):
    ''' Installs required Python packages into virtual environment. '''
    raw, frozen, unpublished = generate_pip_requirements_text(
        identifier = identifier )
    context.run(
        'pip install --upgrade setuptools pip wheel',
        pty = on_tty, **context_options )
    if not identifier or not frozen:
        pip_options = [ ]
        if not identifier: pip_options.append( '--upgrade' )
        execute_pip_with_requirements(
            context, context_options, 'install', raw,
            pip_options = pip_options )
    else:
        pip_options = [ '--require-hashes' ]
        execute_pip_with_requirements(
            context, context_options, 'install', frozen,
            pip_options = pip_options )
    if unpublished:
        execute_pip_with_requirements(
            context, context_options, 'install', unpublished )
    # Pip cannot currently mix editable and digest-bound requirements,
    # so we must install editable packages separately. (As of 2022-02-06.)
    # https://github.com/pypa/pip/issues/4995
    context.run( 'pip install --editable .', pty = on_tty, **context_options )


def indicate_current_python_packages( context_options ):
    ''' Returns currently-installed Python packages. '''
    ensure_python_package( 'packaging' )
    from packaging.requirements import Requirement
    entries = [ ]
    for line in standard_execute_external(
        split_command( 'pip freeze' ), env = context_options[ 'env' ]
    ).stdout.strip( ).splitlines( ):
        entry = SimpleNamespace( flags = [ ] )
        if line.startswith( '-e' ):
            entry.flags.append( 'editable' )
            # Replace '-e' with '{package_name}@'.
            line = ' '.join( (
                line.rsplit( '=', maxsplit = 1 )[ -1 ] + '@',
                line.split( ' ', maxsplit = 1 )[ 1 ]
            ) )
        entry.requirement = Requirement( line )
        entries.append( entry )
    return entries


pypi_release_digests_cache = { }
def aggregate_pypi_release_digests( name, version, index_url = '' ):
    ''' Aggregates hashes for release on PyPI. '''
    cache_index = ( index_url, name, version )
    digests = pypi_release_digests_cache.get( cache_index )
    if digests: return digests
    release_info = retrieve_pypi_release_information(
        name, version, index_url = index_url )
    digests = [
        package_info[ 'digests' ][ 'sha256' ]
        for package_info in release_info ]
    pypi_release_digests_cache[ cache_index ] = digests
    return digests


def record_python_packages_fixtures( identifier, fixtures ):
    ''' Records table of Python packages fixtures. '''
    ensure_python_package( 'tomli' )
    from tomli import load
    ensure_python_package( 'tomli-w' )
    from tomli_w import dump
    fixtures_path = paths.configuration.pypackages_fixtures
    if fixtures_path.exists( ):
        with fixtures_path.open( 'rb' ) as file: document = load( file )
    else: document = { }
    document[ identifier ] = fixtures
    with fixtures_path.open( 'wb' ) as file: dump( document, file )


@task
def freshen_git_modules( context ):
    ''' Performs recursive update of all Git modules.

        Initializes SCM modules as needed.
        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Freshen: SCM Modules' )
    context.run(
        'git submodule update --init --recursive --remote', pty = True )


@task
def freshen_git_hooks( context ):
    ''' Updates Git hooks to latest tagged release.

        This task requires Internet access and may take some time. '''
    render_boxed_title( 'Freshen: SCM Hooks' )
    context.run(
        f"pre-commit autoupdate --config {paths.configuration.pre_commit}",
        pty = True, **derive_venv_context_options( ) )


@task(
    pre = (
        clean,
        freshen_pythons, freshen_pythons_packages,
        freshen_git_modules, freshen_git_hooks,
    )
)
def freshen( context ): # pylint: disable=unused-argument
    ''' Performs the various freshening tasks, cleaning first.

        This task requires Internet access and may take some time. '''


@task
def lint_bandit( context ):
    ''' Security checks the source code with Bandit. '''
    render_boxed_title( 'Lint: Bandit' )
    context.run(
        f"bandit --recursive --verbose {paths.sources.p.python3}",
        pty = True, **derive_venv_context_options( ) )


@task( iterable = ( 'packages', 'modules', 'files', ) )
def lint_mypy( context, packages, modules, files ):
    ''' Lints the source code with Mypy. '''
    render_boxed_title( 'Lint: MyPy' )
    context_options = derive_venv_context_options( )
    if not which( 'mypy', path = context_options[ 'env' ][ 'PATH' ] ):
        eprint( 'Mypy not available on this platform. Skipping.' )
        return
    environment_str = f"MYPYPATH={paths.project}:{paths.sources.p.python3}"
    configuration_str = f"--config-file {paths.configuration.mypy}"
    if not packages and not modules and not files: packages = ( project_name, )
    packages_str = ' '.join( map(
        lambda package: f"--package {package}", packages ) )
    modules_str = ' '.join( map(
        lambda module: f"--module {module}", modules ) )
    files_str = ' '.join( map( str, files ) )
    context.run(
        f"{environment_str} "
        f"mypy {configuration_str} "
        f"{packages_str} {modules_str} {files_str}",
        pty = True, **context_options )


@task( iterable = ( 'targets', 'checks', ) )
def lint_pylint( context, targets, checks ):
    ''' Lints the source code with Pylint. '''
    render_boxed_title( 'Lint: Pylint' )
    context_options = derive_venv_context_options( )
    if not which( 'pylint', path = context_options[ 'env' ][ 'PATH' ] ):
        eprint( 'Pylint not available on this platform. Skipping.' )
        return
    reports_str = '--reports=no --score=no' if targets or checks else ''
    if not targets:
        targets = (
            project_name,
            *paths.tests.p.python3.rglob( '*.py' ),
            *paths.sources.d.python3.rglob( '*.py' ),
            paths.sources.p.sphinx / 'conf.py',
            __package__, )
    targets_str = ' '.join( map( str, targets ) )
    checks_str = (
        "--disable=all --enable={}".format( ','.join( checks ) )
        if checks else '' )
    context.run(
        f"pylint {reports_str} {checks_str} {targets_str}",
        pty = True, **context_options )


@task
def lint_semgrep( context ):
    ''' Lints the source code with Semgrep. '''
    render_boxed_title( 'Lint: Semgrep' )
    context_options = derive_venv_context_options( )
    if not which( 'semgrep', path = context_options[ 'env' ][ 'PATH' ] ):
        eprint( 'Semgrep not available on this platform. Skipping.' )
        return
    sgconfig_path = paths.scm_modules / 'semgrep-rules' / 'python' / 'lang'
    context.run(
        f"semgrep --config {sgconfig_path} --use-git-ignore "
        f"{paths.sources.p.python3}", pty = on_tty, **context_options )


@task( pre = (
    call( lint_pylint, targets = ( ), checks = ( ) ),
    call( lint_semgrep ),
    call( lint_mypy, packages = ( ), modules = ( ), files = ( ) ),
    call( lint_bandit ),
) )
def lint( context ): # pylint: disable=unused-argument
    ''' Lints the source code. '''


@task
def report_coverage( context ):
    ''' Combines multiple code coverage results into a single report. '''
    render_boxed_title( 'Artifact: Code Coverage Report' )
    context_options = derive_venv_context_options( )
    context.run( 'coverage combine', pty = True, **context_options )
    context.run( 'coverage report', pty = True, **context_options )
    context.run( 'coverage html', pty = True, **context_options )
    context.run( 'coverage xml', pty = True, **context_options )


@task( pre = ( lint, ) )
def test( context, version = None ):
    ''' Runs the test suite with current or specified Python version. '''
    render_boxed_title( 'Test: Unit + Code Coverage', supplement = version )
    context_options = derive_venv_context_options( version = version )
    context_options[ 'env' ].update( dict(
        HYPOTHESIS_STORAGE_DIRECTORY = paths.caches.hypothesis,
    ) )
    context.run(
        f"coverage run --source {project_name}",
        pty = True, **context_options )


@task( pre = ( lint, ), post = ( report_coverage, ) )
def test_all_versions( context ):
    ''' Runs the test suite across multiple, isolated Python versions. '''
    for version in indicate_python_versions_support( ):
        test( context, version )


@task
def check_urls( context ):
    ''' Checks the HTTP URLs in the documentation for liveness. '''
    render_boxed_title( 'Test: Documentation URLs' )
    context.run(
        f"sphinx-build -b linkcheck {sphinx_options} "
        f"{paths.sources.p.sphinx} {paths.artifacts.sphinx_linkcheck}",
        pty = on_tty, **derive_venv_context_options( ) )


@task
def check_readme( context ):
    ''' Checks that the README will render correctly on PyPI. '''
    render_boxed_title( 'Test: README Render' )
    path = _get_sdist_path( )
    context.run(
        f"twine check {path}", pty = on_tty, **derive_venv_context_options( ) )


@task( pre = ( test, check_urls, ), post = ( check_readme, ) )
def make_sdist( context ):
    ''' Packages the Python sources for release. '''
    render_boxed_title( 'Artifact: Source Distribution' )
    assert_gpg_tty( )
    path = _get_sdist_path( )
    # https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html
    context.run(
        f"python3 setup.py {setuptools_build_command} "
            f"sdist --dist-dir {paths.artifacts.sdists}",
        **derive_venv_context_options( ) )
    context.run( f"gpg --detach-sign --armor {path}", pty = True )


def _get_sdist_path( ):
    project_version = discover_project_version( )
    name = f"{project_name}-{project_version}.tar.gz"
    return paths.artifacts.sdists / name


@task( pre = ( make_sdist, ) )
def make_wheel( context ):
    ''' Packages a Python wheel for release. '''
    render_boxed_title( 'Artifact: Python Wheel' )
    assert_gpg_tty( )
    path = _get_wheel_path( )
    # https://blog.ganssle.io/articles/2021/10/setup-py-deprecated.html
    context.run(
        f"python3 setup.py {setuptools_build_command} "
            f"bdist_wheel --dist-dir {paths.artifacts.wheels}",
        **derive_venv_context_options( ) )
    context.run( f"gpg --detach-sign --armor {path}", pty = True )


def _get_wheel_path( ):
    project_version = discover_project_version( )
    name = f"{project_name}-{project_version}-py3-none-any.whl"
    return paths.artifacts.wheels / name


@task( pre = ( check_urls, ) )
def make_html( context ):
    ''' Generates documentation as HTML artifacts. '''
    render_boxed_title( 'Artifact: Documentation' )
    unlink_recursively( paths.artifacts.sphinx_html )
    context.run(
        f"sphinx-build -b html {sphinx_options} "
        f"{paths.sources.p.sphinx} {paths.artifacts.sphinx_html}",
        pty = on_tty, **derive_venv_context_options( ) )


@task( pre = ( clean, make_wheel, make_html, ) )
def make( context ): # pylint: disable=unused-argument
    ''' Generates all of the artifacts. '''


class Version:
    ''' Package version manager.

        Compatible with the version scheme laid forth in
        `PEP 440 <https://www.python.org/dev/peps/pep-0440/#version-scheme>`_.

        Core Format: ``{{major}}.{{minor}}``
        Release amendments extend the core format by appending
        ``.{{amendment}}``.
        Development prereleases extend the core format by appending
        ``a{{timestamp:yyyymmddHHMM}}``.
        Release candidates extend the core format by appending
        ``rc{{candidate}}``, where ``candidate`` starts at ``1`` and increases
        by one upon each increment.
    '''

    @classmethod
    def from_string( kind, version ):
        ''' Constructs a version object by parsing it from a string. '''
        from re import match
        matched = match(
            r"(?P<major>\d+)\.(?P<minor>\d+)"
            r"(?:\.(?P<patch>\d+)"
            r"|(?P<stage>a|rc)(?:"
            r"(?:(?<=a)(?P<ts>\d{12}))|(?:(?<=rc)(?P<rc>\d+))"
            r"))", version )
        stage = matched.group( 'stage' ) or 'f'
        patch = (
            matched.group( 'ts' ) if 'a' == stage
            else (
                matched.group( 'rc' ) if 'rc' == stage
                else matched.group( 'patch' ) ) )
        return kind(
            stage, matched.group( 'major' ), matched.group( 'minor' ), patch )

    def __init__( self, stage, major, minor, patch ):
        if stage not in ( 'a', 'rc', 'f' ):
            raise Exit( f"Bad stage: {stage}" )
        self.stage = stage
        self.major = int( major )
        self.minor = int( minor )
        self.patch = int( patch )

    def __str__( self ):
        stage, patch = self.stage, self.patch
        return ''.join( filter( None, (
            f"{self.major}", f".{self.minor}",
            f".{patch}" if 'f' == stage else '',
            f"{stage}{patch}" if stage in ( 'a', 'rc' ) else '' ) ) )

    def as_bumped( self, piece ):
        ''' Returns a derivative of the version,
            altered according to current state and desired modification.
        '''
        from datetime import datetime as DateTime
        Version_ = type( self )
        stage, major, minor, patch = (
            self.stage, self.major, self.minor, self.patch )
        if 'stage' == piece:
            if 'a' == stage: return Version_( 'rc', major, minor, 1 )
            if 'rc' == stage: return Version_( 'f', major, minor, 0 )
            raise Exit( 'Cannot bump last stage.' )
        timestamp = DateTime.utcnow( ).strftime( '%Y%m%d%H%M' )
        if 'patch' == piece:
            if 'a' == stage:
                return Version_( 'a', major, minor, timestamp )
            return Version_( stage, major, minor, patch + 1 )
        if 'major' == piece:
            return Version_( 'a', major + 1, 0, timestamp )
        if 'minor' == piece:
            return Version_( 'a', major, minor + 1, timestamp )
        raise Exit( f"Unknown kind of piece: {piece}" )


def _ensure_clean_workspace( context ):
    ''' Error if version control reports any dirty or untracked files. '''
    result = context.run( 'git status --short', pty = True )
    if result.stdout or result.stderr:
        raise Exit( 'Dirty workspace. Please stash or commit changes.' )


@task
def bump( context, piece ):
    ''' Bumps a piece of the current version. '''
    render_boxed_title( f"Version: Adjust" )
    _ensure_clean_workspace( context )
    assert_gpg_tty( )
    project_version = discover_project_version( )
    current_version = Version.from_string( project_version )
    new_version = current_version.as_bumped( piece )
    if 'stage' == piece: part = 'release_class'
    elif 'patch' == piece:
        if current_version.stage in ( 'a', 'rc' ): part = 'prerelease'
        else: part = 'patch'
    else: part = piece
    context.run(
        f"bumpversion --config-file={paths.configuration.bumpversion}"
        f" --current-version {current_version}"
        f" --new-version {new_version}"
        f" {part}", pty = True, **derive_venv_context_options( ) )


@task( post = ( call( bump, piece = 'patch' ), ) )
def bump_patch( context ): # pylint: disable=unused-argument
    ''' Bumps to next patch level. '''


@task( post = ( call( bump, piece = 'stage' ), ) )
def bump_stage( context ): # pylint: disable=unused-argument
    ''' Bumps to next release stage. '''


@task( post = ( bump_stage, ) )
def branch_release( context, remote = 'origin' ):
    ''' Makes a new branch for development torwards a release. '''
    _ensure_clean_workspace( context )
    project_version = discover_project_version( )
    mainline_regex = re.compile(
        r'''^\s+HEAD branch:\s+(.*)$''', re.MULTILINE )
    mainline_branch = mainline_regex.search( context.run(
        f"git remote show {remote}", hide = 'stdout' ).stdout.strip( ) )[ 1 ]
    true_branch = context.run(
        'git branch --show-current', hide = 'stdout' ).stdout.strip( )
    if mainline_branch != true_branch:
        raise Exit( f"Cannot create release from branch: {true_branch}" )
    this_version = Version.from_string( project_version )
    stage = this_version.stage
    if 'a' != stage: raise Exit( f"Cannot create release from stage: {stage}" )
    target_branch = f"release-{this_version.major}.{this_version.minor}"
    context.run( f"git checkout -b {target_branch}", pty = True )


@task
def check_code_style( context, write_changes = False ):
    ''' Checks code style of new changes. '''
    yapf_options = [ ]
    if write_changes: yapf_options.append( '--in-place --verbose' )
    yapf_options_string = ' '.join( yapf_options )
    context.run(
        f"git diff --unified=0 --no-color -- {paths.sources.p.python3} "
        f"| yapf-diff {yapf_options_string}",
        pty = on_tty, **derive_venv_context_options( ) )


@task( pre = ( test, ) )
def push( context, remote = 'origin' ):
    ''' Pushes commits on current branch, plus all tags. '''
    render_boxed_title( 'SCM: Push Branch with Tags' )
    _ensure_clean_workspace( context )
    project_version = discover_project_version( )
    true_branch = context.run(
        'git branch --show-current', hide = 'stdout' ).stdout.strip( )
    this_version = Version.from_string( project_version )
    target_branch = f"release-{this_version.major}.{this_version.minor}"
    if true_branch == target_branch:
        context.run(
            f"git push --set-upstream {remote} {true_branch}", pty = True )
    else: context.run( 'git push', pty = True )
    context.run( 'git push --tags', pty = True )


@task
def check_pip_install( context, index_url = '', version = None ):
    ''' Checks import of current package after installation via Pip. '''
    version = version or discover_project_version( )
    render_boxed_title( f"Verify: Python Package Installation ({version})" )
    with TemporaryDirectory( ) as venv_path:
        venv_path = Path( venv_path )
        create_venv( venv_path, clear = True, with_pip = True )
        index_url_option = ''
        if index_url: index_url_option = f"--index-url {index_url}"
        context_options = derive_venv_context_options( venv_path )
        attempts_count_max = 2
        for attempts_count in range( attempts_count_max + 1 ):
            try:
                context.run(
                    f"pip install {index_url_option} "
                    f"  {project_name}=={version}",
                    pty = on_tty, **context_options )
            except Failure:
                if attempts_count_max == attempts_count: raise
                sleep( 2 ** attempts_count )
            else: break
        python_import_command = (
            f"import {project_name}; "
            f"print( {project_name}.__version__ )" )
        context.run(
            f"python -c '{python_import_command}'",
            pty = True, **context_options )


@task
def check_pypi_integrity( context, version = None, index_url = '' ):
    ''' Checks integrity of project packages on PyPI.
        If no version is provided, the current project version is used.

        This task requires Internet access and may take some time. '''
    version = version or discover_project_version( )
    render_boxed_title( f"Verify: Python Package Integrity ({version})" )
    release_info = retrieve_pypi_release_information(
        project_name, version, index_url = index_url )
    for package_info in release_info:
        url = package_info[ 'url' ]
        if not package_info.get( 'has_sig', False ):
            raise Exit( f"No signature found for: {url}" )
        check_pypi_package( context, url )


def retrieve_pypi_release_information( name, version, index_url = '' ): # pylint: disable=inconsistent-return-statements
    ''' Retrieves information about specific release on PyPI. '''
    index_url = index_url or 'https://pypi.org'
    # https://warehouse.pypa.io/api-reference/json.html#release
    request = HttpRequest(
        f"{index_url}/pypi/{name}/json",
        headers = { 'Accept': 'application/json', } )
    attempts_count_max = 2
    for attempts_count in range( attempts_count_max + 1 ):
        try:
            with urlopen( request ) as http_reader:
                return load_json( http_reader )[ 'releases' ][ version ]
        except ( KeyError, UrlError, ):
            if attempts_count_max == attempts_count: raise
            sleep( 2 ** attempts_count )


def check_pypi_package( context, package_url ):
    ''' Verifies signature on package. '''
    assert_gpg_tty( )
    package_filename = urlparse( package_url ).path.split( '/' )[ -1 ]
    with TemporaryDirectory( ) as cache_path_raw:
        cache_path = Path( cache_path_raw )
        package_path = cache_path / package_filename
        signature_path = cache_path / f"{package_filename}.asc"
        attempts_count_max = 2
        for attempts_count in range( attempts_count_max + 1 ):
            try:
                with urlopen( package_url ) as http_reader:
                    with package_path.open( 'wb' ) as file:
                        file.write( http_reader.read( ) )
                with urlopen( f"{package_url}.asc" ) as http_reader:
                    with signature_path.open( 'wb' ) as file:
                        file.write( http_reader.read( ) )
            except UrlError:
                if attempts_count_max == attempts_count: raise
                sleep( 2 ** attempts_count )
            else: break
        context.run( f"gpg --verify {signature_path}" )


@task(
    pre = ( make, ),
    post = (
        call( check_pypi_integrity, index_url = 'https://test.pypi.org' ),
        call( check_pip_install, index_url = 'https://test.pypi.org/simple/' ),
    )
)
def upload_test_pypi( context ):
    ''' Publishes current sdist and wheels to Test PyPI. '''
    _upload_pypi( context, 'testpypi' )


@task(
    pre = ( upload_test_pypi, test_all_versions, ),
    post = ( check_pypi_integrity, check_pip_install, )
)
def upload_pypi( context ):
    ''' Publishes current sdist and wheels to PyPI. '''
    _upload_pypi( context )


def _upload_pypi( context, repository_name = '' ):
    repository_option = ''
    task_name_suffix = ''
    if repository_name:
        repository_option = f"--repository {repository_name}"
        task_name_suffix = f" ({repository_name})"
    render_boxed_title( f"Publication: PyPI{task_name_suffix}" )
    artifacts = _get_pypi_artifacts( )
    context_options = derive_venv_context_options( )
    context_options.update( _get_pypi_credentials( repository_name ) )
    context.run(
        f"twine upload --skip-existing --verbose {repository_option} "
        f"{artifacts}", pty = True, **context_options )


def _get_pypi_artifacts( ):
    stems = ( _get_sdist_path( ), _get_wheel_path( ), )
    return ' '.join( chain(
        map( str, stems ), map( lambda p: f"{p}.asc", stems ) ) )


def _get_pypi_credentials( repository_name ):
    from tomli import load as load_toml
    if '' == repository_name: repository_name = 'pypi'
    with open( paths.project / 'credentials.toml', 'rb' ) as file:
        table = load_toml( file )[ repository_name ]
    return {
        'TWINE_USERNAME': table[ 'username' ],
        'TWINE_PASSWORD': table[ 'password' ], }


# Inspiration: https://stackoverflow.com/a/58993849/14833542
@task( pre = ( test, make_html, ) )
def upload_github_pages( context ):
    ''' Publishes Sphinx HTML output to Github Pages for project. '''
    render_boxed_title( 'Publication: Github Pages' )
    # Use relative path, since 'git subtree' needs it.
    html_path = paths.artifacts.sphinx_html.relative_to( paths.project )
    nojekyll_path = html_path / '.nojekyll'
    target_branch = 'documentation'
    with CMStack( ) as cm_stack:
        # Work from project root, since 'git subtree' requires relative paths.
        cm_stack.enter_context( context.cd( paths.project ) )
        saved_branch = context.run(
            'git branch --show-current', hide = 'stdout' ).stdout.strip( )
        context.run( f"git branch -D local-{target_branch}", warn = True )
        context.run( f"git checkout -b local-{target_branch}", pty = True )
        def restore( *exc_info ): # pylint: disable=unused-argument
            context.run( f"git checkout {saved_branch}", pty = True )
        cm_stack.push( restore )
        nojekyll_path.touch( exist_ok = True )
        # Override .gitignore to pickup artifacts.
        context.run( f"git add --force {html_path}", pty = True )
        context.run( 'git commit -m "Update documentation."', pty = True )
        subtree_id = context.run(
            f"git subtree split --prefix {html_path}",
            hide = 'stdout' ).stdout.strip( )
        context.run(
            f"git push --force origin {subtree_id}:refs/heads/{target_branch}",
            pty = True )


@task( pre = ( bump_patch, push, upload_pypi, ) )
def release_new_patch( context ): # pylint: disable=unused-argument
    ''' Unleashes a new patch upon the world. '''


@task( pre = ( bump_stage, push, upload_pypi, ) )
def release_new_stage( context ): # pylint: disable=unused-argument
    ''' Unleashes a new stage upon the world. '''


@task
def run( context, command, version = None ):
    ''' Runs command in virtual environment. '''
    context.run(
        command,
        pty = on_tty, **derive_venv_context_options( version = version ) )
