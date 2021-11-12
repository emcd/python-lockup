""" Project maintenance tasks, executed via :command:`invoke`.

    `Invoke Documentation <http://docs.pyinvoke.org/en/stable/index.html>`_

    Why use :command:`invoke` instead of :command:`make`?

    * The Makefile language, while generally elegant and well-suited
      to deterministic workflows, such as software maintenance automation,
      is an additional language which must be remembered.

    * While GNU Make is essentially ubiquitous in the Unix world,
      it is not available by default on Windows.
      Moreover, Microsoft Nmake does not have entirely compatible syntax.
      Dual maintenance of DOS/Windows batch files or Powershell scripts
      is also undesirable.

    * As Python is a prerequisite for this project
      and we have the infrastructure to guarantee
      a particular software environment,
      we can ensure a specific version of :command:`invoke` is available.
      We would have no similar assurance with a system-provided
      :command:`make`
      and cannot provide this command via the Python package ecosystem.

    * We can avoid the use of commands, such as :command:`find`,
      which have platform-specific variations,
      and instead use equivalent standardized functions.
      An additional benefit is that function invocations are
      within the same Python interpreter session,
      whereas command invocations have fork-exec overhead.

    * Separate options can be passed for each of multiple targets
      to :command:`invoke`, whereas :command:`make` only consumes
      global options and variables.

    * A summary of all available targets/subcommands
      along with brief descriptions can be listed by :command:`invoke`,
      whereas :command:`make` does not provide such a facility.
"""


from pathlib import Path
from invoke import Exit, task, call


top_path = Path( __file__ ).parent.parent
artifacts_path = top_path / 'artifacts'
caches_path = top_path / 'caches'
scm_modules_path = top_path / 'scm-modules'
sources_path = top_path / 'sources'
tests_path = top_path / 'tests'
project = top_path.name

python3_sources_path = sources_path / 'python3'
python3_tests_path = tests_path / 'python3'

sphinx_sources_path = sources_path / 'sphinx'
sphinx_cache_path = caches_path / 'sphinx'
# https://www.sphinx-doc.org/en/master/man/sphinx-build.html
sphinx_options = f"-j auto -d {sphinx_cache_path} -n -T"


def _parse_project_information( ):
    path = top_path / 'setup.cfg'
    if path.is_file( ):
        from configparser import ConfigParser
        config = ConfigParser( )
        config.read( path )
        metadata = config[ 'metadata' ]
        return path, metadata[ 'name' ], metadata[ 'version' ]
    # TODO: Look in 'pyproject.toml' if PEP 621 is implemented.
    #       https://www.python.org/dev/peps/pep-0621/
    raise Exception( 'Cannot find suitable source of project metadata.' )

configuration_path, package_name, package_version = (
    _parse_project_information( ) )


def _unlink_recursively( path ):
    """ Pure Python implementation of ``rm -rf``, essentially. """
    if not path.exists( ): return
    if not path.is_dir( ):
        path.unlink( )
        return
    dirs_stack = [ ]
    for child_path in path.rglob( '*' ):
        if child_path.is_dir( ):
            dirs_stack.append( child_path )
            continue
        child_path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )
    path.rmdir( )


@task
def clean_pycaches( context ): # pylint: disable=unused-argument
    """ Removes all caches of compiled CPython bytecode. """
    from itertools import chain
    anchors = ( python3_sources_path, python3_tests_path, )
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '__pycache__/*' ), anchors
    ) ): path.unlink( )
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '__pycache__' ), anchors
    ) ): path.rmdir( )


@task
def clean_tool_caches( context ): # pylint: disable=unused-argument
    """ Clears the caches used by code generation and testing utilities. """
    from itertools import chain
    anchors = caches_path.glob( '*' )
    gitignore_paths = set( caches_path.glob( '*/.gitignore' ) )
    dirs_stack = [ ]
    for path in chain.from_iterable( map(
        lambda anchor: anchor.rglob( '*' ), anchors
    ) ):
        if path in gitignore_paths: continue
        if path.is_dir( ):
            dirs_stack.append( path )
            continue
        path.unlink( )
    while dirs_stack: dirs_stack.pop( ).rmdir( )
    # Note: 'setuptools' hardcodes this path.
    _unlink_recursively( top_path / '.eggs' )


@task
def clean_pipenv( context ):
    """ Removes unused packages in the Python development virtualenv. """
    context.run( 'pipenv clean', pty = True )


@task( pre = ( clean_pycaches, clean_tool_caches, clean_pipenv, ) )
def clean( context ): # pylint: disable=unused-argument
    """ Cleans all caches. """


@task
def check_pipenv_security( context ):
    """ Checks for security issues in utilized packages and tools.

        This task requires Internet access and may take some time. """
    context.run( 'pipenv check', pty = True )


@task( post = ( clean_pipenv, check_pipenv_security, ) )
def freshen_pipenv( context ):
    """ Updates packages for the Python development virtualenv.

        This task requires Internet access and may take some time. """
    context.run( 'pipenv update --dev', pty = True )


@task
def freshen_scm_modules( context ):
    """ Performs recursive update of all SCM modules.

        Initializes SCM modules as needed.
        This task requires Internet access and may take some time. """
    context.run(
        'git submodule update --init --recursive --remote', pty = True )


@task( pre = ( clean, freshen_pipenv, freshen_scm_modules, ) )
def freshen( context ): # pylint: disable=unused-argument
    """ Performs the various freshening tasks, cleaning first.

        This task requires Internet access and may take some time. """


@task
def lint_bandit( context ):
    """ Security checks the source code with Bandit. """
    context.run( f"bandit --recursive --verbose {python3_sources_path}" )


@task( iterable = ( 'packages', 'modules', 'files', ) )
def lint_mypy( context, packages, modules, files ):
    """ Lints the source code with Mypy. """
    environment_str = f"MYPYPATH={top_path}:{python3_sources_path}"
    configuration_str = "--config-file {}".format( sources_path / 'mypy.ini' )
    if not packages and not modules and not files: packages = ( package_name, )
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
    """ Lints the source code with Pylint. """
    reports_str = '--reports=no --score=no' if targets or checks else ''
    if not targets:
        targets = (
            package_name,
            *python3_tests_path.rglob( '*.py' ),
            sphinx_sources_path / 'conf.py',
            __package__, )
    targets_str = ' '.join( map( str, targets ) )
    checks_str = (
        "--disable=all --enable={}".format( ','.join( checks ) )
        if checks else '' )
    context.run(
        f"pylint {reports_str} {checks_str} {targets_str}", pty = True )


@task
def lint_semgrep( context ):
    """ Lints the source code with Semgrep. """
    sgconfig_path = (
        scm_modules_path / 'semgrep-rules' / 'python' / 'lang' )
    # TODO: Remove error interception once Semgrep core does not crash.
    context.run(
        f"semgrep --config {sgconfig_path} --use-git-ignore "
        f"{python3_sources_path}", hide = 'stderr', warn = True )


@task( pre = (
    call( lint_pylint, targets = ( ), checks = ( ) ),
    call( lint_semgrep ),
    call( lint_mypy, packages = ( ), modules = ( ), files = ( ) ),
    call( lint_bandit ),
) )
def lint( context ): # pylint: disable=unused-argument
    """ Lints the source code. """


@task( pre = ( lint, ) )
def test( context ):
    """ Runs the test suite with the current Python version. """
    context.run(
        'coverage run', pty = True,
        env = dict(
            HYPOTHESIS_STORAGE_DIRECTORY = caches_path / 'hypothesis', ) )
    context.run( 'coverage report', pty = True )
    context.run( 'coverage html', pty = True )


@task( pre = ( lint, ) )
def test_all_versions( context ):
    """ Runs the test suite across multiple, isolated Python versions. """
    context.run(
        'tox --asdf-no-fallback --asdf-install', pty = True,
        env = dict(
            HYPOTHESIS_STORAGE_DIRECTORY = caches_path / 'hypothesis', ) )


@task( pre = ( test_all_versions, ) )
def cover_all_versions( context ):
    """ Reports on code coverage across multiple, isolated Python versions. """
    context.run( 'coverage combine', pty = True )
    context.run( 'coverage report', pty = True )
    context.run( 'coverage html', pty = True )


@task
def check_urls( context ):
    """ Checks the HTTP URLs in the documentation for liveness. """
    output_path = artifacts_path / 'sphinx-linkcheck'
    context.run(
        f"sphinx-build -b linkcheck {sphinx_options} "
        f"{sphinx_sources_path} {output_path}" )


@task
def check_readme( context ):
    """ Checks that the README will render correctly on PyPI. """
    sdist_name = f"{package_name}-{package_version}.tar.gz"
    sdist_path = artifacts_path / 'sdists' / sdist_name
    context.run( f"twine check {sdist_path}" )


@task( pre = ( cover_all_versions, check_urls, ), post = ( check_readme, ) )
def make_sdist( context ):
    """ Packages the Python sources for release. """
    context.run( 'python3 setup.py sdist' )


@task( pre = ( make_sdist, ) )
def make_wheel( context ):
    """ Packages a Python wheel for release. """
    context.run( 'python3 setup.py bdist_wheel' )


@task( pre = ( check_urls, ) )
def make_html( context ):
    """ Generates documentation as HTML artifacts. """
    output_path = artifacts_path / "html" / "sphinx"
    _unlink_recursively( output_path )
    context.run(
        f"sphinx-build -b html {sphinx_options} "
        f"{sphinx_sources_path} {output_path}" )


@task( pre = ( freshen, make_wheel, make_html, ) )
def make( context ): # pylint: disable=unused-argument
    """ Generates all of the artifacts. """


class Version:
    """ Package version manager.

        Compatible with the version scheme laid forth in
        `PEP 440 <https://www.python.org/dev/peps/pep-0440/#version-scheme>`_.

        Core Format: ``{{major}}.{{minor}}.{{amendment}}``
        Development prereleases ("alpha versions") extend the core format
        by appending ``a{{timestamp:yyyymmddHHMM}}`` to it.
        Release candidates extend the core format
        by appending ``c{{candidate}}``,
        where ``candidate`` starts at ``1`` and increases by one
        upon each increment.
    """

    @classmethod
    def from_string( kind, version ):
        """ Constructs a version object by parsing it from a string. """
        from re import match
        matched = match(
            r"(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
            r"(?:(?P<stage>dev|rc)(?:"
            r"(?:(?<=dev)(?P<ts>\d{12}))|(?:(?<=rc)(?P<rc>\d+))"
            r"))?", version )
        stage = matched.group( 'stage' ) or 'f'
        patch = (
            matched.group( 'ts' ) if 'dev' == stage
            else (
                matched.group( 'rc' ) if 'rc' == stage
                else matched.group( 'patch' ) ) )
        return kind(
            stage, matched.group( 'major' ), matched.group( 'minor' ), patch )

    def __init__( self, stage, major, minor, patch ):
        if stage not in ( 'dev', 'rc', 'f' ):
            raise Exit( f"Bad stage: {stage}" )
        self.stage = stage
        self.major = int( major )
        self.minor = int( minor )
        self.patch = int( patch )

    # TODO: Make immutable with 'setattr'.

    def __str__( self ):
        stage, patch = self.stage, self.patch
        return ''.join( filter( None, (
            f"{self.major}", f".{self.minor}",
            f".{patch}" if 'f' == stage else '.0',
            f"{stage}{patch}" if stage in ( 'dev', 'rc' ) else '' ) ) )

    def as_bumped( self, piece ):
        """ Returns a derivative of the version,
            altered according to current state and desired modification.
        """
        from datetime import datetime as DateTime
        Version_ = type( self )
        stage, major, minor, patch = (
            self.stage, self.major, self.minor, self.patch )
        if 'stage' == piece:
            if 'dev' == stage: return Version_( 'rc', major, minor, 1 )
            if 'rc' == stage: return Version_( 'f', major, minor, 0 )
            raise Exit( 'Cannot bump last stage.' )
        timestamp = DateTime.utcnow( ).strftime( '%Y%m%d%H%M' )
        if 'patch' == piece:
            if 'dev' == stage:
                return Version_( 'dev', major, minor, timestamp )
            return Version_( stage, major, minor, patch + 1 )
        if 'major' == piece:
            return Version_( 'dev', major + 1, 0, timestamp )
        if 'minor' == piece:
            return Version_( 'dev', major, minor + 1, timestamp )
        raise Exit( f"Unknown kind of piece: {piece}" )


def _ensure_clean_workspace( context ):
    """ Error if version control reports any dirty or untracked files. """
    result = context.run( 'git status --short', pty = True )
    if result.stdout or result.stderr:
        raise Exit( 'Dirty workspace. Please stash or commit changes.' )


@task
def bump( context, piece ):
    """ Bumps a piece of the current version. """
    _ensure_clean_workspace( context )
    current_version = Version.from_string( package_version )
    new_version = current_version.as_bumped( piece )
    if 'stage' == piece: part = 'release_class'
    elif 'patch' == piece:
        if current_version.stage in 'ac': part = 'prerelease'
        else: part = 'patch'
    else: part = piece
    my_cfg_path = sources_path / 'bumpversion.cfg'
    context.run(
        f"bumpversion --config-file={my_cfg_path}"
        f" --current-version {current_version}"
        f" --new-version {new_version}"
        f" {part}", pty = True )


@task( post = ( call( bump, piece = 'patch' ), ) )
def bump_patch( context ): # pylint: disable=unused-argument
    """ Bumps to next patch level. """


@task( post = ( call( bump, piece = 'stage' ), ) )
def bump_stage( context ): # pylint: disable=unused-argument
    """ Bumps to next release stage. """


@task( post = ( bump_stage, ) )
def branch_release( context ):
    """ Makes a new branch for development torwards a release. """
    _ensure_clean_workspace( context )
    # TODO: Assert mainline branch.
    this_version = Version.from_string( package_version )
    stage = this_version.stage
    if 'a' != stage: raise Exit( f"Cannot create branch at stage: {stage}" )
    new_version = Version( 'f', this_version.major, this_version.minor, 0 )
    context.run( f"git checkout -b release-{new_version}", pty = True )


@task( optional = ( 'write_changes', ) )
def check_code_style( context, write_changes = False ):
    """ Checks code style of new changes. """
    yapf_options = [ ]
    if write_changes: yapf_options.append( '--in-place --verbose' )
    yapf_options_string = ' '.join( yapf_options )
    context.run(
        f"git diff -U0 --no-color -- {python3_sources_path} "
        f"| yapf-diff {yapf_options_string}" )


@task
def push( context ):
    """ Pushes commits on current branch, plus all tags. """
    _ensure_clean_workspace( context )
    true_branch = context.run(
        'git branch --show-current',
        hide = 'stdout', pty = True ).stdout.strip( )
    this_version = Version.from_string( package_version )
    new_version = Version( 'f', this_version.major, this_version.minor, 0 )
    target_branch = f"release-{new_version}"
    if true_branch == target_branch:
        remote = context.run(
            'git config --local branch.master.remote',
            hide = 'stdout', pty = True ).stdout.strip( )
        context.run(
            f"git push --set-upstream {remote} {true_branch}", pty = True )
    context.run( 'git push --tags', pty = True )


@task( pre = ( clean, make, push, ) )
def upload( context ):
    """ Publishes all relevant artifacts to their intended destinations. """
    # TODO: Call 'twine'.
    # TODO: Publish to Github pages, etc....
    context.run( 'echo "TODO: Implement the upload task."' )


@task( pre = ( clean, bump_patch, upload, ) )
def release_new_patch( context ): # pylint: disable=unused-argument
    """ Unleashes a new patch upon the world. """


@task( pre = ( clean, bump_stage, upload, ) )
def release_new_stage( context ): # pylint: disable=unused-argument
    """ Unleashes a new stage upon the world. """
