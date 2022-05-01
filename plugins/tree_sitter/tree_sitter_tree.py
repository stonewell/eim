import logging
import pathlib
import platform

from tree_sitter import Language, Parser
from .tree_sitter_langs import suffix
from .tree_sitter_highlighter_state import TreeSitterHighlightState
from .neovim_tree_sitter_highlighter_state import NeovimTreeSitterHighlightState
from .neovim_query_convert import convert as neovim_query_convert


class TreeSitterLangTree(object):

  def __init__(self, ctx, buffer):
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.tree_ = None
    self.highlight_ = None
    self.indent_ = None

    self.__load_language()
    self.buffer_.document_.contentsChange[int, int,
                                          int].connect(self.on_contents_change)

  def __load_language(self):
    lang = self.buffer_.get_lang()

    if lang is None:
      logging.warn('buffer languange is not detected')
      return

    langs_dir = pathlib.Path(
        self.ctx_.appdirs_.user_config_dir) / 'tree_sitter_langs'
    neovim_langs_dir = pathlib.Path(
        self.ctx_.appdirs_.user_config_dir) / 'neovim_tree_sitter'
    langs_data_dir = langs_dir / 'data'
    neovim_langs_data_dir = neovim_langs_dir / 'data'
    langs_data_bin_dir = langs_data_dir / 'bin'
    langs_data_query_file = langs_data_dir / 'queries' / lang.replace(
        '-', '_') / 'highlights.scm'
    neovim_langs_data_query_file = neovim_langs_data_dir / 'queries' / lang.replace(
        '-', '_') / 'highlights.scm'
    langs_data_indent_file = langs_data_dir / 'queries' / lang.replace(
        '-', '_') / 'indents.scm'
    neovim_langs_data_indent_file = neovim_langs_data_dir / 'queries' / lang.replace(
        '-', '_') / 'indents.scm'

    lang_binary = langs_data_bin_dir / '{}.{}'.format(lang, suffix())

    if not lang_binary.exists():
      logging.warn('buffer language:{} is not supported'.format(lang))
      self.buffer_.invalid_lang()
      return

    self.lang_ = Language(lang_binary.as_posix(), lang.replace('-', '_'))
    self.parser_ = Parser()
    self.parser_.set_language(self.lang_)

    self.tree_ = self.parser_.parse(
        self.buffer_.document_.toPlainText().encode('utf-8'))

    # highlight
    self.highlight_ = None
    if neovim_langs_data_query_file.exists():
      try:
        self.highlight_ = self.lang_.query(
            neovim_query_convert(neovim_langs_data_query_file.read_text()))
        self.highlight_type_ = 'nvim_treesitter'
        logging.debug(
            f'using {neovim_langs_data_query_file.as_posix()} for highlight')
      except:
        logging.exception(
            f'failed loading {neovim_langs_data_query_file.as_posix()} for highlight'
        )

    if self.highlight_ is None and langs_data_query_file.exists():
      try:
        self.highlight_ = self.lang_.query(langs_data_query_file.read_text())
        self.highlight_type_ = 'treesitter'
        logging.debug(
            f'using {langs_data_query_file.as_posix()} for highlight')
      except:
        logging.exception(
            f'failed loading {langs_data_query_file.as_posix()} for highlight')

    if self.highlight_ is None:
      logging.debug(f'no highlight for lang:{lang}')

    # indents
    self.indent_ = None
    if neovim_langs_data_indent_file.exists():
      try:
        self.indent_ = self.lang_.query(
            neovim_query_convert(neovim_langs_data_indent_file.read_text()))
        self.indent_type_ = 'nvim_treesitter'
        logging.debug(
            f'using {neovim_langs_data_indent_file.as_posix()} for indents')
      except:
        logging.exception(
            f'failed loading {neovim_langs_data_indent_file.as_posix()} for indents'
        )
    if self.indent_ is None and langs_data_indent_file.exists():
      try:
        self.indent_ = self.lang_.query(langs_data_indent_file.read_text())
        self.indent_type_ = 'treesitter'
        logging.debug(f'using {langs_data_indent_file.as_posix()} for indents')
      except:
        logging.exception(
            f'failed loading {langs_data_indent_file.as_posix()} for indents')

    if self.indent_ is None:
      logging.debug(f'no indent for lang:{lang}')

  def on_contents_change(self, start, chars_removed, chars_added):
    if self.tree_ is None:
      self.__load_language()
      return

    self.tree_.edit(start_byte=start,
                    old_end_byte=start + chars_removed,
                    new_end_byte=start + chars_added,
                    start_point=(0, 0),
                    old_end_point=(0, 0),
                    new_end_point=(0, 0))
    old_tree = self.tree_
    self.tree_ = self.parser_.parse(
        self.buffer_.document_.toPlainText().encode('utf-8'), self.tree_)

  def highlight_query(self, begin, end):
    if self.highlight_ is None:
      return None, None

    if self.highlight_type_ == 'treesitter':
      state = TreeSitterHighlightState(self.ctx_)
    else:
      state = NeovimTreeSitterHighlightState(self.ctx_)

    return (self.highlight_.captures(self.tree_.root_node,
                                 start_byte=begin,
                                 end_byte=end), state)

  def reload_languange(self):
    self.__load_language()

  def indent_query(self, begin, end):
    if self.indent_ is None:
      return None, None

    state = None

    return (self.indent_.captures(self.tree_.root_node,
                                 start_byte=begin,
                                 end_byte=end), state)
