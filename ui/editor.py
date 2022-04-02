from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit


class Editor(QPlainTextEdit):
  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

  def resizeEvent(self, e):
    super().resizeEvent(e)
