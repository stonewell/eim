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

    if len(captures) > 0:
      for c in captures:
        theme_def = self.ctx_.color_theme_.get_theme_def(c[1])

        if theme_def is None:
          logging.debug(f'theme:{c[1]} is not found')
          continue

        f_c = self.ctx_.get_color(theme_def, 'foreground')
        b_c = self.ctx_.get_color(theme_def, 'background')
        bold = theme_def['weight'] == 'bold'

        f = QTextCharFormat()
        if bold:
          f.setFontWeight(QFont.Bold)
        f.setForeground(f_c)
        f.setBackground(b_c)

        start_index = c[0].start_byte - self.currentBlock().position()
        count = c[0].end_byte - c[0].start_byte

        logging.debug(f'set format at {start_index} cout:{count} using {c[1]}')
        self.setFormat(start_index, count, f)

