import logging

from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtGui import QTextCharFormat
from PySide6.QtGui import QTextCursor


class TreeSitterSyntaxHighlighter(QSyntaxHighlighter):

  def __init__(self, ctx, buffer, editor):
    QSyntaxHighlighter.__init__(self, buffer.document_)
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.editor_ = editor

  def highlightBlock(self, text):
    current_block = self.currentBlock()
    captures, state = self.buffer_.tree_sitter_tree_.highlight_query(
        current_block.position(),
        current_block.position() + current_block.length())

    if captures is None or len(captures) == 0:
      return

    #tc = self.editor_.textCursor()

    #select_begin = -1
    #select_end = -1

    # if tc.hasSelection():
    #   select_begin = tc.selectionStart() - self.currentBlock().position()
    #   select_end = tc.selectionEnd() - self.currentBlock().position()

    #   print(f'select: {select_begin}, {select_end}, {tc.selectionStart()}, {tc.selectionEnd()}')

    for c in captures:
      start_index, count, update_format = state.should_update_format(
          current_block, c)

      if not update_format:
        continue

      theme_def = self.ctx_.get_theme_def(c[1])

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

      if 'italic' in theme_def and theme_def['italic']:
        f.setFontItalic(True)

      self.__set_format(start_index, count, f)

      if self.ctx_.args.debug > 2:
        logging.debug(
            f'set format at {start_index} count:{count} using {c[1]}, [{text}], [{text[start_index:start_index + count]}]'
        )

      #handling selection
      # if ((start_index >= select_begin and start_index < select_end) or
      #     (start_index + count >= select_begin and start_index + count < select_end)):
      #   start_index = max(start_index, select_begin)
      #   count = min(start_index + count, select_end) - start_index

      #   selectF = QTextCharFormat(f)

      #   theme_def = self.ctx_.color_theme_.get_theme_def('highlight')
      #   b_c = self.ctx_.get_color(theme_def, 'background')
      #   selectF.setBackground(b_c)
      #   self.setFormat(start_index, count, selectF)

  def __set_format(self, p, c, f):
    tc = self.editor_.textCursor()
    current_block = self.currentBlock()

    tc.beginEditBlock()
    tc.clearSelection()
    tc.setPosition(current_block.position() + p)
    tc.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, c)
    tc.setCharFormat(f)
    tc.clearSelection()
    tc.endEditBlock()
