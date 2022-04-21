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

    self.ctx.register_command('commands_list', self.show_commands_window, None,
                              False)
    self.ctx.bind_key('Alt+X', 'commands_list')

  def show_commands_window(self, ctx):
    self.commands_ = ctx.get_commands()

    self.content_window_ = cw = ctx.create_list_content_window()

    self.list_widget_ = l = cw.content_widget_
    self.text_edit_ = t = cw.text_edit_

    self.list_items_ = []

    f_c = self.ctx.get_theme_def_color('default', 'foreground')
    b_c = self.ctx.get_theme_def_color('default', 'background')

    for cmd in self.commands_:
      item = QListWidgetItem(cmd, l)
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
    self.ctx.run_command(item.text())
