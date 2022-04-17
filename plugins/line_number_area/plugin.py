from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit

from yapsy.IPlugin import IPlugin


class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)
    return

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor
    self.line_number_area_ = LineNumberArea(self.editor_)


class LineNumberArea(QWidget):

  def __init__(self, editor):
    super().__init__(editor)
    self.editor_ = editor
    self.editor_.blockCountChanged[int].connect(
        self.update_line_number_area_width)
    self.editor_.updateRequest[QRect,
                               int].connect(self.update_line_number_area)
    self.update_line_number_area_width(0)

  def sizeHint(self):
    return QSize(self.line_number_area_width(), 0)

  def paintEvent(self, event):
    painter = QPainter(self)
    painter.fillRect(event.rect(), Qt.lightGray)
    block = self.editor_.firstVisibleBlock()
    block_number = block.blockNumber()
    offset = self.editor_.contentOffset()
    top = self.editor_.blockBoundingGeometry(block).translated(offset).top()
    bottom = top + self.editor_.blockBoundingRect(block).height()

    painter.setPen(Qt.black)
    width = self.width()
    height = self.editor_.fontMetrics().height()

    while block.isValid() and top <= event.rect().bottom():
      if block.isVisible() and bottom >= event.rect().top():
        number = str(block_number + 1)
        painter.drawText(0, top, width, height, Qt.AlignRight, number)

      block = block.next()
      top = bottom
      bottom = top + self.editor_.blockBoundingRect(block).height()
      block_number += 1

    # QPainter needs an explicit end() in PyPy. This will become a context manager in 6.3.
    painter.end()

  def line_number_area_width(self):
    digits = 1
    max_num = max(1, self.editor_.blockCount())
    while max_num >= 10:
      max_num *= 0.1
      digits += 1

    space = 3 + self.editor_.fontMetrics().horizontalAdvance('9') * digits
    return space

  @Slot()
  def update_line_number_area_width(self, newBlockCount):
    self.editor_.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

  @Slot()
  def update_line_number_area(self, rect, dy):
    self.update_geometry()

    if dy:
      self.scroll(0, dy)
    else:
      width = self.width()

      self.update(0, rect.y(), width, rect.height())

    if rect.contains(self.editor_.viewport().rect()):
      self.update_line_number_area_width(0)

  def update_geometry(self):
    current_geometry = self.geometry()
    cr = self.editor_.contentsRect()
    width = self.line_number_area_width()
    rect = QRect(cr.left(), cr.top(), width, cr.height())

    if current_geometry != rect:
      self.setGeometry(rect)
      self.update_line_number_area_width(0)
