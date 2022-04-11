from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QListWidget


class ContentWindow(QWidget):

  def __init__(self, content_widget, ctx, parent=None):
    super().__init__(parent)

    self.parent_widget_ = parent
    self.ctx_ = ctx
    self.content_widget_ = content_widget

    self.text_edit_ = QLineEdit()

    layout = QVBoxLayout()
    layout.addWidget(self.content_widget_)
    layout.addWidget(self.text_edit_)
    self.setLayout(layout)

    self.text_edit_.setFocus(Qt.ActiveWindowFocusReason)
    self.update_geometry()

    ctx.switch_behavior_context('content_window')

  def update_geometry(self):
    cr = self.parent_widget_.contentsRect()

    self.setGeometry(
        QRect(cr.left(),
              cr.bottom() - cr.height() / 4, cr.width(),
              cr.height() / 4))

  def sizeHint(self):
    cr = self.parent_widget_.contentsRect()

    return QSize(cr.width(), cr.height() / 4)

  def close(self):
    super().close()

    self.ctx_.switch_behavior_context()


class ListContentWindow(ContentWindow):

  def __init__(self, ctx, parent=None):
    super().__init__(QListWidget(), ctx, parent)

    cc = self.ctx_.get_behavior_context('content_window')
    lc = self.ctx_.get_behavior_context('list_content_window', cc)

    self.register_commands()
    self.bind_keys()

    self.ctx_.switch_behavior_context('list_content_window')

    self.content_widget_.itemSelectionChanged.connect(
        self.item_selection_changed)

  def register_commands(self):
    self.ctx_.hook_command('prev', self.prev_command, 'list_content_window',
                           False)
    self.ctx_.hook_command('next', self.next_command, 'list_content_window',
                           False)

  def bind_keys(self):
    pass

  def prev_command(self, ctx):
    count = self.content_widget_.count()
    cur_row = self.content_widget_.currentRow()

    if cur_row - 1 >= 0:
      self.content_widget_.setCurrentRow(cur_row - 1)

  def next_command(self, ctx):
    count = self.content_widget_.count()
    cur_row = self.content_widget_.currentRow()

    if cur_row + 1 < count:
      self.content_widget_.setCurrentRow(cur_row + 1)

  def item_selection_changed(self):
    self.text_edit_.setText(self.content_widget_.currentItem().text())
