import os
import runpy
from urllib import parse as urlparse
from gi.repository import Gtk
from gi.repository import Geany
from gi.repository import Peasy
from reST import *
try:
    import sphinx
except ImportError:
    sphinx = None

def check_for_sphinx(filedir):
    """Check for sphinx based on dir and stop if it nears home.
    Args:
        filedir(str): path of open doc
    """
    if not sphinx:
        return '', False
    conf = os.path.join(filedir, 'conf.py')
    if not os.path.isfile(conf):
        if len(filedir.split('/')) <= 3:
            return '', False
        return check_for_sphinx(os.path.dirname(filedir))
    #  extensions = {}
    try:
        gd = runpy.run_path(conf)
    except Exception as e:
        print(e)
        pass
    else:
        extensions = gd.get('extensions', []) or []
        if extensions and any('sphinx' in k for k in extensions):
            return filedir, True
    return '', False
    
class ReStructuredTextPlugin(Peasy.Plugin):
    __gtype_name__ = "reStructuredTextPreview"
    is_sphinx = False

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

    def update_window(self, doc):
        uri = urlparse.urljoin('file:', doc.file_name)
        #  Geany.msgwin_clear_tab(Geany.MessageWindowTabNum.MESSAGE)
        #  doc.editor.indicator_clear(Geany.Indicator.ERROR)
        if doc.file_type.id == Geany.FiletypeID.FILETYPES_REST:
            sci = doc.editor.sci
            content = sci.get_contents(sci.get_length()+1)
            text = content.strip()
            #  errors = check_for_errors(text, uri)
            #  if errors:
                #  pass
                #  Geany.msgwin_switch_tab(Geany.MessageWindowTabNum.MESSAGE, True)
                #  for error in errors:
                    #  doc.editor.indicator_set_on_line(Geany.Indicator.ERROR, error.line-1)
                    #  err_msg = '{}:{}:{}'.format(error.type, error.line,  error.message)
                    #  Geany.msgwin_msg_add(err_msg, Geany.MsgColors.RED, error.line, doc)
            #  else:
            self.notebook.set_current_page(self.page_num)
        else:
            text = 'Current Document is not reStructuredText Document'
        self.rest_win.update_view(text, uri)

    def on_document_notify(self, user_data, doc):
        srcdir = None
        rp = doc.real_path
        if sphinx and rp:
            """ Check sphinx conf in file open directory and move up. """
            srcdir, self.is_sphinx = check_for_sphinx(os.path.dirname(rp))
        if self.is_sphinx and srcdir:
            """ Sphinx Conf found then use sphinx source and build parallel directory. """
            if doc.file_type.id != Geany.FiletypeID.FILETYPES_REST:
                self.update_window(doc)
                return
            base = os.path.dirname(srcdir)
            builddir = os.path.join(base, 'build')
            cmd = [srcdir, builddir]
            try:
                sphinx.main(cmd)
            except Exception as e:
                self.rest_win.update_view("OOPS! Sphinx Call Issue\n{}".format(e), "file:///hhh")
            else:
                if not os.path.isdir(builddir):
                    self.rest_win.update_view('OOPS! No Sphinx Build', "file:///hhh")
                    return
                hp = rp.replace(srcdir, '')
                hp = os.path.join(builddir, hp[1:] if hp.startswith('/') else hp)
                hp = hp.replace('.rst', '.html')
                if not os.path.isfile(hp):
                    self.rest_win.update_window('OOPS! No Sphinx Build', 'file:///hhh')
                    return
                self.rest_win.update_view_with_uri(urlparse.urljoin('file:', hp))
                self.notebook.set_current_page(self.page_num)
        else:
            self.update_window(doc)

    def on_editor_notify(self, g_obj, editor, nt):
        pass
        #  check = (nt.nmhdr.code == GeanyScintilla.SCN_MODIFIED and nt.length > 0) \
                #  and ((nt.modificationType & GeanyScintilla.SC_MOD_INSERTTEXT) \
                #  or (nt.modificationType & GeanyScintilla.SC_MOD_DELETETEXT))
        #  doc = editor.document
        #  if check and doc.file_type.name in self.file_types and not self.is_sphinx:
            #  text = self.check_selection_or_filetype(editor.document)
            #  self.update_window(text, editor.document)
