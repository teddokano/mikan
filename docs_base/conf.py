from unittest.mock import MagicMock

import os
import sys
sys.path.insert(0, os.path.abspath('../'))
#sys.path.insert(0, os.path.abspath('./'))
sys.modules['machine'] = MagicMock()
sys.modules['utime'] = MagicMock()

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information ---------------------------------w--------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mikan'
copyright = '2023, Tedd OKANO'
author = 'Tedd OKANO'
release = '1.10'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [  'sphinx.ext.autodoc',
				'sphinx.ext.napoleon',
				'sphinx.ext.viewcode',
				'sphinx.ext.doctest',
				'sphinx.ext.intersphinx',
				'sphinx.ext.todo',
				'sphinx.ext.coverage',
				]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

autodoc_mock_imports = ['ustruct']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
