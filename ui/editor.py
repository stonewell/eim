from PySide6.QtCore import QSize
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

from core.builtin_commands import BuiltinCommands
from .textedit_mixin import TextEditMixin

class Editor(QPlainTextEdit, TextEditMixin):

  def __init__(self, ctx):
    QPlainTextEdit.__init__(self)
    TextEditMixin.__init__(self)

    self.setWindowTitle("EIM")

    self.ctx_ = ctx
    ctx.ui_helper.set_current_window(self)

    ctx.switch_behavior_context('editor')

    self.register_commands()
    self.bind_keys()

  def resizeEvent(self, e):
    super().resizeEvent(e)

  def sizeHint(self):
    return QSize(1024, 768)

  def focusInEvent(self, e):
    super().focusInEvent(e)

    self.ctx_.close_content_window()

    self.ctx_.switch_behavior_context('editor')

  def keyPressEvent(self, evt):
    super().keyPressEvent(evt)

  def cursor_position(self):
    return self.textCursor().position

