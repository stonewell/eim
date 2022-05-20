import logging
from pubsub import pub

from yapsy.IPlugin import IPlugin

from PySide6.QtGui import QTextDocument, QTextCursor
from PySide6.QtCore import QMargins
from PySide6.QtCore import QRegularExpression

from eim.core.builtin_commands import BuiltinCommands

SPLIT_CHAR = ' → '


class Plugin(IPlugin):
  REPLACE = 0
  REPLACE_REGEX = 1

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

    self.replace_history_ = {
        Plugin.REPLACE: [],
        Plugin.REPLACE_REGEX: [],
    }

    self.ctx.register_command(
        BuiltinCommands.REPLACE,
        lambda ctx: self.show_input_window(ctx, Plugin.REPLACE), None, False)
    self.ctx.register_command(
        BuiltinCommands.REPLACE_REGEX,
        lambda ctx: self.show_input_window(ctx, Plugin.REPLACE_REGEX), None,
        False)

    self.content_window_ = None

  def show_input_window(self, ctx, replace_type):
    try:
      self.__show_input_window(ctx, replace_type)
    except:
      logging.exception('show input window failed')

  def __show_input_window(self, ctx, replace_type):
    self.replace_type_ = replace_type

    self.current_history_ = history = self.replace_history_[replace_type]

    self.content_window_ = cw = ctx.create_input_content_window()

    self.text_edit_ = t = cw.text_edit_
    self.label_ = e = cw.label_widget_

    if len(history) > 0:
      s, r = history[0]
      self.label_.setText(f'Replace: (default {s}{SPLIT_CHAR}{r})')
    else:
      self.label_.setText(f'Replace: ')

    cw.set_input_history(history)

    self.text_edit_.returnPressed.connect(self.__execute_command)

    pub.subscribe(self.__on_window_close, 'content_window_closed')

    self.search_pattern_ = None
    cw.set_input_content_delegate(self)

    cw.show()

  def get_history_display_text(self, history):
    s, r = history
    return f'{s}{SPLIT_CHAR}{r}'

  def __on_window_close(self, ctx):
    if ctx != self.ctx:
      return

    self.content_window_ = None
    self.search_pattern_ = None

  def __execute_command(self):
    s = self.search_pattern_
    r = self.text_edit_.text()

    if self.search_pattern_ is None:
      txt_to_search = self.text_edit_.text()

      if len(txt_to_search) > 0:
        pos = txt_to_search.find(SPLIT_CHAR)
        if pos < 0:
          self.search_pattern_ = txt_to_search
          self.label_.setText(f'Replace {txt_to_search} with:')
          self.text_edit_.setText('')
          return

        s = txt_to_search[:pos]
        r = txt_to_search[pos + len(SPLIT_CHAR):]

    self.__do_replace(s, r)

    self.ctx.close_content_window()
    self.content_window_ = None

  def __do_save_replace(self, text_to_search, text_to_replace):
    pattern = (text_to_search, text_to_replace)

    try:
      self.current_history_.remove(pattern)
    except:
      pass

    self.current_history_.insert(0, pattern)

  def __do_replace(self, text_to_search, text_to_replace):
    if text_to_search is None or len(text_to_search) == 0:
      if len(self.current_history_) == 0:
        return

      text_to_search, text_to_replace = self.current_history_[0]

    self.__do_save_replace(text_to_search, text_to_replace)

    # do real replace
    options = QTextDocument.FindFlags()

    options |= QTextDocument.FindCaseSensitively

    logging.debug(
        f'replace type:{self.replace_type_}, replace:[{text_to_search}] with [{text_to_replace}]'
    )

    tc = self.editor_.textCursor()
    document = self.ctx.current_buffer_.document_

    if tc.hasSelection():
      selection_start = tc.selectionStart()
      selection_end = tc.selectionEnd()
    else:
      selection_start = tc.position()
      selection_end = None

    edit_started = False
    while True:
      c = document.find(
          QRegularExpression(text_to_search)
          if self.replace_type_ == Plugin.REPLACE_REGEX else text_to_search,
          selection_start, options)

      if c is None or not c.hasSelection():
        logging.debug('replace not found match')
        break

      match_start = c.selectionStart()
      match_end = c.selectionEnd()

      if selection_end is not None and (match_start >= selection_end
                                        or match_end > selection_end):
        logging.debug(
            f'replace match {match_start}->{match_end}, exceed:{selection_end}'
        )
        break

      if edit_started:
        c.joinPreviousEditBlock()
      else:
        c.beginEditBlock()
      c.insertText(text_to_replace)
      c.endEditBlock()

      edit_started = True

      selection_start = match_start + len(text_to_replace)
