from PySide6.QtGui import QTextCursor

from eim.core.builtin_commands import BuiltinCommands


class Marker(object):

  def __init__(self):
    self.active_ = True
    self.marker_pos_ = None


class MarkerMixin(object):

  def __init__(self, *args):
    super().__init__()
    self.marker_ = None

  def is_marker_active(self):
    return self.marker_ is not None and self.marker_.active_

  def active_marker(self, v=True):
    if self.marker_ is not None:
      self.marker_.active_ = v

    self.clear_selection()

  def push_marker(self):
    self.marker_ = Marker()
    self.marker_.marker_pos_ = self.cursor_position()
    self.marker_.active_ = True

  def bind_keys(self):
    pass

  def register_commands(self):
    self.ctx_.hook_command(BuiltinCommands.PUSH_MARK,
                           lambda ctx: self.push_marker(), None, False)
    self.ctx_.hook_command(BuiltinCommands.CANCEL, self.cmd_cancel, None,
                           False)

  def cmd_cancel(self, ctx):
    self.active_marker(False)
