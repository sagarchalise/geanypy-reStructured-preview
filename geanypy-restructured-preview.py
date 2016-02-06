import urlparse
from gettext import gettext as _
from gi.repository import Gtk
import geany
from reST import *


class ReStructuredTextPlugin(geany.Plugin):
    __plugin_name__ = _("reStructuredText Preview")
    __plugin_version__ = _("0.1")
    __plugin_description__ = _("reStructured Text Preview Panel in message window.")
    __plugin_author__ = _("Sagar Chalise <chalisesagar@gmail.com>")
    file_types = ('reStructuredText',)

    def __init__(self):
        signals = ('document-reload', 'document-save', 'document-activate', 'document-close')
        self.rest_win = RestructuredtextHtmlPanel()
        geany.main_widgets.message_window_notebook.append_page(self.rest_win, Gtk.Label(self.name))
        self.rest_win.show_all()
        for signal in signals:
            geany.signals.connect(signal, self.on_document_notify)


    def check_selection_or_filetype(self, doc):
        sci = doc.editor.scintilla
        if doc.file_type.name in self.file_types:
            content = sci.get_contents()
            uri = urlparse.urljoin('file:', doc.file_name)
            return (content.strip(), uri)
        return ('No ReStructured Text', '')
        # if sci.has_selection():
            # return (sci.get_selection_contents(), '')

    def update_window(self, text, uri, doc):
        msgwin = geany.msgwindow
        msgwin.clear_tab(msgwin.TAB_MESSAGE)
        doc.editor.indicator_clear(geany.editor.INDICATOR_ERROR)
        if doc.file_type.name in self.file_types:
            errors = check_for_errors(text, uri)
            if errors:
                msgwin.switch_tab(msgwin.TAB_MESSAGE, True)
                for error in errors:
                    doc.editor.indicator_set_on_line(geany.editor.INDICATOR_ERROR, error.line-1)
                    err_msg = '{}:{}:{}'.format(error.type, error.line,  error.message)
                    msgwin.msg_add(err_msg, msgwin.COLOR_RED, error.line, doc)
        self.rest_win.update_view(text, uri)

    def on_document_notify(self, user_data, doc):
        text, uri = self.check_selection_or_filetype(doc)
        self.update_window(text, uri, doc)
