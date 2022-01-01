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


from contextlib import ExitStack as CMStack
from itertools import chain
from json import load as json_load
from os import environ as psenv
from pathlib import Path
import re
from shutil import which
from sys import stderr
from tempfile import TemporaryDirectory
from time import sleep
from urllib.error import URLError as UrlError
from urllib.parse import urlparse
from urllib.request import ( Request as HttpRequest, urlopen, )
from venv import create as create_venv

from invoke import Context, Exit, Failure, call, task

from .base import (
    derive_python_venv_execution_options,
    derive_python_venv_path,
    detect_vmgr_python_path,
    ensure_directory,
    eprint, epprint,
    indicate_python_versions_support,
    paths,
)


# https://www.sphinx-doc.org/en/master/man/sphinx-build.html
sphinx_options = f"-j auto -d {paths.sphinx.caches} -n -T"


def parse_project_name( ):
    ''' Returns project name, as parsed from configuration. '''
    return parse_project_information( )[ 'name' ]

def parse_project_version( ):
    ''' Returns project version, as parsed from configuration. '''
    return parse_project_information( )[ 'version' ]

def parse_project_information( ):
    ''' Returns project information, as parsed from configuration. '''
    path = paths.project / 'setup.cfg'
    if path.is_file( ):
        from configparser import ConfigParser
        config = ConfigParser( )
        config.read( path )
        return config[ 'metadata' ]
    # TODO: Look in 'pyproject.toml' if PEP 621 is implemented for setuptools.
    #       https://www.python.org/dev/peps/pep-0621/
    raise Exception( 'Cannot find suitable source of project metadata.' )

project_name = parse_project_name( )


def _assert_gpg_tty( ):
    if 'GPG_TTY' not in psenv:
        raise Exit(
            "ERROR: Environment variable 'GPG_TTY' is not set. "
            "Task cannot prompt for GPG secret key passphrase." )


# TODO? Replace with 'shutil.rmtree'.
def _unlink_recursively( path ):
    ''' Pure Python implementation of ``rm -rf``, essentially. '''
    if not path.exists( ): return
    if not path.is_dir( ):
        path.unlink( )
        return
    dirs_stack = [ ]
    for child_path in path.rglob( '*' ):
        if child_path.is_dir( ) and not child_path.is_symlink( ):
            dirs_stack.append( child_path )
            continue
        child_path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )
    path.rmdir( )


def _render_boxed_title( title ):
    ''' Renders box around title. '''
    columns_count = int( psenv.get( 'COLUMNS', 79 ) )
    icolumns_count = columns_count - 2
    content_template = (
        '\N{BOX DRAWINGS DOUBLE VERTICAL}{fill}'
        '\N{BOX DRAWINGS DOUBLE VERTICAL}' )
    return '\n'.join( (
        '',
        '\N{BOX DRAWINGS DOUBLE DOWN AND RIGHT}{fill}'
        '\N{BOX DRAWINGS DOUBLE DOWN AND LEFT}'.format(
            fill = '\N{BOX DRAWINGS DOUBLE HORIZONTAL}' * icolumns_count ),
        content_template.format( fill = ' ' * icolumns_count ),
        content_template.format( fill = title.center( icolumns_count ) ),
        content_template.format( fill = ' ' * icolumns_count ),
        '\N{BOX DRAWINGS DOUBLE UP AND RIGHT}{fill}'
        '\N{BOX DRAWINGS DOUBLE UP AND LEFT}'.format(
            fill = '\N{BOX DRAWINGS DOUBLE HORIZONTAL}' * icolumns_count ),
        '', ) )


@task
def install_git_hooks( context ):
    ''' Installs hooks to check goodness of code changes before commit. '''
    eprint( _render_boxed_title( 'Install: Git Pre-Commit Hooks' ) )
    my_cfg_path = paths.configuration / 'pre-commit.yaml'
    context.run(
        f"pre-commit install --config {my_cfg_path} --install-hooks",
        pty = True )


@task
def install_pythons( context ):
    ''' Installs each supported Python version.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Install: Python Releases' ) )
    context.run( 'asdf install python', pty = True )


@task
def build_python_venvs( context ):
    ''' Creates virtual environment for each supported Python version. '''
    for version in indicate_python_versions_support( ):
        build_python_venv( context, version )


@task
def build_python_venv( context, version, overwrite = False ):
    ''' Creates virtual environment for requested Python version. '''
    eprint( _render_boxed_title(
        f"Build: Python Virtual Environment ({version})" ) )
    python_path = detect_vmgr_python_path( context, version )
    venv_path = ensure_directory( derive_python_venv_path(
        context, version, python_path ) )
    venv_options = [ ]
    if overwrite: venv_options.append( '--clear' )
    venv_options_str = ' '.join( venv_options )
    context.run(
        f"{python_path} -m venv {venv_options_str} {venv_path}", pty = True )
    options = derive_python_venv_execution_options( context, venv_path )
    context.run(
        'pip install --upgrade setuptools pip wheel', pty = True, **options )
    # TODO: Install packages into virtual environment.


@task( pre = ( install_pythons, install_git_hooks, ) )
def bootstrap( context ): # pylint: disable=unused-argument
    ''' Bootstraps the development environment and utilities. '''


@task
def clean_pycaches( context ): # pylint: disable=unused-argument
    ''' Removes all caches of compiled CPython bytecode. '''
    eprint( _render_boxed_title( 'Clean: Python Caches' ) )
    anchors = ( paths.python3.sources, paths.python3.tests, )
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
    eprint( _render_boxed_title( 'Clean: Tool Caches' ) )
    # TODO? Simplify by using a single .gitignore in paths.caches.
    anchors = paths.caches.glob( '*' )
    gitignore_paths = set( paths.caches.glob( '*/.gitignore' ) )
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
    # Note: 'setuptools' hardcodes this path.
    _unlink_recursively( paths.project / '.eggs' )


@task
def clean_pipenv( context ):
    ''' Removes unused packages in the Python development virtualenv. '''
    eprint( _render_boxed_title( 'Clean: Orphan Packages' ) )
    context.run( 'pipenv clean', pty = True )


@task( pre = ( clean_pycaches, clean_tool_caches, clean_pipenv, ) )
def clean( context ): # pylint: disable=unused-argument
    ''' Cleans all caches. '''


@task
def check_pipenv_security( context ):
    ''' Checks for security issues in utilized packages and tools.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Lint: Package Security' ) )
    context.run( 'pipenv check', pty = True )


@task
def freshen_asdf( context ):
    ''' Asks Asdf to update itself.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Freshen: Version Manager' ) )
    context.run( 'asdf update', pty = stderr.isatty( ) )
    context.run( 'asdf plugin update python', pty = stderr.isatty( ) )


@task( pre = ( freshen_asdf, ) )
def freshen_pythons( context ):
    ''' Updates each supported Python minor version to latest patch.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Freshen: Python Versions' ) )
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


@task( post = ( clean_pipenv, check_pipenv_security, ) )
def freshen_pipenv( context ):
    ''' Updates packages for the Python development virtualenv.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Freshen: Development Dependencies' ) )
    context.run( 'pipenv update --dev', pty = stderr.isatty( ) )


@task
def freshen_git_modules( context ):
    ''' Performs recursive update of all Git modules.

        Initializes SCM modules as needed.
        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Freshen: SCM Modules' ) )
    context.run(
        'git submodule update --init --recursive --remote', pty = True )


@task
def freshen_git_hooks( context ):
    ''' Updates Git hooks to latest tagged release.

        This task requires Internet access and may take some time. '''
    eprint( _render_boxed_title( 'Freshen: SCM Hooks' ) )
    my_cfg_path = paths.configuration / 'pre-commit.yaml'
    context.run( f"pre-commit autoupdate --config {my_cfg_path}", pty = True )


@task(
    pre = (
        clean,
        freshen_pythons, freshen_pipenv,
        freshen_git_modules, freshen_git_hooks,
    )
)
def freshen( context ): # pylint: disable=unused-argument
    ''' Performs the various freshening tasks, cleaning first.

        This task requires Internet access and may take some time. '''


@task
def lint_bandit( context ):
    ''' Security checks the source code with Bandit. '''
    eprint( _render_boxed_title( 'Lint: Bandit' ) )
    context.run( f"bandit --recursive --verbose {paths.python3.sources}" )


@task( iterable = ( 'packages', 'modules', 'files', ) )
def lint_mypy( context, packages, modules, files ):
    ''' Lints the source code with Mypy. '''
    eprint( _render_boxed_title( 'Lint: MyPy' ) )
    if not which( 'mypy' ):
        eprint( 'Mypy not available on this platform. Skipping.' )
        return
    environment_str = f"MYPYPATH={paths.project}:{paths.python3.sources}"
    configuration_str = "--config-file {}".format(
        paths.configuration / 'mypy.ini' )
    if not packages and not modules and not files: packages = ( project_name, )
    packages_str = ' '.join( map(
        lambda package: f"--package {package}", packages ) )
    modules_str = ' '.join( map(
        lambda module: f"--module {module}", modules ) )
    files_str = ' '.join( map( str, files ) )
    context.run(
        f"{environment_str} "
        f"mypy {configuration_str} "
        f"{packages_str} {modules_str} {files_str}", pty = True )


@task( iterable = ( 'targets', 'checks', ) )
def lint_pylint( context, targets, checks ):
    ''' Lints the source code with Pylint. '''
    eprint( _render_boxed_title( 'Lint: Pylint' ) )
    if not which( 'pylint' ):
        eprint( 'Pylint not available on this platform. Skipping.' )
        return
    reports_str = '--reports=no --score=no' if targets or checks else ''
    if not targets:
        targets = (
            project_name,
            *paths.python3.tests.rglob( '*.py' ),
            paths.sphinx.sources / 'conf.py',
            __package__, )
    targets_str = ' '.join( map( str, targets ) )
    checks_str = (
        "--disable=all --enable={}".format( ','.join( checks ) )
        if checks else '' )
    context.run(
        f"pylint {reports_str} {checks_str} {targets_str}", pty = True )


@task
def lint_semgrep( context ):
    ''' Lints the source code with Semgrep. '''
    eprint( _render_boxed_title( 'Lint: Semgrep' ) )
    sgconfig_path = (
        paths.scm_modules / 'semgrep-rules' / 'python' / 'lang' )
    context.run(
        f"semgrep --config {sgconfig_path} --use-git-ignore "
        f"{paths.python3.sources}", pty = stderr.isatty( ) )


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
    eprint( _render_boxed_title( 'Artifact: Code Coverage Report' ) )
    context.run( 'coverage combine', pty = True )
    context.run( 'coverage report', pty = True )
    context.run( 'coverage html', pty = True )
    context.run( 'coverage xml', pty = True )


@task( pre = ( lint, ) )
def test( context ):
    ''' Runs the test suite with the current Python version. '''
    eprint( _render_boxed_title( 'Test: Unit + Code Coverage' ) )
    context.run(
        f"coverage run --source {project_name}", pty = True,
        env = dict(
            HYPOTHESIS_STORAGE_DIRECTORY = paths.caches / 'hypothesis', ) )


@task( pre = ( lint, ), post = ( report_coverage, ) )
def test_all_versions( context ):
    ''' Runs the test suite across multiple, isolated Python versions. '''
    eprint( _render_boxed_title( 'Test: Unit + Code Coverage (all Pythons)' ) )
    context.run(
        'tox --asdf-no-fallback --asdf-install', pty = True,
        env = dict(
            HYPOTHESIS_STORAGE_DIRECTORY = paths.caches / 'hypothesis',
            _PROJECT_NAME = f"{project_name}" ) )


@task
def check_urls( context ):
    ''' Checks the HTTP URLs in the documentation for liveness. '''
    eprint( _render_boxed_title( 'Test: Documentation URLs' ) )
    output_path = paths.artifacts / 'sphinx-linkcheck'
    context.run(
        f"sphinx-build -b linkcheck {sphinx_options} "
        f"{paths.sphinx.sources} {output_path}" )


@task
def check_readme( context ):
    ''' Checks that the README will render correctly on PyPI. '''
    eprint( _render_boxed_title( 'Test: README Render' ) )
    path = _get_sdist_path( )
    context.run( f"twine check {path}" )


@task( pre = ( test, check_urls, ), post = ( check_readme, ) )
def make_sdist( context ):
    ''' Packages the Python sources for release. '''
    eprint( _render_boxed_title( 'Artifact: Source Distribution' ) )
    _assert_gpg_tty( )
    path = _get_sdist_path( )
    context.run( 'python3 setup.py sdist' )
    context.run( f"gpg --detach-sign --armor {path}", pty = True )


def _get_sdist_path( ):
    project_version = parse_project_version( )
    name = f"{project_name}-{project_version}.tar.gz"
    return paths.artifacts / 'sdists' / name


@task( pre = ( make_sdist, ) )
def make_wheel( context ):
    ''' Packages a Python wheel for release. '''
    eprint( _render_boxed_title( 'Artifact: Python Wheel' ) )
    _assert_gpg_tty( )
    path = _get_wheel_path( )
    context.run( 'python3 setup.py bdist_wheel' )
    context.run( f"gpg --detach-sign --armor {path}", pty = True )


def _get_wheel_path( ):
    project_version = parse_project_version( )
    name = f"{project_name}-{project_version}-py3-none-any.whl"
    return paths.artifacts / 'wheels' / name


@task( pre = ( check_urls, ) )
def make_html( context ):
    ''' Generates documentation as HTML artifacts. '''
    eprint( _render_boxed_title( 'Artifact: Documentation' ) )
    output_path = paths.artifacts / 'html' / 'sphinx'
    _unlink_recursively( output_path )
    context.run(
        f"sphinx-build -b html {sphinx_options} "
        f"{paths.sphinx.sources} {output_path}" )


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
    eprint( _render_boxed_title( f"Version: Adjust" ) )
    _ensure_clean_workspace( context )
    _assert_gpg_tty( )
    project_version = parse_project_version( )
    current_version = Version.from_string( project_version )
    new_version = current_version.as_bumped( piece )
    if 'stage' == piece: part = 'release_class'
    elif 'patch' == piece:
        if current_version.stage in ( 'a', 'rc' ): part = 'prerelease'
        else: part = 'patch'
    else: part = piece
    my_cfg_path = paths.configuration / 'bumpversion.cfg'
    context.run(
        f"bumpversion --config-file={my_cfg_path}"
        f" --current-version {current_version}"
        f" --new-version {new_version}"
        f" {part}", pty = True )


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
    project_version = parse_project_version( )
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
        f"git diff --unified=0 --no-color -- {paths.python3.sources} "
        f"| yapf-diff {yapf_options_string}" )


@task( pre = ( test, ) )
def push( context, remote = 'origin' ):
    ''' Pushes commits on current branch, plus all tags. '''
    eprint( _render_boxed_title( 'SCM: Push Branch with Tags' ) )
    _ensure_clean_workspace( context )
    project_version = parse_project_version( )
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
    version = version or parse_project_version( )
    eprint( _render_boxed_title(
        f"Verify: Python Package Installation ({version})" ) )
    with TemporaryDirectory( ) as venv_path:
        venv_path = Path( venv_path )
        create_venv( venv_path, clear = True, with_pip = True )
        index_url_option = ''
        if index_url: index_url_option = f"--index-url {index_url}"
        options = derive_python_venv_execution_options( context, venv_path )
        attempts_count_max = 2
        for attempts_count in range( attempts_count_max + 1 ):
            try:
                context.run(
                    f"pip install {index_url_option} "
                    f"  {project_name}=={version}", pty = True, **options )
            except Failure:
                if attempts_count_max == attempts_count: raise
                sleep( 2 ** attempts_count )
            else: break
        python_import_command = (
            f"import {project_name}; "
            f"print( {project_name}.__version__ )" )
        context.run(
            f"python -c '{python_import_command}'", pty = True, **options )


@task
def check_pypi_integrity( context, index_url = '' ):
    ''' Checks integrity of current package uploads on PyPI. '''
    index_url = index_url or 'https://pypi.org'
    project_url = f"{index_url}/pypi/{project_name}/json"
    project_version = parse_project_version( )
    request = HttpRequest(
        project_url, headers = { 'Accept': 'application/json', } )
    attempts_count_max = 2
    for attempts_count in range( attempts_count_max + 1 ):
        try:
            with urlopen( request ) as http_reader:
                packages_info = json_load(
                    http_reader )[ 'releases' ][ project_version ]
        except ( KeyError, UrlError, ):
            if attempts_count_max == attempts_count: raise
            sleep( 2 ** attempts_count )
        else: break
    for package_info in packages_info:
        url = package_info[ 'url' ]
        if not package_info.get( 'has_sig', False ):
            raise Exit( f"No signature found for: {url}" )
        check_pypi_package( context, url )


def check_pypi_package( context, package_url ):
    ''' Verifies signature on package. '''
    _assert_gpg_tty( )
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
    eprint( _render_boxed_title( f"Publication: PyPI{task_name_suffix}" ) )
    artifacts = _get_pypi_artifacts( )
    context.run(
        f"twine upload --skip-existing --verbose {repository_option} "
        f"{artifacts}",
        env = _get_pypi_credentials( repository_name ), pty = True )


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
    eprint( _render_boxed_title( 'Publication: Github Pages' ) )
    # Use relative path, since 'git subtree' needs it.
    html_path = (
        paths.artifacts.relative_to( paths.project ) / 'html' / 'sphinx' )
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
