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
release = '4.7.13'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.todo", "sphinx.ext.viewcode", "sphinx.ext.autodoc", "sphinx_c_autodoc", "sphinx_c_autodoc.viewcode", "sphinx.ext.mathjax"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

c_autodoc_roots = ['../meafs_code/scripts/']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '../meafs_code/images/Meafs_Logo.png'
html_theme_options = {'logo_only': True}

html_css_files = [
    'css/custom.css',
]

# Bug Fix for Clang bindins
def capture_command_output(command):
    stream = os.popen(command)
    output = stream.read().strip()
    return output

clangver = capture_command_output("clang --version")
clangver = clangver.replace("\n", " ")
clangver = clangver.split(" ")
clangver = clangver[clangver.index("version") + 1]
clangver = clangver.split(".")[0]

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
    version_test = i.split("/")
    if clangver in version_test[-1]:
        libclang_path += i
        break

ossystem = capture_command_output("cat /etc/os-release | awk '$0 ~ /^NAME/' | awk '{split($0,a,\"=\"); print a[2]}' |"
                                  " awk '{a=substr($0,2,length($0)-2); print a}'")

from clang.cindex import Config

if ossystem == "Ubuntu":
    Config.set_library_file("/home/docs/checkouts/readthedocs.org/user_builds/meafs/envs/latest/lib/"
                            "python3.12/site-packages/clang/native/libclang.so")
else:
    Config.set_library_file(libclang_path)
