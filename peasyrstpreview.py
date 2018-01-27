from urllib import parse as urlparse
from gi.repository import Gtk
from gi.repository import Geany
from gi.repository import GeanyScintilla
from gi.repository import Peasy
from reST import *


class ReStructuredTextPlugin(Peasy.Plugin):
    __gtype_name__ = "reStructuredTextPreview"
    file_types = ('reStructuredText',)
    
    def __init__(self):
        self.rest_win = RestructuredtextHtmlPanel()

    def do_enable(self):
        geany_data = self.geany_plugin.geany_data
        o = geany_data.object
        signals = ('document-reload', 'document-save', 'document-activate', 'document-new')
        self.notebook = geany_data.main_widgets.message_window_notebook
        self.page_num = self.notebook.append_page(self.rest_win, Gtk.Label('reST Preview'))
        self.rest_win.show_all()
        for signal in signals:
            o.connect(signal, self.on_document_notify)
        o.connect("editor-notify", self.on_editor_notify)
        return True

    def do_disable(self):
        self.notebook.remove_page(self.page_num)
        self.rest_win.clean_destroy()

    def check_selection_or_filetype(self, doc):
        sci = doc.editor.sci
        if doc.file_type.name in self.file_types:
            content = sci.get_contents(sci.get_length()+1)
            uri = urlparse.urljoin('file:', doc.file_name)
            doc.set_filetype(Geany.filetypes_index(Geany.FiletypeID.FILETYPES_MARKDOWN))
            return (content.strip(), uri)
        return ('Current Document is not reStructuredText Document', '')


    def update_window(self, text, uri, doc):
        Geany.msgwin_clear_tab(Geany.MessageWindowTabNum.MESSAGE)
        doc.editor.indicator_clear(Geany.Indicator.ERROR)
        if doc.file_type.name in self.file_types:
            errors = check_for_errors(text, uri)
            if errors:
                Geany.msgwin_switch_tab(Geany.MessageWindowTabNum.MESSAGE, True)
                for error in errors:
                    doc.editor.indicator_set_on_line(Geany.Indicator.ERROR, error.line-1)
                    err_msg = '{}:{}:{}'.format(error.type, error.line,  error.message)
                    Geany.msgwin_msg_add(err_msg, Geany.MsgColors.RED, error.line, doc)
            else:
               self.notebook.set_current_page(self.page_num)
        self.rest_win.update_view(text, uri)

    def on_document_notify(self, user_data, doc):
        text, uri = self.check_selection_or_filetype(doc)
        self.update_window(text, uri, doc)

    def on_editor_notify(self, g_obj, editor, nt):
        check = (nt.nmhdr.code == GeanyScintilla.SCN_MODIFIED and nt.length > 0) \
                and ((nt.modificationType & GeanyScintilla.SC_MOD_INSERTTEXT) \
                or (nt.modificationType & GeanyScintilla.SC_MOD_DELETETEXT))
        if check:
            text, uri = self.check_selection_or_filetype(editor.document)
            self.rest_win.update_view(text, uri)
