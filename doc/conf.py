import os
import sys

html_static_path = []

# enable autodoc to load local modules
sys.path.insert(0, os.path.abspath(".."))

project = "JMU Python Gradescope Utils"
copyright = "2020"
author = "JMU People"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx.ext.napoleon"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None)
}
html_theme_options = {"nosidebar": True}
