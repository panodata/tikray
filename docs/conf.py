# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# ruff: noqa: ERA001

project = "tikray"
copyright = "2019-2025, The Panodata Developers"  # noqa: A001
author = "The Panodata Developers"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.ifconfig",
    "sphinxcontrib.mermaid",
    "sphinxext.opengraph",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.

html_title = "Tikray"

html_theme_options = {
    "sidebar_hide_name": False,
    # https://github.com/pradyunsg/furo/blob/main/src/furo/assets/styles/variables/_colors.scss
    # "light_logo": "logo-light.svg",
    # "dark_logo": "logo-dark.svg",
    # #CC3333 is persian red.
    "light_css_variables": {
        "color-brand-primary": "darkcyan",
        "color-brand-content": "darkblue",
        # "color-admonition-background": "orange",
    },
    "dark_css_variables": {
        "color-brand-primary": "darkcyan",
        "color-brand-content": "lightblue",
        # "color-admonition-background": "orange",
    },
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}

html_show_sourcelink = True


# -- Intersphinx ----------------------------------------------------------

intersphinx_mapping = {
    # "influxio": ("https://influxio.readthedocs.io/", None),
}
linkcheck_ignore = [
    r"https://stackoverflow.com/questions/70518350",
]

# Disable caching remote inventories completely.
# http://www.sphinx-doc.org/en/stable/ext/intersphinx.html#confval-intersphinx_cache_limit
# intersphinx_cache_limit = 0


# -- Extension configuration -------------------------------------------------

sphinx_tabs_valid_builders = ["linkcheck"]
todo_include_todos = True

# Configure sphinx-copybutton
copybutton_remove_prompts = True
copybutton_line_continuation_character = "\\"
copybutton_prompt_text = r">>> |\.\.\. |\$ |sh\$ |PS> |cr> |mysql> |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: |expression: "
copybutton_prompt_is_regexp = True

# Configure sphinxext-opengraph
ogp_site_url = "https://tikray.readthedocs.io/"
ogp_enable_meta_description = True
# ogp_image = "http://example.org/image.png"
# ogp_description_length = 300


# -- Options for MyST -------------------------------------------------

myst_heading_anchors = 3
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "strikethrough",
    "substitution",
    "tasklist",
]
myst_substitutions = {}
