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

libclang_path = "/usr/lib/"
candidates = []
for i in os.listdir(libclang_path):
    if "llvm" in i:
        partial_path = i + "/lib/"
        for j in os.listdir(libclang_path + partial_path):
            if "libclang" in j and ".so" in j and "cpp" not in j:
                candidates.append(partial_path + j)
    elif "libclang" in i and ".so" in i and "cpp" not in i:
        candidates.append(i)
for i in candidates:
    if "libclang.so" in i:
        libclang_path += i
        break

from clang.cindex import Config
Config.set_library_file(libclang_path)


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '../meafs_code/images/Meafs_Logo.png'
html_theme_options = {'logo_only': True}
