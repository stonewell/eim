import logging
from pubsub import pub

from yapsy.IPlugin import IPlugin

from PySide6.QtGui import QTextDocument
from PySide6.QtCore import QMargins

from core.builtin_commands import BuiltinCommands


class Plugin(IPlugin):
  SEARCH = 0
  REVERSE_SEARCH = 1
  SEARCH_REGEX = 2

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)
    return

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    try:
      self.__init_current_window(editor)
    except:
      logging.exception('set current window failed')

  def __init_current_window(self, editor):
    self.editor_ = editor

    self.search_history_ = {
        Plugin.SEARCH: [],
        Plugin.SEARCH_REGEX: [],
    }

    self.search_history_[Plugin.REVERSE_SEARCH] = self.search_history_[
        Plugin.SEARCH]

    self.ctx.register_command(
        BuiltinCommands.SEARCH,
        lambda ctx: self.show_input_window(ctx, Plugin.SEARCH), None, False)
    self.ctx.register_command(
        BuiltinCommands.REVERSE_SEARCH,
        lambda ctx: self.show_input_window(ctx, Plugin.REVERSE_SEARCH), None,
        False)
    self.ctx.register_command(
        BuiltinCommands.SEARCH_REGEX,
        lambda ctx: self.show_input_window(ctx, Plugin.SEARCH_REGEX), None,
        False)

    self.content_window_ = None

  def show_input_window(self, ctx, search_type):
    self.search_type_ = search_type

    self.current_history_ = history = self.search_history_[search_type]

    if self.content_window_ is not None:
      self.__do_search()
      return

    self.content_window_ = cw = ctx.create_input_content_window()

    self.text_edit_ = t = cw.text_edit_
    self.label_ = e = cw.label_widget_

    self.label_.setText(f'Search:{history[0] if len(history) > 0 else ""}')
    cw.set_input_history(history)

    self.text_edit_.returnPressed.connect(self.__execute_command)

    pub.sendMessage('viewport_changed')
    cw.show()

  def __execute_command(self):
    self.__do_save_search()

    self.ctx.close_content_window()
    self.content_window_ = None
    pub.sendMessage('viewport_changed')

  def __do_save_search(self):
    txt_to_search = self.text_edit_.text()

    if len(txt_to_search) == 0:
      return

    try:
      self.current_history_.remove(txt_to_search)
    except:
      pass

    self.current_history_.insert(0, txt_to_search)

  def __do_search(self):
    text_to_search = self.text_edit_.text()

    if len(text_to_search) == 0:
      if len(self.current_history_) == 0:
        return

      self.text_edit_.setText(self.current_history_[0])
      text_to_search = self.text_edit_.text()

    # do real search
    options = QTextDocument.FindFlags()

    if self.search_type_ == Plugin.REVERSE_SEARCH:
      options |= QTextDocument.FindBackward

    if text_to_search.lower() != text_to_search:
      options |= QTextDocument.FindCaseSensitively

    if self.editor_.find(text_to_search, options):
      self.editor_.centerCursor()
