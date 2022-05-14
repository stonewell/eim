from PySide6.QtWidgets import QListWidgetItem

from yapsy.IPlugin import IPlugin
from eim.core.builtin_commands import BuiltinCommands


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

    self.ctx.hook_command(BuiltinCommands.COPY_PASTE_HISTORY,
                          self.show_content_window, 'editor', False)

  def show_content_window(self, ctx):
    history = self.editor_.kill_ring_

    self.content_window_ = cw = ctx.create_list_with_preview_content_window()
    self.content_window_.list_window_delegate_ = self

    self.list_widget_ = l = cw.list_widget_
    self.text_edit_ = t = cw.text_edit_
    self.preview_edit_ = pt = cw.preview_edit_

    pt.setReadOnly(True)

    self.list_items_ = []

    f_c = self.ctx.get_theme_def_color('default', 'foreground')
    b_c = self.ctx.get_theme_def_color('default', 'background')

    index = 0
    for v in history:
      item = QListWidgetItem(self.__get_list_item_display(v), l)
      item.setForeground(f_c)
      item.setBackground(b_c)
      item.preview_text_ = v
      item.order_ = index
      item.custom_lt = self.__get_item_custom_lt(item)

      self.list_items_.append(item)
      index += 1

    t.returnPressed.connect(self.execute_command)
    l.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)
    l.itemSelectionChanged.connect(self.__item_selection_changed)

    self.content_window_.select_first_visible_item()

    cw.show()

  def execute_command(self):
    self.item_double_clicked(self.list_widget_.currentItem())

  def item_double_clicked(self, item):
    order = self.list_widget_.currentItem().order_
    self.editor_.paste_from_history(order)

    self.ctx.close_content_window()

  def on_text_edited(self, txt):
    return False

  def should_add_mock_item(self, txt):
    return False

  def get_item_text(self, item):
    return item.text()

  def get_item_display_text(self, item):
    return ''

  def create_mock_item(self, txt):
    pass

  def __get_item_custom_lt(self, item):
    return lambda other: item.order_ < other.order_

  def __get_list_item_display(self, v):
    s = min(15, len(v))

    return v[:s]

  def __item_selection_changed(self):
    txt = self.list_widget_.currentItem().preview_text_
    self.preview_edit_.setText(txt)
