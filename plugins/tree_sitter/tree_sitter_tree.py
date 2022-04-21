import logging
import pathlib
import platform

from tree_sitter import Language, Parser


class TreeSitterLangTree(object):

  def __init__(self, ctx, buffer):
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.tree_ = None

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
    langs_data_dir = langs_dir / 'data'
    langs_data_bin_dir = langs_data_dir / 'bin'
    langs_data_query_file = langs_data_dir / 'queries' / lang / 'highlights.scm'

    lang_binary = langs_data_bin_dir / '{}.{}'.format(
        lang, TreeSitterLangTree.__suffix())

    if not lang_binary.exists():
      logging.warn('buffer language:{} is not supported'.format(lang))

    self.lang_ = Language(lang_binary.as_posix(), lang)
    self.parser_ = Parser()
    self.parser_.set_language(self.lang_)

    self.tree_ = self.parser_.parse(
        self.buffer_.document_.toPlainText().encode('utf-8'))

    if langs_data_query_file.exists():
      self.query_ = self.lang_.query(langs_data_query_file.read_text())
    else:
      self.query_ = None

  @staticmethod
  def __suffix():
    if platform.system() == 'Linux':
      return 'so'
    if platform.system() == 'Windows':
      return 'dll'
    if platform.system() == 'Darwin':
      return 'dylib'

    raise ValueError('unspported platform:{}'.format(platform.system()))

  def on_contents_change(self, start, chars_removed, chars_added):
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
    if self.query_ is None:
      return None

    return self.query_.captures(self.tree_.root_node,
                                start_byte=begin,
                                end_byte=end)
