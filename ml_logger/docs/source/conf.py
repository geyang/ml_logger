# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import os, sys

# --- configure the python environment for autodoc ---
cwd = os.path.dirname(os.path.abspath(__file__))

print(os.path.join(cwd, "../../"))
# print(os.path.abspath("../../"))
sys.path.insert(0, os.path.abspath(os.path.join(cwd, '../../')))
# sys.path.insert(0, '../../')

# -- Project information -----------------------------------------------------

project = 'ml-logger'
copyright = '2019, Ge Yang'
author = 'Ge Yang'

print(os.path.join(cwd, "../../VERSION"))
print(os.path.abspath("../../VERSION"))
with open(os.path.abspath(os.path.join(cwd, '../../VERSION')), encoding='utf-8') as f:
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
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# autodoc_mock_imports = ["waterbear"]
