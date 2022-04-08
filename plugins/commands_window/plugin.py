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

    self.ctx.register_command('commands_list', self.show_commands_window)
    self.ctx.bind_key('Alt+X', 'commands_list')

  def show_commands_window(self, ctx):
    self.commands_ = ctx.get_commands()

    self.content_window_ = cw = ctx.create_list_content_window()

    self.list_widget_ = l = cw.content_widget_
    self.text_edit_ = t = cw.text_edit_

    self.list_items_ = []

    for cmd in self.commands_:
      self.list_items_.append(QListWidgetItem(cmd, l))

    if len(self.commands_) > 0:
      l.setCurrentItem(self.list_items_[0])

    t.returnPressed.connect(self.execute_command)
    l.itemDoubleClicked[QListWidgetItem].connect(self.execute_command)
    cw.show()

  def execute_command(self):
    cmd = self.list_widget_.currentItem().text()

    self.ctx.run_command(cmd)

  def item_double_clicked(self, item):
    self.ctx.run_command(item.text())
