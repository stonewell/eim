from PySide6.QtGui import QTextCursor

from core.builtin_commands import BuiltinCommands
from .marker_mixin import MarkerMixin


class TextEditMixin(MarkerMixin):
  def __init__(self):
    super().__init__()

  def bind_keys(self):
    super().bind_keys()

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(
        BuiltinCommands.PREV_LINE, lambda ctx: self.moveCursor(
            QTextCursor.Up, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.NEXT_LINE, lambda ctx: self.moveCursor(
            QTextCursor.Down, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.PREV_CHAR, lambda ctx: self.moveCursor(
            QTextCursor.Left, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.NEXT_CHAR, lambda ctx: self.moveCursor(
            QTextCursor.Right, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
