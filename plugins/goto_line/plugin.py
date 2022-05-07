import logging

from PySide6.QtGui import QTextCursor

from yapsy.IPlugin import IPlugin

from core.builtin_commands import BuiltinCommands


class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    try:
      self.__init_current_window(editor)
    except:
      logging.exception('set current window failed')

  def __init_current_window(self, editor):
    self.editor_ = editor

    self.ctx.register_command(BuiltinCommands.GOTO_LINE,
                              self.__show_input_window, 'editor')

  def __show_input_window(self, ctx):
    self.content_window_ = cw = ctx.create_input_content_window()

    self.text_edit_ = t = cw.text_edit_
    self.label_ = e = cw.label_widget_

    self.label_.setText(f'Goto Line:')

    self.text_edit_.returnPressed.connect(self.__execute_command)

    cw.show()

  def __execute_command(self):
    try:
      self.__do_goto_line()
    except:
      logging.exception('goto line failed')
    self.ctx.close_content_window()

  def __do_goto_line(self):
    txt = self.text_edit_.text().strip()

    if len(txt) == 0:
      return

    new_l = int(txt)

    if new_l <= 0:
      return

    l, c, tl = self.ctx.get_row_and_col()

    if new_l > tl:
      new_l = tl

    if new_l == l:
      return

    tc = self.editor_.textCursor()

    moved = tc.movePosition(QTextCursor.Down if new_l > l else QTextCursor.Up,
                            QTextCursor.MoveAnchor, abs(l - new_l))

    if moved:
      self.editor_.setTextCursor(tc)
      self.editor_.ensureCursorVisible()
      self.editor_.centerCursor()
