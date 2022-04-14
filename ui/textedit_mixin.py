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
        BuiltinCommands.PREV_LINE, lambda ctx: self.move_cursor(
            QTextCursor.Up, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.NEXT_LINE, lambda ctx: self.move_cursor(
            QTextCursor.Down, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.PREV_CHAR, lambda ctx: self.move_cursor(
            QTextCursor.Left, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.NEXT_CHAR, lambda ctx: self.move_cursor(
            QTextCursor.Right, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.END_OF_LINE, lambda ctx: self.move_cursor(
            QTextCursor.EndOfLine, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.START_OF_LINE, lambda ctx: self.move_cursor(
            QTextCursor.StartOfLine, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.PREV_WORD, lambda ctx: self.move_cursor(
            QTextCursor.PreviousWord, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(
        BuiltinCommands.NEXT_WORD, lambda ctx: self.move_cursor(
            QTextCursor.NextWord, QTextCursor.MoveAnchor
            if not self.is_marker_active() else QTextCursor.KeepAnchor), None,
        False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_PAGE, self.__next_page, None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.PREV_PAGE, self.__prev_page, None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.SELECT_ALL,
                           lambda ctx: self.select_all(), None, False)
    self.ctx_.hook_command(BuiltinCommands.PASTE, lambda ctx: self.paste(),
                           None, False)
    self.ctx_.hook_command(BuiltinCommands.COPY, lambda ctx: self.copy(), None,
                           False)
    self.ctx_.hook_command(BuiltinCommands.CUT, lambda ctx: self.cut(), None,
                           False)

  def __next_page(self, ctx):
    self._page_up_down(ctx, True)

  def __prev_page(self, ctx):
    self._page_up_down(ctx, False)

  def _page_up_down(self, ctx, pageDown):
    logging.debug('text edit mixin page up down')
    pass
