import os
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

  def custom_lt(self, other):
    if self.order_ == other.order_:
      return self.item_.name < other.item_.name

    return self.order_ < other.order_

  def __lt__(self, other):
    return self.custom_lt(other)


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

  def show(self, ctx, *args):
    self.content_window_ = cw = ctx.create_list_content_window()
    cw.list_window_delegate_ = self

    try:
      self.__directory_content_file_path_selected = args[0][
          'directory_content_file_path_selected']
    except:
      self.__directory_content_file_path_selected = None

    try:
      self.__directory_content_dir_path_selected = args[0][
          'directory_content_dir_path_selected']
    except:
      self.__directory_content_dir_path_selected = None

    def item_text_match(item, text):
      if item.text().find(text) >= 0:
        return 1
      else:
        return 0

    self.content_window_.item_match_text_ratio = item_text_match

    self.list_widget_ = cw.content_widget_
    self.text_edit_ = cw.text_edit_

    self.text_edit_.returnPressed.connect(self.execute_command)
    self.list_widget_.itemDoubleClicked[QListWidgetItem].connect(
        self.item_double_clicked)

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
      item = dir.resolve() / name
      icon = self.content_window_.style().standardIcon(QStyle.SP_DirIcon)
      l_item = DirectoryContentItem(item, icon, item.as_posix(),
                                    self.list_widget_)
      l_item.order_ = order

      self.list_items_.append(l_item)

    for item in self.__list_directory(dir):
      if item.is_dir():
        icon = self.content_window_.style().standardIcon(QStyle.SP_DirIcon)
      else:
        icon = self.content_window_.style().standardIcon(QStyle.SP_FileIcon)

      self.list_items_.append(
          DirectoryContentItem(item, icon, item.name, self.list_widget_))

    self.list_widget_.sortItems()

    self.content_window_.select_first_visible_item()

  def __list_directory(self, dir):
    return dir.iterdir()

  def execute_command(self):
    self.item_double_clicked(self.list_widget_.currentItem())

  def item_double_clicked(self, item):
    if hasattr(item, 'mock_'):
      selected_item = self.current_list_dir_ / item.mock_name_
    else:
      selected_item = item.item_

    self.__load_path(selected_item)

  def __load_path(self, path_item):
    if path_item.is_dir():
      if self.__directory_content_dir_path_selected is None:
        self.__load_dir_content(path_item)
      else:
        self.__directory_content_dir_path_selected(path_item)
    else:
      #load file
      if self.__directory_content_file_path_selected is None:
        self.ctx.load_buffer(path_item)
        self.ctx.close_content_window()
      else:
        self.__directory_content_file_path_selected(path_item)

  def on_text_edited(self, txt):
    if txt.find('/') < 0:
      return False

    tmp_path = new_path = (
        self.current_list_dir_ /
        os.path.expandvars(os.path.expanduser(txt))).resolve()

    while True:
      if tmp_path.is_dir():
        break

      if tmp_path.parent == tmp_path or tmp_path == self.current_list_dir_:
        return False

      tmp_path = tmp_path.parent.resolve()

    logging.debug('will show content:{} for {}'.format(new_path, tmp_path))
    if new_path == tmp_path:
      txt = ''
    else:
      txt = new_path.relative_to(tmp_path).as_posix()

    logging.debug('switch to:{}, update text:{}'.format(tmp_path, txt))

    self.__load_dir_content(tmp_path)

    self.text_edit_.setText(txt)
    self.content_window_.match_txt_and_mock_item(txt)

    return True

  def should_add_mock_item(self, txt):
    return len(txt) > 0

  def get_item_text(self, item):
    if hasattr(item, 'mock_'):
      return item.mock_name_

    if item.order_ < 0:
      return ''

    return item.text()

  def create_mock_item(self, txt):
    icon = self.content_window_.style().standardIcon(QStyle.SP_FileIcon)

    item = DirectoryContentItem(None, icon, '[?] {}'.format(txt),
                                self.list_widget_)
    item.order_ = -3
    item.mock_ = True
    item.mock_name_ = txt

    self.list_items_.append(item)

    return item
