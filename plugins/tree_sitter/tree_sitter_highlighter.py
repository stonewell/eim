import logging

from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtGui import QTextCharFormat


class TreeSitterSyntaxHighlighter(QSyntaxHighlighter):

  def __init__(self, ctx, buffer):
    QSyntaxHighlighter.__init__(self, buffer.document_)
    self.buffer_ = buffer
    self.ctx_ = ctx

  def highlightBlock(self, text):
    captures = self.buffer_.tree_sitter_tree_.highlight_query(
        self.currentBlock().position(),
        self.currentBlock().position() + self.currentBlock().length())

    if captures is None or len(captures) == 0:
      return

    prev_start = -1
    prve_key = None

    for c in captures:
      if c[0].start_byte > (self.currentBlock().position() + self.currentBlock().length()):
        logging.debug(f'captures {c} exceed current block')
        continue

      theme_def = self.ctx_.color_theme_.get_theme_def(c[1])

      if theme_def is None:
        logging.error(f'theme:{c[1]} is not found')
        continue

      f_c = self.ctx_.get_color(theme_def, 'foreground')
      b_c = self.ctx_.get_color(theme_def, 'background')
      bold = theme_def['weight'] == 'bold'

      f = QTextCharFormat()
      f.setForeground(f_c)
      f.setBackground(b_c)

      if bold:
        f.setFontWeight(QFont.Bold)

      if 'italic' in theme_def:
        f.setFontItalic(True if theme_def['italic'] else False)

      start_index = c[0].start_byte - self.currentBlock().position()
      count = c[0].end_byte - c[0].start_byte

      if start_index < 0:
        count += start_index
        start_index = 0

      if (start_index + count) > (self.currentBlock().position() +
                                  self.currentBlock().length()):
        count = (self.currentBlock().position() +
                 self.currentBlock().length() - start_index)

      logging.debug(f'set format at {start_index} count:{count} using {c[1]}, {text}')

      if prev_start == start_index:
        self.__merge_format(start_index, f, c[1], prev_key)

      prev_start = start_index
      prev_key = c[1]

      self.setFormat(start_index, count, f)

  def __merge_format(self, start_index, f, key, prev_key):
    merge = key == 'property' and prev_key == 'method.call'

    if not merge:
      return

    prev_f = self.format(start_index)
    f.setForeground(prev_f.foreground())
    f.setBackground(prev_f.background())
