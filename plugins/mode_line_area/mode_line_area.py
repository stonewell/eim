from PySide6.QtCore import Slot, Qt, QRect, QSize, QMargins
from PySide6.QtWidgets import QStatusBar, QLabel

from pubsub import pub


class ModeLineArea(QStatusBar):

  def __init__(self, ctx, editor):
    super().__init__(editor)
    self.editor_ = editor
    self.ctx_ = ctx

    self.ctx_.register_editor_viewport_handler(self)

    self.setSizeGripEnabled(False)

    self.editor_.updateRequest[QRect, int].connect(self.update_mode_line_area)

    l = QLabel()
    self.addPermanentWidget(l)
    l.setText('Line Numbers')

    l = QLabel()
    self.addWidget(l, 0)
    l.setText('Buffer info xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

    l = QLabel()
    self.addWidget(l, 1)

  def sizeHint(self):
    return QSize(0, self.mode_line_area_height())

  def mode_line_area_height(self):
    space = 4 + self.editor_.fontMetrics().lineSpacing()
    return space

  @Slot()
  def update_mode_line_area(self, rect, dy):
    self.update_geometry()

  def update_geometry(self):
    current_geometry = self.geometry()
    cr = self.editor_.contentsRect() - self.editor_.viewportMargins()

    height = self.mode_line_area_height()
    rect = QRect(cr.left(), cr.bottom(), cr.width(), height)

    if current_geometry != rect:
      self.setGeometry(rect)

  def get_editor_margin(self):
    return QMargins(0, 0, 0, self.mode_line_area_height())
