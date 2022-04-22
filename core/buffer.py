import logging
from guesslang import Guess

from pathlib import Path

guess = Guess()


class EditorBuffer(object):

  def __init__(self, ctx, name=None):
    self.file_path_ = None
    self.name_ = name
    self.ctx_ = ctx
    self.document_ = self.ctx_.create_document('')
    self.lang_ = None
    self.invalid_langs_ = {}

  def load_file(self, file_path):
    if not isinstance(file_path, Path):
      file_path = Path(file_path)

    if not file_path.exists():
      self.file_path_ = file_path

      self.document_ = self.ctx_.create_document('')

      return

    with file_path.open(encoding='utf-8') as f:
      content = f.read()

      self.file_path_ = file_path

      self.document_ = self.ctx_.create_document(content)

  def save_file(self, file_path=None):
    if file_path is None and self.file_path_ is None:
      self.ctx_.ask_for_file_path(self.__write_to_file)
      return
    elif file_path is None:
      file_path = self.file_path_

    self.__write_to_file(file_path)

  def __write_to_file(self, file_path):
    logging.debug('save to file:{}'.format(file_path.resolve()))

    file_path.write_text(self.ctx_.get_document_content(self.document_))

  def name(self):
    if self.name_ is not None:
      return self.name_

    if self.file_path_ is None:
      return 'Untitiled'

    return self.file_path_.name

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

      if self.lang_ == 'c++':
        self.lang_ = 'cpp'
    except:
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
