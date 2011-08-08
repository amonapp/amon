# -*- coding: utf-8 -*-
#
# Amon documentation build configuration file, created by
# sphinx-quickstart on Thu Mar 03 09:29:25 2011.
#

import sys, os


extensions = ['sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

project = u'Amon'
copyright = u'2011, Martin Rusev'
version = '0.1'
release = '0.1'

# directories to ignore when looking for source files.
exclude_patterns = ['_build']



# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'trac'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

html_theme = 'amon'
html_theme_path = ['_theme']
html_static_path = ['_static']

html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}
html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html','relations.html' ],
}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# Output file base name for HTML help builder.
htmlhelp_basename = 'Amondoc'


# -- Options for LaTeX output --------------------------------------------------



# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'Amon.tex', u'Amon Documentation',
   u'Martin Rusev', 'manual'),
]


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'amon', u'Amon Documentation',
     [u'Martin Rusev'], 1)
]
