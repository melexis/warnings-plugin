# -*- coding: utf-8 -*-

import errno
import os
import subprocess
import sys

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
    extensions.append('sphinxcontrib.spelling')
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'warning-plugin'
year = '2017-2019'
author = 'Bavo Van Achte'
copyright = '{0}, {1}'.format(year, author)

# The full version, including alpha/beta/rc tags.
from setuptools_scm import get_version
version = release = get_version(root="..")
# The short X.Y version.
#version = '.'.join(release.split('.')[:3])

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/melexis/warnings-plugin/issues/%s', '#%s'),
    'pr': ('https://github.com/melexis/warnings-plugin/pull/%s', 'PR #%s'),
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

linkcheck_ignore = [r'https://www\.mathworks\.com.+']
linkcheck_allowed_redirects = {
    # All HTTP redirections from the source URI to
    # the canonical URI will be treated as "working".
    r'https://www.bestpractices.dev/projects/\d+': r'https://www.bestpractices.dev/\w+/projects/\d+',
    'https://badge.fury.io/py/mlx.warnings.svg': r'https://\w+.cloudfront.net/badge.svg.+',
}

# Point to plantuml jar file
# confirm we have plantuml in the path
if 'nt' in os.name:
    plantuml_path = subprocess.check_output(["where", "/F", "plantuml.jar"])
    if not plantuml_path:
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
    if not plantuml_path:
        print("Can't find 'plantuml.jar' file.")
        print("You need to add path to 'plantuml.jar' file to your PATH variable.")
        sys.exit(os.strerror(errno.EPERM))
