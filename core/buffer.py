import os
import logging

from guesslang import Guess
from pubsub import pub
from pathlib import Path
from editorconfig import get_properties as ec_get_properties

guess = Guess()
guess.probabilities('''
#include <stdio.h>

int main(int argc, char ** argv) {
  printf("Hello World!\n");
  return 0;
}
''')

lang_name_mapping = {
    'c++': 'c',
    'c#': 'c-sharp',
}


class EditorBuffer(object):

  def __init__(self, ctx, name=None):
    self.file_path_ = None
    self.name_ = name
    self.ctx_ = ctx
    self.__set_buffer_document(self.ctx_.create_document(''))
    self.lang_ = None
    self.text_cursor_ = None
    self.invalid_langs_ = {}

  def load_file(self, file_path):
    if not isinstance(file_path, Path):
      file_path = Path(file_path)

    if not file_path.exists():
      self.file_path_ = file_path

      self.__set_buffer_document(self.ctx_.create_document(''))

      return

    with file_path.open(encoding='utf-8') as f:
      content = f.read()

      self.file_path_ = file_path

      self.__set_buffer_document(self.ctx_.create_document(content))

  def __set_buffer_document(self, document):
    self.document_ = document
    self.document_.setModified(False)
    self.document_.clearUndoRedoStacks()

    self.document_.modificationChanged[bool].connect(
        self.__modification_changed)
    pub.subscribe(self.__cursor_position_changed, 'cursor_position_changed')

  def save_file(self, file_path=None, action=None):
    if file_path is None and self.file_path_ is None:
      self.ctx_.ask_for_file_path(self.__write_to_file, action)
      return
    elif file_path is None:
      file_path = self.file_path_

    self.__write_to_file(file_path)
    if callable(action):
      action()

  def __write_to_file(self, file_path):
    logging.debug('save to file:{}'.format(file_path.resolve()))
    self.file_path_ = file_path

    file_path.write_text(self.ctx_.get_document_content(self.document_))

    self.document_.setModified(False)

    self.update_mode_line()

  def name(self):
    if self.file_path_ is not None:
      return self.file_path_.name

    if self.name_ is not None:
      return self.name_

    return 'Untitiled'

  def get_lang(self):
    if self.lang_ is not None:
      return self.lang_

    if self.document_.characterCount() <= 10:
      return None

    self.guess_lang()

    return self.lang_

  def set_lang(self, lang):
    self.lang_ = lang

    if self.lang_ is not None:
      self.tree_sitter_tree_.reload_languange()
      self.highlighter_.rehighlight()

  def guess_lang(self):
    if self.file_path_ is None:
      self.__try_guess_lang()
      return

    suffix = self.file_path_.suffix
    if suffix.startswith('.'):
      suffix = suffix[1:]

    try:
      langs = self.ctx_.langs_mapping_[suffix]

      self.lang_ = langs[0]

      try:
        self.lang_ = lang_name_mapping[self.lang_]
      except (KeyError):
        pass
    except (KeyError):
      logging.warn(f'no lang mapping for:{suffix}')
      self.__try_guess_lang()

  def invalid_lang(self):
    if self.lang_ is None:
      return

    self.invalid_langs_[self.lang_] = True
    self.lang_ = None

  def __try_guess_lang(self):
    logging.debug('guess lang running')

    content = self.ctx_.get_document_content(self.document_)
    langs = guess.probabilities(content)

    lang = None
    if langs is not None and len(langs) > 0 and langs[0][1] >= 0.5:
      lang = langs[0][0]
      logging.debug(
          f'lang detected:{lang} whose possibility:{langs[0][1]} >= 0.5')

    if lang is not None:
      lang = lang.lower()

      if lang in self.invalid_langs_:
        lang = None

    if lang is not None:
      logging.debug(f'lang detected:{lang}')
      self.lang_ = lang

      try:
        self.lang_ = lang_name_mapping[self.lang_]
      except (KeyError):
        pass

  def update_mode_line(self):
    self.__update_buffer_id_mode_line()

  def __update_buffer_id_mode_line(self):
    theme = self.ctx_.get_theme_def(
        'mode-line-buffer-id') or self.ctx_.get_theme_def('default')

    f_c = self.ctx_.get_color(theme, 'foreground')
    b_c = self.ctx_.get_color(theme, 'background')

    bold = theme['weight'] == 'bold'

    buffer_id_message = self.name()

    if bold:
      buffer_id_message = '<b>' + buffer_id_message + '</b>'

    if 'italic' in theme and theme['italic']:
      buffer_id_message = '<i>' + buffer_id_message + '</i>'

    buffer_id_message = f' {"*" if self.document_.isModified() else "-"} {self.__get_document_size()} -\ <font color="{f_c.name()}">{buffer_id_message}</font> '

    pub.sendMessage('update_mode_line',
                    name='buffer-id',
                    message=buffer_id_message,
                    permanant=False)

  def __modification_changed(self, m):
    self.__update_buffer_id_mode_line()

  def __round(self, c, ndigit=1):
    r_c = round(c, ndigit)

    return round(c) if r_c == round(c) else r_c

  def __get_document_size(self):
    c = float(self.document_.characterCount())

    size_units = ['B', 'K', 'M', 'G', 'T', 'P']

    for index, value in enumerate(size_units):
      if c < 1024:
        return f'{self.__round(c)}{value}'
      c = c / 1024.0

    return f'{self.__round(c)}{size_units[-1]}'

  def __cursor_position_changed(self, pos):
    l, c, tl = pos

    s_l = f'{l}'
    s_c = f'{c}'

    w = max(4, len(s_l), len(s_c))

    msg = f' {s_l.center(w, " ")} : {s_c.center(w, " ")} {self.__get_line_percent(self.__round(float(l) / float(tl), 3) * 100, pos)}  '

    pub.sendMessage('update_mode_line',
                    name='line_pos',
                    message=msg,
                    permanant=True)

    self.__update_buffer_id_mode_line()

  def __get_line_percent(self, v, pos):
    l, c, tl = pos

    if v == 0 or l == 1:
      return 'Top'

    if v == 100 or l == tl:
      return 'Bottom'

    return f'{self.__round(v)}%'

  def get_indent_options(self):
    options = self.__get_editor_options()

    # TODO detect indent of file
    indent_style = options.get('indent_style', 'space').lower()
    indent_size = int(options.get('indent_size', '2'))

    return (' ', indent_size) if indent_style == 'space' else ('\t', 1)

  def apply_editor_config(self):
    options = self.__get_editor_options()

    tab_width = int(options.get('tab_width', '4'))

    self.ctx_.set_tab_width(tab_width)

  def __get_editor_options(self):
    options = {}

    options.update(self.ctx_.config.get('app/editor', {}))

    full_path = self.__get_file_full_path()

    ec = ec_get_properties(full_path)

    if ec:
      logging.debug(f'loaded editor config:{ec}')
      options.update(ec)

    return options

  def __get_file_full_path(self):
    if self.file_path_ is not None:
      return os.path.abspath(self.file_path_.as_posix())

    return os.path.abspath(self.name())

  def is_modified(self):
    return self.document_ is not None and self.document_.isModified()

  def set_modified(self, v):
    if self.document_ is not None:
      self.document_.setModified(v)
