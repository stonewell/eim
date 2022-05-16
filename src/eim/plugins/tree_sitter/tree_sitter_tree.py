import logging
import pathlib
import platform

from tree_sitter import Language, Parser
from .tree_sitter_langs import suffix
from .tree_sitter_highlighter_state import TreeSitterHighlightState
from .neovim_tree_sitter_highlighter_state import NeovimTreeSitterHighlightState
from .neovim_query_convert import convert as neovim_query_convert


class TreeSitterLangTree(object):
  CONTINUE = 1
  BREAK = 2
  GO = 0

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

  def __point_lt(self, start_row, start_column, end_row, end_column):
    return (start_row < end_row) or (start_row == end_row
                                     and start_column < end_column)

  def __point_lte(self, start_row, start_column, end_row, end_column):
    return (start_row < end_row) or (start_row == end_row
                                     and start_column <= end_column)

  def __node_descendant_for_range(self, check_child_node, include_anonymous):
    node = self.tree_.root_node
    last_visible_node = node

    did_descend = True

    while did_descend:
      did_descend = False

      cursor = node.walk()

      if not cursor.goto_first_child():
        break

      while True:
        child = cursor.node

        check = check_child_node(child)

        if check == TreeSitterLangTree.CONTINUE:
          if not cursor.goto_next_sibling():
            break

          continue
        elif check == TreeSitterLangTree.BREAK:
          break

        node = child

        if include_anonymous:
          last_visible_node = node
        elif node.is_named:
          last_visible_node = node

        did_descend = True
        break

    return last_visible_node

  def __node_descendant_for_point_range(self, start_row, start_column, end_row,
                                        end_column, include_anonymous):

    def check_child_node(child):
      node_end_row, node_end_col = child.end_point
      node_start_row, node_start_col = child.start_point

      # The end of this node must extend far enough forward to touch
      # the end of the range and exceed the start of the range.
      if self.__point_lt(node_end_row, node_end_col, end_row, end_column):
        return TreeSitterLangTree.CONTINUE

      if self.__point_lte(node_end_row, node_end_col, start_row, start_column):
        return TreeSitterLangTree.CONTINUE

      # The start of this node must extend far enough backward to
      # touch the start of the range.
      if self.__point_lt(start_row, start_column, node_start_row,
                         node_start_col):
        return TreeSitterLangTree.BREAK

      return TreeSitterLangTree.GO

    return self.__node_descendant_for_range(check_child_node,
                                            include_anonymous)

  def __node_descendant_for_byte_range(self, start_byte, end_byte,
                                       include_anonymous):

    def check_child_node(child):
      node_end_byte = child.end_byte
      node_start_byte = child.start_byte

      # The end of this node must extend far enough forward to touch
      # the end of the range and exceed the start of the range.
      if node_end_byte < end_byte:
        return TreeSitterLangTree.CONTINUE

      if node_end_byte <= start_byte:
        return TreeSitterLangTree.CONTINUE

      # The start of this node must extend far enough backward to
      # touch the start of the range.
      if start_byte < node_start_byte:
        return TreeSitterLangTree.BREAK

      return TreeSitterLangTree.GO

    return self.__node_descendant_for_range(check_child_node,
                                            include_anonymous)

  def node_descendant_for_point_range(self, start_row, start_column, end_row,
                                      end_column):
    if hasattr(self.tree_.root_node, 'descendant_for_point_range'):
      return self.tree_.root_node.descendant_for_point_range(
          (start_row, start_column), (end_row, end_column))

    logging.warning('node do not have function descendant_for_point_range')
    return self.__node_descendant_for_point_range(start_row, start_column,
                                                  end_row, end_column, True)

  def node_named_descendant_for_point_range(self, start_row, start_column,
                                            end_row, end_column):
    if hasattr(self.tree_.root_node, 'named_descendant_for_point_range'):
      return self.tree_.root_node.named_descendant_for_point_range(
          (start_row, start_column), (end_row, end_column))

    logging.warning(
        'node do not have function named_descendant_for_point_range')
    return self.__node_descendant_for_point_range(start_row, start_column,
                                                  end_row, end_column, False)

  def node_descendant_for_byte_range(self, start_bytes, end_bytes):
    if hasattr(self.tree_.root_node, 'descendant_for_byte_range'):
      return self.tree_.root_node.descendant_for_byte_range(
          start_bytes, end_bytes)

    logging.warning('node do not have function descendant_for_byte_range')
    return self.__node_descendant_for_byte_range(start_bytes, end_bytes, True)

  def node_named_descendant_for_byte_range(self, start_bytes, end_bytes):
    if hasattr(self.tree_.root_node, 'named_descendant_for_byte_range'):
      return self.tree_.root_node.named_descendant_for_byte_range(
          start_bytes, end_bytes)

    logging.warning(
        'node do not have function named_descendant_for_byte_range')
    return self.__node_descendant_for_byte_range(start_bytes, end_bytes, False)
