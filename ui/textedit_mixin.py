from PySide6.QtGui import QTextCursor

from core.builtin_commands import BuiltinCommands


class TextEditMixin(object):
  def bind_keys(self):
    pass

  def register_commands(self):
    self.ctx_.hook_command(BuiltinCommands.PREV_LINE,
                           lambda ctx: self.moveCursor(QTextCursor.Up, QTextCursor.MoveAnchor),
                           None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_LINE,
                           lambda ctx: self.moveCursor(QTextCursor.Down, QTextCursor.MoveAnchor),
                           None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.PREV_CHAR,
                           lambda ctx: self.moveCursor(QTextCursor.Left, QTextCursor.MoveAnchor),
                           None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_CHAR,
                           lambda ctx: self.moveCursor(QTextCursor.Right, QTextCursor.MoveAnchor),
                           None,
                           False)
