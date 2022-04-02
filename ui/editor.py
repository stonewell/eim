from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit


class Editor(QPlainTextEdit):
  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

    self.cursorPositionChanged.connect(self.highlight_current_line)

    self.highlight_current_line()

  def resizeEvent(self, e):
    super().resizeEvent(e)

  @Slot()
  def highlight_current_line(self):
    extra_selections = []

    if not self.isReadOnly():
      selection = QTextEdit.ExtraSelection()

      line_color = QColor(Qt.yellow).lighter(160)
      selection.format.setBackground(line_color)

      selection.format.setProperty(QTextFormat.FullWidthSelection, True)

      selection.cursor = self.textCursor()
      selection.cursor.clearSelection()

      extra_selections.append(selection)

    self.setExtraSelections(extra_selections)
