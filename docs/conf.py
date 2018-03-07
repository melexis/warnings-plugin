# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys, os, subprocess

# Append src directory to path so that autodoc can find the python module
sys.path.append("src")


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinxcontrib.plantuml',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'warning-plugin'
year = '2017'
author = 'Bavo Van Achte'
copyright = '{0}, {1}'.format(year, author)
version = release = '0.1.0'

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/melexis/warnings-plugin/issues/%s', '#'),
    'pr': ('https://github.com/melexis/warnings-plugin/pull/%s', 'PR #'),
}
import sphinx_py3doc_enhanced_theme
html_theme = "sphinx_py3doc_enhanced_theme"
html_theme_path = [sphinx_py3doc_enhanced_theme.get_html_theme_path()]
html_theme_options = {
    'githuburl': 'https://github.com/melexis/warnings-plugin'
}

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

# Point to plantuml jar file
# confirm we have plantuml in the path
if 'nt' in os.name:
    plantuml_path = subprocess.check_output(["where", "/F", "plantuml.jar"])
    if not plantuml_path :
        print("Can't find 'plantuml.jar' file.")
        print("You need to add path to 'plantuml.jar' file to your PATH variable.")
        sys.exit(os.strerror(errno.EPERM))
    plantuml = plantuml_path.decode("utf-8")
    plantuml = plantuml.rstrip('\n\r')
    plantuml = plantuml.replace('"', '')
    plantuml = plantuml.replace('\\', '//')
    plantuml = 'java -jar' + ' ' + plantuml
else:
    plantuml_path = subprocess.check_output(["whereis", "-u", "plantuml"])
    if not plantuml_path :
        print("Can't find 'plantuml.jar' file.")
        print("You need to add path to 'plantuml.jar' file to your PATH variable.")
        sys.exit(os.strerror(errno.EPERM))


