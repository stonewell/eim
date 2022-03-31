from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit


class LineNumberArea(QWidget):
  def __init__(self, editor):
    QWidget.__init__(self, editor)
    self._editor = editor

  def sizeHint(self):
    return QSize(self._editor.line_number_area_width(), 0)

  def paintEvent(self, event):
    self._editor.lineNumberAreaPaintEvent(event)


class Editor(QPlainTextEdit):
  def __init__(self):
    super().__init__()
    self.line_number_area = LineNumberArea(self)

    self.blockCountChanged[int].connect(self.update_line_number_area_width)
    self.updateRequest[QRect, int].connect(self.update_line_number_area)
    self.cursorPositionChanged.connect(self.highlight_current_line)

    self.update_line_number_area_width(0)
    self.highlight_current_line()

  def line_number_area_width(self):
    digits = 1
    max_num = max(1, self.blockCount())
    while max_num >= 10:
      max_num *= 0.1
      digits += 1

    space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
    return space

  def resizeEvent(self, e):
    super().resizeEvent(e)
    cr = self.contentsRect()
    width = self.line_number_area_width()
    rect = QRect(cr.left(), cr.top(), width, cr.height())
    self.line_number_area.setGeometry(rect)

  def lineNumberAreaPaintEvent(self, event):
    painter = QPainter(self.line_number_area)
    painter.fillRect(event.rect(), Qt.lightGray)
    block = self.firstVisibleBlock()
    block_number = block.blockNumber()
    offset = self.contentOffset()
    top = self.blockBoundingGeometry(block).translated(offset).top()
    bottom = top + self.blockBoundingRect(block).height()

    while block.isValid() and top <= event.rect().bottom():
      if block.isVisible() and bottom >= event.rect().top():
        number = str(block_number + 1)
        painter.setPen(Qt.black)
        width = self.line_number_area.width()
        height = self.fontMetrics().height()
        painter.drawText(0, top, width, height, Qt.AlignRight, number)

      block = block.next()
      top = bottom
      bottom = top + self.blockBoundingRect(block).height()
      block_number += 1

    # QPainter needs an explicit end() in PyPy. This will become a context manager in 6.3.
    painter.end()

  @Slot()
  def update_line_number_area_width(self, newBlockCount):
    self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

  @Slot()
  def update_line_number_area(self, rect, dy):
    if dy:
      self.line_number_area.scroll(0, dy)
    else:
      width = self.line_number_area.width()
      self.line_number_area.update(0, rect.y(), width, rect.height())

    if rect.contains(self.viewport().rect()):
      self.update_line_number_area_width(0)

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
