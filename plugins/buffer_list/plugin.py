from PySide6.QtWidgets import QListWidgetItem

from yapsy.IPlugin import IPlugin


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

    self.ctx.register_command('buffer_list', self.show_buffer_list, None,
                              False)
    self.ctx.bind_key('Ctrl+X,B', 'buffer_list')

  def show_buffer_list(self, ctx):
    buf_names = ctx.buffer_names()

    self.content_window_ = cw = ctx.create_list_content_window()
    self.content_window_.list_window_delegate_ = self

    self.list_widget_ = l = cw.content_widget_
    self.text_edit_ = t = cw.text_edit_

    self.list_items_ = []

    for name in buf_names:
      item = QListWidgetItem(name, l)
      item.custom_lt = self.__get_item_custom_lt(item)
      self.list_items_.append(item)

    t.returnPressed.connect(self.execute_command)
    l.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)

    self.content_window_.select_first_visible_item()

    cw.show()

  def execute_command(self):
    self.item_double_clicked(self.list_widget_.currentItem())

  def item_double_clicked(self, item):
    if hasattr(item, 'mock_'):
      newBuf = item.mock_name_
    else:
      newBuf = item.text()

    self.ctx.switch_to_buffer(newBuf)
    self.ctx.close_content_window()

  def on_text_edited(self, txt):
    return False

  def should_add_mock_item(self, txt):
    return len(txt) > 0

  def get_item_text(self, item):
    if hasattr(item, 'mock_'):
      return item.mock_name_

    return item.text()

  def create_mock_item(self, txt):
    item = QListWidgetItem('[?] {}'.format(txt), self.list_widget_)
    item.mock_ = True
    item.mock_name_ = txt
    item.custom_lt = self.__get_item_custom_lt(item)

    self.list_items_.append(item)

    return item

  def __get_item_custom_lt(self, item):
    return lambda other: self.get_item_text(item) < self.get_item_text(other)
