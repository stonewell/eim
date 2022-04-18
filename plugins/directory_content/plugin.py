import logging

from PySide6.QtWidgets import QListWidgetItem, QStyle

from yapsy.IPlugin import IPlugin
from core.builtin_commands import BuiltinCommands


class DirectoryContentItem(QListWidgetItem):
  def __init__(self, item, *args):
    QListWidgetItem.__init__(self, *args)
    self.item_ = item
    try:
      self.order_ = 0 if item.is_dir() else 1
    except:
      pass

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
    cw.text_edit_delegate_ = self

    def item_text_match(item, text):
      if item.text().find(text) >= 0:
        return 1
      else:
        return 0

    self.content_window_.item_match_text_ratio = item_text_match

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

    self.current_list_dir_ = dir

    # add special folder . and ..
    for name, order in [('.', -2), ('..', -1)]:
      item = dir / name
      icon = self.content_window_.style().standardIcon(QStyle.SP_DirIcon)
      l_item = DirectoryContentItem(item, icon, name, self.list_widget_)
      l_item.order_ = order

      self.list_items_.append(l_item)

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
    if hasattr(item, 'mock_'):
      selectItem = self.current_list_dir_ / item.mock_name_
    else:
      selectItem = item.item_

    self.__load_path(selectItem)

  def __load_path(self, path_item):
    if path_item.is_dir():
      self.__load_dir_content(path_item)
    else:
      #load file
      self.ctx.load_buffer(path_item)
      self.ctx.close_content_window()

  def on_text_edited(self, txt):
    self.__remove_mock_item()

    if len(txt) == 0:
      return

    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if txt == item.item_.name:
          logging.debug('find {} in items, do nothing'.format(txt))
          return

      logging.debug('add mock item for {}'.format(txt))
      icon = self.content_window_.style().standardIcon(QStyle.SP_FileIcon)

      item = DirectoryContentItem(item, icon, '[?] {}'.format(txt), self.list_widget_)
      item.order_ = -3
      item.mock_ = True
      item.mock_name_ = txt

      self.list_items_.append(item)

      self.list_widget_.sortItems()

      if not self.__has_non_mock_item_visible():
        self.list_widget_.setCurrentItem(item)
    except:
      logging.exception('directory content on text edited error')

  def __remove_mock_item(self):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if hasattr(item, 'mock_'):
          self.list_widget_.takeItem(row)
    except:
      logging.exception('remove mock item failed')

  def get_item_text(self, item):
    if hasattr(item, 'mock_'):
      return item.mock_name_

    if item.order_ < 0:
      return ''

    return item.text()

  def __has_non_mock_item_visible(self):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if not hasattr(item, 'mock_') and not item.isHidden():
          return True
    except:
      logging.exception('has_non_mock_item_visible failed')

    return False
