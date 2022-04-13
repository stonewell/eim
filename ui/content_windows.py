import logging

from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
from PySide6.QtWidgets import QListWidget
from fuzzywuzzy import fuzz

from core.builtin_commands import BuiltinCommands
from .marker_mixin import MarkerMixin

class ContentWindowLineEdit(QLineEdit):
  def __init__(self, ctx, *args):
    super().__init__(*args)

  def keyPressEvent(self, evt):
    key = evt.keyCombination().toCombined()
    if key == Qt.Key_Return or key == Qt.Key_Enter:
      evt.accept()
      self.returnPressed.emit()
      return

    super().keyPressEvent(evt)

class ContentWindow(QWidget, MarkerMixin):

  def __init__(self, content_widget, ctx, parent=None):
    QWidget.__init__(self, parent)
    MarkerMixin.__init__(self)

    self.parent_widget_ = parent
    self.ctx_ = ctx
    self.content_widget_ = content_widget

    self.text_edit_ = ContentWindowLineEdit(ctx)

    layout = QVBoxLayout()
    layout.addWidget(self.content_widget_)
    layout.addWidget(self.text_edit_)
    self.setLayout(layout)

    self.text_edit_.setFocus(Qt.ActiveWindowFocusReason)
    self.update_geometry()

    ctx.switch_behavior_context('content_window')

  def cursor_position(self):
    return self.text_edit_.cursorPosition()

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(BuiltinCommands.PREV_CHAR,
                           lambda ctx: self.text_edit_.cursorBackward(self.is_marker_active()),
                           None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_CHAR,
                           lambda ctx: self.text_edit_.cursorForward(self.is_marker_active()),
                           None,
                           False)

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
    self.text_edit_.textEdited[str].connect(self.on_text_edited)

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(BuiltinCommands.PREV_LINE, self.prev_command, 'list_content_window',
                           False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_LINE, self.next_command, 'list_content_window',
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

  def on_text_edited(self, txt):
    for row in range(self.content_widget_.count()):
      item = self.content_widget_.item(row)
      ratio = fuzz.partial_ratio(txt, item.text())

      logging.debug('ratio:{} for {} -> {}'.format(ratio, txt, item.text()))
      item.setHidden(ratio <= 30 and len(txt) > 0)
