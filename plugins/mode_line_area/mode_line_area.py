from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget
from pubsub import pub


class ModeLineArea(QWidget):

  def __init__(self, editor):
    super().__init__(editor)
    self.editor_ = editor
    self.editor_.blockCountChanged[int].connect(
        self.update_mode_line_area_height)
    self.editor_.updateRequest[QRect, int].connect(self.update_mode_line_area)
    self.update_mode_line_area_height(0)

  def sizeHint(self):
    return QSize(0, self.mode_line_area_height())

  #def paintEvent(self, event):
  #  pass

  def mode_line_area_height(self):
    space = 4 + self.editor_.fontMetrics().lineSpacing()
    return space

  @Slot()
  def update_mode_line_area_height(self, newBlockCount):
    pub.sendMessage('viewport_changed')

  @Slot()
  def update_mode_line_area(self, rect, dy):
    self.update_geometry()

    if dy:
      self.scroll(0, dy)
    else:
      height = self.height()

      self.update(0, rect.y(), rect.width(), height)

    if rect.contains(self.editor_.viewport().rect()):
      self.update_mode_line_area_height(0)

  def update_geometry(self):
    current_geometry = self.geometry()
    cr = self.editor_.contentsRect()
    height = self.mode_line_area_height()
    rect = QRect(cr.left(), cr.top(), cr.width(), height)

    if current_geometry != rect:
      self.setGeometry(rect)
      self.update_mode_line_area_height(0)
