import logging

from PySide6.QtGui import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QEvent, QObject, QCoreApplication, Qt

from .content_windows import ListContentWindow


class UIHelper(QObject):

  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

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
    self.ctx_.register_command('quit', lambda c: QCoreApplication.quit())

  def bind_keys(self):
    self.ctx_.bind_key('Ctrl+Q', 'quit')

  def focus_editor(self):
    self.editor_.setFocus(Qt.ActiveWindowFocusReason)
