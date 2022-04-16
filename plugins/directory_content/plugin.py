from PySide6.QtWidgets import QListWidgetItem, QStyle

from yapsy.IPlugin import IPlugin
from core.builtin_commands import BuiltinCommands


class DirectoryContentItem(QListWidgetItem):
  def __init__(self, item, *args):
    QListWidgetItem.__init__(self, *args)
    self.item_ = item
    self.order_ = 0 if item.is_dir() else 1

  def __lt__(self, other):
    if self.order_ == other.order_:
      return self.item_.name < other.item_.name

    return self.order_ < other.order_

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

    self.ctx.register_command(BuiltinCommands.OPEN, self.show, None, False)

  def show(self, ctx):
    self.content_window_ = cw = ctx.create_list_content_window()

    self.list_widget_ = cw.content_widget_
    self.text_edit_ = cw.text_edit_

    self.text_edit_.returnPressed.connect(self.execute_command)
    self.list_widget_.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)

    self.__load_dir_content()

    cw.show()

  def __load_dir_content(self, dir=None):
    self.list_items_ = []
    self.list_widget_.clear()

    if dir is None:
      dir = self.ctx.get_current_buffer_dir()

    for item in self.__list_directory(dir):
      if item.is_dir():
        icon = self.content_window_.style().standardIcon(QStyle.SP_DirIcon)
      else:
        icon = self.content_window_.style().standardIcon(QStyle.SP_FileIcon)

      self.list_items_.append(DirectoryContentItem(item, icon, item.name, self.list_widget_))

    self.list_widget_.sortItems()

    self.content_window_.select_first_visible_item()

  def __list_directory(self, dir):
    return dir.iterdir()

  def execute_command(self):
    self.item_double_clicked(self.list_widget_.currentItem())

  def item_double_clicked(self, item):
    if item.item_.is_dir():
      self.__load_dir_content(item.item_)
    else:
      #load file
      self.ctx.load_buffer(item.item_)
      self.ctx.close_content_window()
