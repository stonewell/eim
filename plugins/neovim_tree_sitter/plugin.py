from yapsy.IPlugin import IPlugin

from .tree_sitter_langs import ensure_tree_sitter_langs

class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)

    ensure_tree_sitter_langs(self.ctx)

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor
