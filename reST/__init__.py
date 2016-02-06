# -*- coding: utf-8 -*-

# __init__.py - HTML preview for reStructuredText (.rst) plugin
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

# from gi.repository import GObject, Gedit

from .restructuredtext import RestructuredtextHtmlPanel
from .lint import check_for_errors

__all__ = ['RestructuredtextHtmlPanel', 'check_for_errors']
