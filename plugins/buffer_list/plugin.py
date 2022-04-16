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

    self.list_widget_ = l = cw.content_widget_
    self.text_edit_ = t = cw.text_edit_

    self.list_items_ = []

    for name in buf_names:
      self.list_items_.append(QListWidgetItem(name, l))

    t.returnPressed.connect(self.execute_command)
    l.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)

    self.content_window_.select_first_visible_item()

    cw.show()

  def execute_command(self):
    if len(self.text_edit_.text()) == 0:
      self.item_double_clicked(self.list_widget_.currentItem())
      return

    self.ctx.switch_to_buffer(self.text_edit_.text())
    self.ctx.close_content_window()

  def item_double_clicked(self, item):
    self.ctx.switch_to_buffer(item.text())
    self.ctx.close_content_window()
