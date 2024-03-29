import logging

from yapsy.IPlugin import IPlugin
from pubsub import pub

from PySide6.QtWidgets import QListWidgetItem

from .tree_sitter_langs import ensure_tree_sitter_langs, get_lang_names
from .tree_sitter_highlighter import TreeSitterSyntaxHighlighter
from .tree_sitter_tree import TreeSitterLangTree
from .tree_sitter_autoindent import TreeSitterAutoIndent


class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

    self.indent_ = None
    self.content_window_ = None

  def activate(self):
    IPlugin.activate(self)

    ensure_tree_sitter_langs(self.ctx)

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor
    self.selected_langs_ = []

    pub.subscribe(self.on_buffer_changed, 'buffer_changed')
    self.ctx.register_command('languages_mode', self.show_language_list, None,
                              True)
    self.indent_ = TreeSitterAutoIndent(self.ctx)

  def on_buffer_changed(self, buf, ctx):
    if ctx != self.ctx:
      return

    if self.indent_ is None:
      self.indent_ = TreeSitterAutoIndent(self.ctx)

    if not hasattr(buf, 'highlighter_'):
      buf.tree_sitter_tree_ = TreeSitterLangTree(self.ctx, buf)
      buf.highlighter_ = TreeSitterSyntaxHighlighter(self.ctx, buf,
                                                     self.editor_)
      logging.debug(
          'install tree and syntax highlighter, auto indent to buffer:%s',
          buf.name())

  def show_language_list(self, ctx):
    lang_names = self.selected_langs_[:]
    lang_names.extend([n for n in get_lang_names(ctx) if n not in lang_names])

    self.content_window_ = cw = ctx.create_list_content_window()
    self.content_window_.list_window_delegate_ = self

    self.list_widget_ = l = cw.list_widget_
    self.text_edit_ = t = cw.text_edit_

    self.list_items_ = []

    f_c = self.ctx.get_theme_def_color('default', 'foreground')
    b_c = self.ctx.get_theme_def_color('default', 'background')

    for name in lang_names:
      item = QListWidgetItem(name, l)
      item.setForeground(f_c)
      item.setBackground(b_c)

      self.list_items_.append(item)

    t.returnPressed.connect(self.execute_command)
    l.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)

    self.content_window_.select_first_visible_item()

    cw.show()

  def execute_command(self):
    self.item_double_clicked(self.list_widget_.currentItem())

  def item_double_clicked(self, item):
    self.ctx.current_buffer_.set_lang(item.text())

    try:
      self.selected_langs_.remove(item.text())
    except:
      pass

    self.selected_langs_.insert(0, item.text())

    self.ctx.close_content_window()

  def on_text_edited(self, txt):
    return False

  def should_add_mock_item(self, txt):
    return False

  def get_item_text(self, item):
    return item.text()

  def create_mock_item(self, txt):
    pass
