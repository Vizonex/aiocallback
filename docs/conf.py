# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

try:
    from aiocallback import __version__
except ModuleNotFoundError:
    __version__ = "0.2.0"

project = "aiocallback"
copyright = "2025, Vizonex"
author = "Vizonex"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
]


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "aiohttp_theme"


html_theme_options = {
    "logo": None,
    "description": "A library for helping configure asynchronous callbacks using member descriptors",
    "github_user": "Vizonex",
    "github_repo": "aiocallback",
    "github_button": True,
    "github_type": "star",
    "github_banner": True,
}

intersphinx_mapping = {"python": ("http://docs.python.org/3", None)}
