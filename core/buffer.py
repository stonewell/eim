import logging

from pathlib import Path


class EditorBuffer(object):

  def __init__(self, ctx, name=None):
    self.file_path_ = None
    self.name_ = name
    self.ctx_ = ctx
    self.document_ = self.ctx_.create_document('')

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
      file_path = self.ctx_.ask_for_file_path()
    elif file_path is None:
      file_path = self.file_path_

    if file_path is None:
      logging.warn('no file path to save')
      return

    logging.debug('save to file:{}'.format(file_path.resolve()))

    file_path.write_text(self.ctx_.get_document_content(self.document_))

  def name(self):
    if self.name_ is not None:
      return self.name_

    if self.file_path_ is None:
      return 'Untitiled'

    return self.file_path_.name
