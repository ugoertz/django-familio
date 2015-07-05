# -*- coding: utf-8 -*-

# chronik documentation build configuration file, created by
# sphinx-quickstart on Sun Mar 15 10:10:21 2015.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os
import shlex

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.environ['DJANGO_PROJECT_DIR'])

# put the settings file that should be used here or define the environment
# variable DJANGO_SETTINGS_MODULE in the shell
# os.environ['DJANGO_SETTINGS_MODULE'] = 'familio.settings.xxx'

import django
from django.conf import settings
django.setup()

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['myext.genealogio', ]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
source_suffix = ['.rst']

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'chronicle'
copyright = u'2015, ug'
author = u'ug'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.0'
# The full version, including alpha/beta/rc tags.
release = ''

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = 'de'

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%d.%m.%Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'alabaster'
html_static_path = ['_static']
htmlhelp_basename = 'chronicledoc'

# -- Options for LaTeX output ---------------------------------------------

ADDITIONAL_PREAMBLE = r"""
\usepackage{pdfpages}
\usepackage{microtype}
\usepackage{fontspec}

\setmainfont{Vollkorn}

\definecolor{TitleColor}{rgb}{0,0,0}
\definecolor{InnerLinkColor}{rgb}{0,0,0}
\definecolor{OuterLinkColor}{rgb}{0,0,0}
\newcommand\DUroleunderline[1]{\underline{#1}}
"""

ADDITIONAL_FOOTER = r"""
"""

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',

    # * gets passed to \documentclass
    # * default options are single sided, double spaced
    # you can change them with these options:
    # * twoside
    # * singlespace
    # * you might want to omit the list of tables (lot)
    # if you use figtable without the :nofig: option
    'classoptions': ',ngerman,twoside,singlespace',
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '11pt',
    # Additional stuff for the LaTeX preamble.
    'preamble': ADDITIONAL_PREAMBLE,
    # Additional footer
    'footer': ADDITIONAL_FOOTER,
    # disable latex font inclusion (we will use xelatex)
    'fontpkg': '',
    'fontenc': '',
    'inputenc': '',
    'utf8extra': '',
    'fncychap': '\\usepackage[Sonny]{fncychap}',
    'releasename':
    # the following needs to be on a line of its own since it is 
    # replaced by a sed command in books/models.py
    u'', # RELEASENAME
}


# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  (master_doc, 'chronicle.tex',
   u'UNSERE FAMILIENGESCHICHTE', # TITLE
   u'',  # Author
   'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_use_parts = False

# If true, show page references after internal links.
latex_show_pagerefs = True

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
latex_appendices = ['appendix', ]

# If false, no module index is generated.
latex_domain_indices = False


latex_additional_files = [
        '../../../../familio/maps/static/png/%s.png' % x
        for x in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' ]

# -- Options for Epub output ----------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

