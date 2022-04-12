from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QKeySequence, QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit


class Editor(QPlainTextEdit):

  def __init__(self, ctx):
    super().__init__()

    self.setWindowTitle("EIM")

    self.ctx_ = ctx

    ctx.switch_behavior_context('editor')

  def resizeEvent(self, e):
    super().resizeEvent(e)

  def sizeHint(self):
    return QSize(1024, 768)

  def focusInEvent(self, e):
    super().focusInEvent(e)

    self.ctx_.close_content_window()

    self.ctx_.switch_behavior_context('editor')

  def bind_keys(self):
    pass

  def keyPressEvent(self, evt):
    super().keyPressEvent(evt)
