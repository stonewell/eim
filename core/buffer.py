import logging

from pathlib import Path


class EditorBuffer(object):

  def __init__(self, ctx, name=None):
    self.file_path_ = None
    self.name_ = None
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

  def name(self):
    if self.name_ is not None:
       return self.name_

    if self.file_path_ is None:
      return 'Untitiled'

    return self.file_path_.name
