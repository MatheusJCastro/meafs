# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = 'MEAFS'
copyright = '2024, Matheus J. Castro'
author = 'Matheus J. Castro'
release = '4.7'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc", "sphinx_c_autodoc", "sphinx_c_autodoc.viewcode", "sphinx.ext.mathjax"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
c_autodoc_roots = ['../meafs_code/scripts/']

def capture_command_output(command):
    stream = os.popen(command)
    output = stream.read().strip()
    return output

libclang_path=capture_command_output("whereis libclang.so | awk '{split($0,a,\" \"); print a[2]}'")

from clang.cindex import Config
Config.set_library_file(libclang_path)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '../meafs_code/images/Meafs_Logo.png'
html_theme_options = {'logo_only': True}
