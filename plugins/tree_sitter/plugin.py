import logging

from yapsy.IPlugin import IPlugin
from pubsub import pub

from .tree_sitter_langs import ensure_tree_sitter_langs
from .tree_sitter_highlighter import TreeSitterSyntaxHighlighter
from .tree_sitter_tree import TreeSitterLangTree


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

    pub.subscribe(self.on_buffer_changed, 'buffer_changed')

  def on_buffer_changed(self, buf):
    if not hasattr(buf, 'highlighter_'):
      buf.tree_sitter_tree_ = TreeSitterLangTree(self.ctx, buf)
      buf.highlighter_ = TreeSitterSyntaxHighlighter(self.ctx, buf)
      logging.debug('install tree and syntax highlighter to buffer:{}'.format(
          buf.name()))
