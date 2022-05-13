from yapsy.IPlugin import IPlugin
from core.builtin_commands import BuiltinCommands

from .grep_tool import get_grep_tool


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

    self.grep_tool_ = get_grep_tool(self.ctx)

    self.ctx.bind_key('Alt+T', self.show)
    self.project_root_ = self.ctx.get_current_buffer_project_root()

  def show(self, ctx, *args):
    ctx.run_command(
        BuiltinCommands.OPEN, None, False, {
            'directory_content_dir_path_selected': self.__list_file,
            'should_add_mock_item': False,
            'on_text_edited': self.__on_text_edited
        })

  def __list_file(self, dir, list_helper):
    list_helper.clear_items()
    list_helper.sort_and_select_first_item()

  def __on_text_edited(self, txt, list_helper):
    list_helper.clear_items()

    for p in self.grep_tool_.list_match_file_name(self.project_root_, txt):
      list_helper.create_list_item_for_path(p)

    list_helper.sort_and_select_first_item()
