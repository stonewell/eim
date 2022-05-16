import logging

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QLabel

from eim.core.builtin_commands import BuiltinCommands
from .content_windows import ContentWindow


class InputContentWindow(ContentWindow):

  def __init__(self, ctx, parent=None):
    ContentWindow.__init__(self, ctx, parent)

    cc = self.ctx_.get_behavior_context('content_window')
    ic = self.ctx_.get_behavior_context('input_content_window')
    ic.set_parent_context(cc)

    self.input_history_ = []
    self.current_input_item_ = -1

    self.ctx_.switch_behavior_context('input_content_window')

    self.set_input_content_delegate(self)

  def set_input_content_delegate(self, delegate):
    self.delegate_ = delegate

  def get_history_display_text(self, history):
    return history

  def create_content_widget(self):
    self.label_widget_ = QLabel()
    return self.label_widget_

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(BuiltinCommands.PREV_LINE, self.__prev_item,
                           'input_content_window', False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_LINE, self.__next_item,
                           'input_content_window', False)

  def bind_keys(self):
    super().bind_keys()

  def __prev_item(self, ctx):
    if len(self.input_history_) == 0:
      return

    if self.current_input_item_ >= len(self.input_history_) - 1:
      return

    self.current_input_item_ += 1

    self.__set_current_item()

  def __set_current_item(self):
    if self.current_input_item_ < 0 or self.current_input_item_ >= len(
        self.input_history_):
      return

    self.text_edit_.setText(self.delegate_.get_history_display_text(self.input_history_[self.current_input_item_]))

  def __next_item(self, ctx):
    if len(self.input_history_) == 0:
      return

    if self.current_input_item_ < 0:
      return

    self.current_input_item_ -= 1

    self.__set_current_item()

  def update_geometry(self):
    cr = self.parent_widget_.contentsRect()
    vm = self.parent_widget_.viewportMargins()

    height = self.layout_.sizeHint().height()

    self.setGeometry(
        QRect(cr.left() + vm.left(),
              cr.bottom() - height - vm.bottom(),
              cr.width() - vm.left() - vm.right(), height))

  def sizeHint(self):
    cr = self.parent_widget_.contentsRect()

    height = self.layout_.sizeHint().height()

    return QSize(cr.width(), height)

  def set_input_history(self, history):
    self.input_history_ = history
    self.current_input_item_ = -1
