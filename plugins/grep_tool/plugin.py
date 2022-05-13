from yapsy.IPlugin import IPlugin
from core.builtin_commands import BuiltinCommands
from PySide6.QtCore import Qt

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

    if self.grep_tool_ is None:
      logging.warning('you need an ag(the silver searcher) to make grep work')
      return

    self.project_root_ = self.ctx.get_current_buffer_project_root()

    self.ctx.bind_key('Alt+T', self.__show_files)
    self.ctx.bind_key('Alt+P', self.__show_matches)

  def __show_files(self, ctx, *args):
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

  def __show_matches(self, ctx, *args):
    ctx.run_command(
        BuiltinCommands.OPEN, None, False, {
            'directory_content_dir_path_selected': self.__list_file,
            'should_add_mock_item': False,
            'on_text_edited': self.__on_matches_text_edited,
            'directory_content_file_path_selected':
            self.__load_file_and_goto_line,
        })

  def __on_matches_text_edited(self, txt, list_helper):
    list_helper.clear_items()

    if len(txt) < 3:
      return

    self.path_line_mapping_ = {}
    for m in self.grep_tool_.list_match_files(self.project_root_, txt):
      p, line, column_length, text = m
      l_item = list_helper.create_list_item_for_path(p)

      self.path_line_mapping_[p] = line
      l_item.setText(
          f'{p.relative_to(self.project_root_).as_posix()}:{line}:{text}')

    list_helper.sort_and_select_first_item()

  def __load_file_and_goto_line(self, p):
    self.ctx.load_buffer(p)
    try:
      self.ctx.run_command(BuiltinCommands.GOTO_LINE, None, False,
                           self.path_line_mapping_[p])
    except:
      pass
