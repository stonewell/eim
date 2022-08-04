import threading
import logging
from functools import partial

from yapsy.IPlugin import IPlugin
from PySide6.QtCore import Qt

from eim.core.builtin_commands import BuiltinCommands
from .grep_tool import get_grep_tool


class PathWrapper(object):

  def __init__(self, p, line, column_length, text):
    self.path_ = p
    self.line_ = line
    self.column_length_ = column_length
    self.text_ = text

  def __getattribute__(self, n):
    if n in ['line_', 'path_', 'column_length_', 'text_']:
      return super().__getattribute__(n)

    return getattr(self.path_, n)


class GrepToolAsyncRunner(object):

  def __init__(self, path_iter, path_handler):
    self.stop_ = False
    self.path_iter_ = path_iter
    self.path_handler_ = path_handler

    self.runner_ = None

  def run(self):
    if self.runner_ is not None:
      return

    self.stop_ = False
    self.runner_ = threading.Thread(target=self.__run)
    self.runner_.start()

  def stop(self):
    if self.runner_ is None:
      return

    self.stop_ = True
    self.runner_.join()

    self.path_handler_(None)

  def __run(self):
    for p in self.path_iter_:
      if self.stop_:
        break

      self.path_handler_(p)

    self.path_handler_(None)


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
    self.grep_tool_runner_ = None

    if self.grep_tool_ is None:
      logging.warning('you need an ag(the silver searcher) to make grep work')
      return

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
    self.project_root_ = self.ctx.get_current_buffer_project_root()

    list_helper.clear_items()

    if self.grep_tool_runner_ is not None:
      self.grep_tool_runner_.stop()

    def __run(ctx, c, p):
      ctx.run_in_ui_thread(partial(c, list_helper, p))

    self.grep_tool_runner_ = GrepToolAsyncRunner(
        self.grep_tool_.list_match_file_name(self.project_root_, txt),
        partial(__run, self.ctx, self.__on_grep_tool_new_path))
    self.grep_tool_runner_.run()

    return True

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
    self.project_root_ = self.ctx.get_current_buffer_project_root()

    list_helper.clear_items()

    if len(txt) < 3:
      return True

    order = 0
    for m in self.grep_tool_.list_match_files(self.project_root_, txt):
      p, line, column_length, text = m

      p = PathWrapper(p, line, column_length, text)

      l_item = list_helper.create_list_item_for_path(p)
      l_item.order_ = order
      order += 1

      l_item.setText(
          f'{p.relative_to(self.project_root_).as_posix()}:{line}:{text}')

    list_helper.sort_and_select_first_item()

    return True

  def __load_file_and_goto_line(self, p):
    self.ctx.load_buffer(p.path_)
    try:
      self.ctx.run_command(BuiltinCommands.GOTO_LINE, None, False, p.line_)
    except:
      pass

  def __on_grep_tool_new_path(self, list_helper, p):
    if p is None:
      list_helper.sort_and_select_first_item()
      return

    l_item = list_helper.create_list_item_for_path(p)
    l_item.setText(f'{p.relative_to(self.project_root_).as_posix()}')
