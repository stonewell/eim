import logging
import platform

from PySide6.QtCore import Slot, Qt, QRect, QSize, QMargins
from PySide6.QtWidgets import QStatusBar, QLabel

from pubsub import pub


class ModeLineArea(QStatusBar):

  def __init__(self, ctx, editor):
    super().__init__(editor)
    try:
      self._init(ctx, editor)

    except:
      logging.exception('init error')

  def _init(self, ctx, editor):
    self.editor_ = editor
    self.ctx_ = ctx

    self.ctx_.register_editor_viewport_handler(self)

    self.setSizeGripEnabled(False)

    self.editor_.updateRequest[QRect, int].connect(self.update_mode_line_area)
    self.mode_line_items_ = {}

    pub.subscribe(self.on_update_model_line, 'update_mode_line')

    l = QLabel()
    self.addWidget(l, 1)

    self.__apply_theme(self)

    # reupdate geometry to count margins
    self.update_geometry()

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
    cr = self.editor_.contentsRect()
    vms = self.ctx_.get_margins_for_handler(self) or QMargins(0, 0, 0, 0)

    cr -= vms

    height = self.mode_line_area_height()
    rect = QRect(cr.left(), cr.bottom() - height, cr.width(), height)

    if current_geometry != rect:
      self.setGeometry(rect)

  def get_editor_margin(self):
    return QMargins(0, 0, 0, self.mode_line_area_height())

  def __apply_theme(self, w):
    f_c = self.ctx_.get_theme_def_color('mode-line', 'foreground')
    b_c = self.ctx_.get_theme_def_color('mode-line', 'background')

    w.setStyleSheet(f'background-color:"{b_c.name()}";color:"{f_c.name()}";')

  def on_update_model_line(self, name, message, permanant):
    if name in self.mode_line_items_:
      self.mode_line_items_[name].setText(message)
    else:
      l = QLabel()
      l.setText(message)

      if permanant:
        self.insertPermanentWidget(0, l)
      else:
        self.insertWidget(0, l)

      self.mode_line_items_[name] = l
