""" Configuration file for the Sphinx documentation builder.

    This file only contains a selection of the most common options.
    For a full list, see the documentation:
        https://www.sphinx-doc.org/en/master/usage/configuration.html
    Also, see this nice article on Sphinx customization:
        https://jareddillard.com/blog/common-ways-to-customize-sphinx-themes.html
"""

# -- Path setup --------------------------------------------------------------

from pathlib import Path
_top_path = Path( __file__ ).parent.parent.parent


# -- Project information -----------------------------------------------------

_setup_cfg_path = _top_path / "setup.cfg"
if _setup_cfg_path.is_file( ):
    from configparser import ConfigParser
    _config = ConfigParser( )
    _config.read( _setup_cfg_path )
    _metadata = _config[ 'metadata' ]
    project = _metadata[ 'name' ]
    release = _metadata[ 'version' ]
    try: author = _metadata[ 'author' ]
    except KeyError: author = _metadata[ 'maintainer' ]
    _license = _metadata[ 'license' ]
# TODO: Also look in 'pyproject.toml' once PEP 621 is implemented.
else: raise Exception( 'Cannot find suitable source of project metadata.' )
from datetime import datetime as DateTime
_first_year = 2021
_now_year = DateTime.utcnow( ).year
if _first_year < _now_year:
    _copyright_year_range = f"{_first_year}-{_now_year}"
else: _copyright_year_range = str( _first_year )
copyright = f"{_copyright_year_range}, {author}" # pylint: disable=redefined-builtin


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
