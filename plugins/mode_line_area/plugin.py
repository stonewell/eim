from yapsy.IPlugin import IPlugin
from .mode_line_area import ModeLineArea


class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)
    return

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor
    self.mode_line_area_ = ModeLineArea(self.editor_)
