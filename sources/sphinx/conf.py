""" Configuration file for the Sphinx documentation builder.

    This file only contains a selection of the most common options.
    For a full list, see the documentation:
        https://www.sphinx-doc.org/en/master/usage/configuration.html
    Also, see this nice article on Sphinx customization:
        https://jareddillard.com/blog/common-ways-to-customize-sphinx-themes.html
"""


def _configure( ):
    from pathlib import Path
    project_path = Path( __file__ ).parent.parent.parent
    from importlib.util import module_from_spec, spec_from_file_location
    module_spec = spec_from_file_location(
        '_develop', project_path / 'develop.py' )
    module = module_from_spec( module_spec )
    module_spec.loader.exec_module( module )
    module.configure_auxiliary( project_path )

_configure( )


def _install_prerequisite_packages( ):
    # Hack to install documentation requirements for ReadTheDocs builder.
    # (Better than maintaining a separate 'requirements.txt'.)
    from os import environ as current_process_environment
    from shlex import split as split_command
    from devshim__base import (
        extract_python_package_requirements,
        indicate_python_packages,
        paths,
        standard_execute_external,
    )
    if 'True' != current_process_environment.get( 'READTHEDOCS', 'False' ):
        return
    requirements = extract_python_package_requirements(
        indicate_python_packages( )[ 0 ], 'development.documentation' )
    # TODO: Handle constraints on package names in requirements.
    manifest = tuple(
        package_name for package_name in requirements
        if 'sphinx' != package_name )
    standard_execute_external(
        ( *split_command( 'pip install --upgrade' ), *manifest ) )
    from sys import path as python_search_paths
    python_search_paths.insert( 0, str( paths.sources.p.python3 ) )
_install_prerequisite_packages( )


# -- Project information -----------------------------------------------------

def _calculate_copyright_notice( information, author_ ):
    from datetime import datetime as DateTime
    first_year = information[ 'year-of-origin' ]
    now_year = DateTime.utcnow( ).year
    if first_year < now_year: year_range = f"{first_year}-{now_year}"
    else: year_range = str( first_year )
    return f"{year_range}, {author_}"

from devshim__base import discover_project_information
_information = discover_project_information( )
project = _information[ 'name' ]
release = _information[ 'version' ]
author = _information[ 'authors' ][ 0 ][ 'name' ]
project_copyright = _calculate_copyright_notice( _information, author )


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.graphviz',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_copybutton',
    'sphinx_inline_tabs',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

rst_prolog = f'''
.. |project| replace:: {project}
'''

nitpicky = True
nitpick_ignore = [
    # Workaround for https://bugs.python.org/issue11975
    # Found on Stack Overflow (credit to Astropy project):
    #   https://stackoverflow.com/a/30624034
    ( 'py:class', "module", ),
    ( 'py:class', "mappingproxy", ),
    ( 'py:class', "integer -- return first index of value.", ),
    ( 'py:class', "integer -- return number of occurrences of value", ),
    ( 'py:class', "a set-like object providing a view on D's keys", ),
    ( 'py:class', "an object providing a view on D's values", ),
    ( 'py:class', "a set-like object providing a view on D's items", ),
    ( 'py:class', "D[k] if k in D, else d.  d defaults to None.", ),
    ( 'py:class', "None.  Update D from mapping/iterable E and F.", ),
    ( 'py:class', "D.get(k,d), also set D[k]=d if k not in D", ),
    ( 'py:class', "(k, v), remove and return some (key, value) pair", ),
    ( 'py:class',
      "v, remove specified key and return the corresponding value.", ),
    ( 'py:class', "None.  Remove all items from D.", ),
]

# -- Options for linkcheck builder -------------------------------------------

linkcheck_ignore = [
    # Circular dependency between building HTML and publishing it.
    # Ideally, we want to warn on failure rather than ignore.
    fr'https://emcd\.github\.io/.*{project}.*/.*',
]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
# https://github.com/pradyunsg/furo
html_theme = 'furo'
html_theme_options = {
    'navigation_with_keys': True,
    'sidebar_hide_name': True,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None ),
}

# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True

# -- Options for autodoc extension -------------------------------------------

autodoc_default_options = {
    'member-order': 'bysource',
    'imported-members': False,
    'inherited-members': True,
    'show-inheritance': True,
    'undoc-members': True,
}
