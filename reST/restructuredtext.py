# -*- coding: utf-8 -*-

# restructuredtext.py - reStructuredText HTML preview panel
#
# Copyright (C) 2015 - Peter Bittner
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

try:
    from gi import pygtkcompat
except ImportError:
    pygtkcompat = None

if pygtkcompat is not None:
    pygtkcompat.enable()
    pygtkcompat.enable_gtk(version='3.0')

import gtk as Gtk
try:
    from gi.repository import WebKit
except ImportError:
    import webkit as WebKit
from docutils.core import publish_parts
from os.path import abspath, dirname, join


class RestructuredtextHtmlPanel(Gtk.ScrolledWindow):
    """
    A Gtk panel displaying HTML rendered from ``.rst`` source code.
    """
    MIME_TYPE = 'text/html'
    ENCODING = 'UTF-8'
    TEMPLATE = u"""<!DOCTYPE html>
    <html>
    <head>
        <style type="text/css">
            {css}
        </style>
    </head>
    <body>
    {body}
    </body>
    </html>
    """

    def __init__(self, styles_filename='restructuredtext.css'):
        super(RestructuredtextHtmlPanel, self).__init__()

        module_dir = dirname(abspath(__file__))
        css_file = join(module_dir, styles_filename)
        with open(css_file, 'r') as styles:
            self.styles = styles.read()

        self.set_policy(Gtk.POLICY_NEVER, Gtk.POLICY_AUTOMATIC)
        self.set_shadow_type(Gtk.SHADOW_NONE)
        self.view = WebKit.WebView()
        self.add(self.view)
        self.view.show()

    def update_view(self, text, base_uri):
        html = publish_parts(text, writer_name='html')['html_body']
        self.view.load_string(self.TEMPLATE.format(
            body=html, css=self.styles
        ), self.MIME_TYPE, self.ENCODING, base_uri)

    def clear_view(self):
        self.view.load_string('', self.MIME_TYPE, self.ENCODING, '')
