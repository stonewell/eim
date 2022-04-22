import os
import logging

from PySide6.QtGui import QFont, QKeySequence, QShortcut, QTextDocument, QColor, QPalette
from PySide6.QtWidgets import QApplication, QPlainTextDocumentLayout
from PySide6.QtCore import QEvent, QObject, QCoreApplication, Qt

from .content_windows import ListContentWindow
from core.builtin_commands import BuiltinCommands


class EIMApplication(QApplication):

  def __init__(self, *args):
    super().__init__(*args)


class UIHelper(QObject):

  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

    if self.ctx_.args.debug > 2:
      os.environ['QT_DEBUG_PLUGINS'] = '1'

  def create_application(self):
    self.ctx_.app = app = EIMApplication()

    self.__apply_theme(app)

    return app

  def init_commands_and_key_bindings(self):
    self.register_commands()
    self.bind_keys()

  def get_font(self):
    fConfig = self.ctx_.config.get('app/font')

    f = None

    if isinstance(fConfig, str):
      f = QFont()
      f.fromString(fConfig)
    else:
      family = fConfig.get('family', QFont().defaultFamily())
      ptSize = fConfig.get('size', 14)
      bold = fConfig.get('bold', False)
      italic = fConfig.get('italic', False)

      logging.debug('family:{}, ptSize:{}, bold:{}, italic:{}'.format(
          family, ptSize, bold, italic))

      f = QFont(family, ptSize, QFont.Bold if bold else -1, italic)

    return f

  def set_current_window(self, editor):
    self.editor_ = editor

    self.ctx_.update_plugins_with_current_window(editor)

  def bind_key(self, keyseq, callable, binding_widget=None):
    logging.debug('bind keyseq:{}'.format(keyseq))
    seq = QKeySequence(keyseq)
    sc = QShortcut(seq,
                   self.editor_ if binding_widget is None else binding_widget)
    sc.activated.connect(callable)
    sc.activatedAmbiguously.connect(callable)

  def create_list_content_window(self):
    content_window = ListContentWindow(self.ctx_, self.editor_)

    return content_window

  def register_commands(self):
    self.ctx_.register_command(BuiltinCommands.QUIT,
                               lambda c: QCoreApplication.quit())

  def bind_keys(self):
    pass

  def focus_editor(self):
    self.editor_.setFocus(Qt.ActiveWindowFocusReason)

  def create_document(self, content):
    doc = QTextDocument(content)
    layout = QPlainTextDocumentLayout(doc)
    doc.setDocumentLayout(layout)

    return doc

  def update_document(self, buffer, load_doc):
    if load_doc:
      self.editor_.setDocument(buffer.document_)
    else:
      buffer.document_ = self.editor_.document()

  def get_document_content(self, document):
    return document.toPlainText()

  def get_color(self, c):
    color = QColor()

    color.setNamedColor(c)

    return color

  def __apply_theme(self, app):
    font = self.get_font()

    if font:
      app.setFont(font)

    p = app.palette()

    f_c = self.ctx_.get_theme_def_color('default', 'foreground')
    b_c = self.ctx_.get_theme_def_color('default', 'background')

    p.setColor(QPalette.Active, QPalette.Base, b_c)
    p.setColor(QPalette.Active, QPalette.Text, f_c)

    #line_color = self.ctx_.get_theme_def_color(
    #    'highlight', 'background', p.color(QPalette.Active,
    #                                       QPalette.Highlight))
    #p.setColor(QPalette.Active, QPalette.Highlight, Qt.yellow)
    #highlight_text_color = self.ctx_.get_theme_def_color(
    #    'highlight', 'foreground')
    #p.setColor(QPalette.Active, QPalette.HighlightedText, highlight_text_color)

    app.setPalette(p)
