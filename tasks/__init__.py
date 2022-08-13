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
from pathlib import Path
from sys import stderr
from tempfile import TemporaryDirectory
from time import sleep
from urllib.error import URLError as UrlError
from urllib.parse import urlparse
from urllib.request import urlopen
from venv import create as create_venv

from invoke import Context, Exit, Failure, call, task

from .base import (
    assert_gpg_tty,
    derive_venv_context_options,
    eprint, epprint,
    indicate_python_versions_support,
    on_tty,
    paths,
    pep508_identify_python,
    render_boxed_title,
    unlink_recursively,
)
from .versions import (
    Version,
)
from our_base import (
    discover_project_version,
    indicate_python_packages,
    project_name,
)


class __:

    from .base import (
        detect_vmgr_python_version,
        is_executable_in_venv,
    )
    from .environments import (
        build_python_venv,
    )
    from .packages import (
        calculate_python_packages_fixtures,
        delete_python_packages_fixtures,
        execute_pip_with_requirements,
        indicate_current_python_packages,
        install_python_packages,
        record_python_packages_fixtures,
        retrieve_pypi_release_information,
    )
    from .platforms import (
        freshen_python,
        install_python_builder,
    )
    from our_base import (
        active_python_abi_label,
        ensure_python_support_packages,
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
def build_python_venv( context, version, overwrite = False ):
    ''' Creates virtual environment for requested Python version. '''
    if 'ALL' == version: versions = indicate_python_versions_support( )
    else: versions = ( version, )
    for version_ in versions:
        __.build_python_venv( context, version_, overwrite = overwrite )


@task(
    pre = (
        call( build_python_venv, version = 'ALL' ),
        call( install_git_hooks ),
    )
)
def bootstrap( context ): # pylint: disable=unused-argument
    ''' Bootstraps the development environment and utilities. '''


@task
def clean_pycaches( context ): # pylint: disable=unused-argument
    ''' Removes all caches of compiled CPython bytecode. '''
    render_boxed_title( 'Clean: Python Caches' )
    anchors = (
        paths.sources.d.python3, paths.sources.p.python3,
        paths.sources.p.sphinx,
        paths.tests.p.python3,
    )
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '__pycache__' ), anchors
    ) ): unlink_recursively( path )


@task
def clean_tool_caches( context, include_development_support = False ): # pylint: disable=unused-argument
    ''' Clears the caches used by code generation and testing utilities. '''
    render_boxed_title( 'Clean: Tool Caches' )
    anchors = paths.caches.SELF.glob( '*' )
    ignorable_paths = set( paths.caches.SELF.glob( '*/.gitignore' ) )
    if not include_development_support:
        ds_path = paths.caches.packages.python3 / __.active_python_abi_label
        ignorable_paths.add( paths.caches.packages.python3 )
        ignorable_paths.add( ds_path )
        ignorable_paths.update( ds_path.rglob( '*' ) )
    dirs_stack = [ ]
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '*' ), anchors
    ) ):
        if path in ignorable_paths: continue
        if path.is_dir( ) and not path.is_symlink( ):
            dirs_stack.append( path )
            continue
        path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )
    # Setuptools hardcodes the eggs path to different location.
    unlink_recursively( paths.caches.eggs )
    # Regnerate development support packages cache, if necessary.
    if include_development_support: __.ensure_python_support_packages( )


@task
def clean_python_packages( context, version = None ):
    ''' Removes unused Python packages.

        If version is 'ALL', then all virtual environments are targeted. '''
    if 'ALL' == version: versions = indicate_python_versions_support( )
    else: versions = ( version, )
    for version_ in versions:
        _clean_python_packages( context, version = version_ )


def _clean_python_packages( context, version = None ):
    ''' Removes unused Python packages in virtual environment. '''
    render_boxed_title( 'Clean: Unused Python Packages', supplement = version )
    context_options = derive_venv_context_options( version = version )
    identifier = pep508_identify_python( version = version )
    _, fixtures = indicate_python_packages( identifier = identifier )
    requested = frozenset( fixture[ 'name' ] for fixture in fixtures )
    installed = frozenset(
        entry.requirement.name
        for entry
        in __.indicate_current_python_packages( context_options[ 'env' ] ) )
    requirements_text = '\n'.join( installed - requested - { project_name } )
    if not requirements_text: return
    __.execute_pip_with_requirements(
        context, context_options, 'uninstall', requirements_text,
        pip_options = ( '--yes', ) )


@task
def clean( context, version = None ):
    ''' Cleans all caches. '''
    clean_python_packages( context, version = version )
    clean_pycaches( context )
    clean_tool_caches( context )


@task
def check_security_issues( context, version = None ):
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
    # Disable until https://github.com/danhper/asdf-python/issues/140
    # is resolved.
    #context.run( 'asdf plugin update python', pty = on_tty )
    # TODO: Preserve this call after 'freshen_asdf' has been removed.
    __.install_python_builder( )


@task( pre = ( freshen_asdf, ) )
def freshen_python( context, version = None ):
    ''' Updates supported Python minor version to latest patch.

        If version is 'ALL', then all supported Pythons are targeted.

        This task requires Internet access and may take some time. '''
    original_versions = indicate_python_versions_support( )
    if 'ALL' == version: versions = original_versions
    else: versions = ( version or __.detect_vmgr_python_version( ), )
    obsolete_identifiers = set( )
    version_replacements = { }
    for version_ in versions:
        replacement, identifier = __.freshen_python( context, version_ )
        version_replacements.update( replacement )
        if None is not identifier: obsolete_identifiers.add( identifier )
    # Can only update record of local versions after they are installed.
    successor_versions = [
        version_replacements.get( version_, version_ )
        for version_ in original_versions ]
    context.run( "asdf local python {versions}".format(
        versions = ' '.join( successor_versions ) ), pty = True )
    # Erase packages fixtures for versions which are no longer extant.
    __.delete_python_packages_fixtures( obsolete_identifiers )


@task
def freshen_python_packages( context, version = None ):
    ''' Updates declared Python packages.

        If version is 'ALL', then all virtual environments are targeted. '''
    if 'ALL' == version: versions = indicate_python_versions_support( )
    else: versions = ( version, )
    for version_ in versions: _freshen_python_packages( context, version_ )


def _freshen_python_packages( context, version = None ):
    ''' Updates Python packages in virtual environment. '''
    render_boxed_title(
        'Freshen: Python Package Versions', supplement = version )
    context_options = derive_venv_context_options( version = version )
    identifier = pep508_identify_python( version = version )
    __.install_python_packages( context, context_options )
    fixtures = __.calculate_python_packages_fixtures(
        context_options[ 'env' ] )
    __.record_python_packages_fixtures( identifier, fixtures )
    check_security_issues( context, version = version )
    test( context, version = version )


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
        call( clean ),
        call( freshen_git_modules ),
        call( freshen_python, version = 'ALL' ),
        call( freshen_python_packages, version = 'ALL' ),
        call( freshen_git_hooks ),
    )
)
def freshen( context ): # pylint: disable=unused-argument
    ''' Performs the various freshening tasks, cleaning first.

        This task requires Internet access and may take some time. '''


@task
def lint_bandit( context, version = None ):
    ''' Security checks the source code with Bandit. '''
    render_boxed_title( 'Lint: Bandit', supplement = version )
    context.run(
        f"bandit --recursive --verbose {paths.sources.p.python3}",
        pty = True, **derive_venv_context_options( version = version ) )


@task( iterable = ( 'packages', 'modules', 'files', ) )
def lint_mypy( context, packages, modules, files, version = None ):
    ''' Lints the source code with Mypy. '''
    render_boxed_title( 'Lint: Mypy', supplement = version )
    context_options = derive_venv_context_options( version = version )
    if not __.is_executable_in_venv(
        'mypy', venv_path = context_options[ 'env' ][ 'VIRTUAL_ENV' ]
    ):
        eprint( 'Mypy not available on this platform. Skipping.' )
        return
    configuration_str = f"--config-file {paths.configuration.mypy}"
    if not packages and not modules and not files:
        #files = ( paths.sources.p.python3, paths.project / 'tasks' )
        files = ( paths.sources.p.python3, )
    packages_str = ' '.join( map(
        lambda package: f"--package {package}", packages ) )
    modules_str = ' '.join( map(
        lambda module: f"--module {module}", modules ) )
    files_str = ' '.join( map( str, files ) )
    context.run(
        f"mypy {configuration_str} "
        f"{packages_str} {modules_str} {files_str}",
        pty = True, **context_options )


@task( iterable = ( 'targets', 'checks', ) )
def lint_pylint( context, targets, checks, version = None ):
    ''' Lints the source code with Pylint. '''
    render_boxed_title( 'Lint: Pylint', supplement = version )
    context_options = derive_venv_context_options( version = version )
    if not __.is_executable_in_venv(
        'pylint', venv_path = context_options[ 'env' ][ 'VIRTUAL_ENV' ]
    ):
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
def lint_semgrep( context, version = None ):
    ''' Lints the source code with Semgrep. '''
    render_boxed_title( 'Lint: Semgrep', supplement = version )
    context_options = derive_venv_context_options( version = version )
    if not __.is_executable_in_venv(
        'semgrep', venv_path = context_options[ 'env' ][ 'VIRTUAL_ENV' ]
    ):
        eprint( 'Semgrep not available on this platform. Skipping.' )
        return
    sgconfig_path = paths.scm_modules / 'semgrep-rules' / 'python' / 'lang'
    context.run(
        f"semgrep --config {sgconfig_path} --use-git-ignore "
        f"{paths.sources.p.python3}", pty = on_tty, **context_options )


@task
def lint( context, version = None ):
    ''' Lints the source code. '''
    lint_pylint( context, targets = ( ), checks = ( ), version = version )
    lint_semgrep( context, version = version )
    lint_mypy( context,
        packages = ( ), modules = ( ), files = ( ), version = version )
    lint_bandit( context, version = version )


@task
def report_coverage( context ):
    ''' Combines multiple code coverage results into a single report. '''
    render_boxed_title( 'Artifact: Code Coverage Report' )
    context_options = derive_venv_context_options( )
    context.run( 'coverage combine', pty = True, **context_options )
    context.run( 'coverage report', pty = True, **context_options )
    context.run( 'coverage html', pty = True, **context_options )
    context.run( 'coverage xml', pty = True, **context_options )


@task
def test( context, version = None ):
    ''' Runs the test suite.

        If version is 'ALL', then all virtual environments are targeted. '''
    if 'ALL' == version: versions = indicate_python_versions_support( )
    else: versions = ( version, )
    for version_ in versions: _test( context, version_ )


def _test( context, version = None ):
    ''' Runs the test suite in virtual environment. '''
    clean( context, version = version )
    lint( context, version = version )
    render_boxed_title( 'Test: Unit + Code Coverage', supplement = version )
    context_options = derive_venv_context_options( version = version )
    context_options[ 'env' ].update( dict(
        HYPOTHESIS_STORAGE_DIRECTORY = paths.caches.hypothesis,
    ) )
    context.run(
        f"coverage run --source {project_name}",
        pty = True, **context_options )


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
    release_info = __.retrieve_pypi_release_information(
        project_name, version, index_url = index_url )
    for package_info in release_info:
        url = package_info[ 'url' ]
        if not package_info.get( 'has_sig', False ):
            raise Exit( f"No signature found for: {url}" )
        check_pypi_package( context, url )


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
    pre = (
        call( upload_test_pypi ),
        call( test, version = 'ALL' ),
    ),
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
