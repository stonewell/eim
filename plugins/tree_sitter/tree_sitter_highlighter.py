import logging

from PySide6.QtGui import QSyntaxHighlighter


class TreeSitterSyntaxHighlighter(QSyntaxHighlighter):

  def __init__(self, buffer):
    QSyntaxHighlighter.__init__(self, buffer.document_)
    self.buffer_ = buffer

  def highlightBlock(self, text):
    captures = self.buffer_.tree_sitter_tree_.highlight_query(
        self.currentBlock().position(),
        self.currentBlock().position() + self.currentBlock().length())

    if len(captures) > 0:
      for c in captures:
        print(c)
        print(c[0].start_byte, c[0].end_byte)
