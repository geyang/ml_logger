# http://www.sphinx-doc.org/en/master/config
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

project = 'ml-logger'
copyright = '2019, Ge Yang'
author = 'Ge Yang'

with open('../../VERSION', encoding='utf-8') as f:
    # with open('../../VERSION', encoding='utf-8') as f:
    version = f.read()  # the short semver string
    release = version  # the release name (with beta/rc etc)

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.viewcode',
    # 'sphinx.ext.githubpages',
    'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = [
    '/home/docs/checkouts/readthedocs.org/user_builds/ml-logger/checkouts/latest/ml_logger/docs/source/',
    '_templates'
]
exclude_patterns = ['build']
html_theme = 'alabaster'
html_static_path = ['_static']

# autodoc_mock_imports = ["waterbear"]
