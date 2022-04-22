import logging

from PySide6.QtGui import QSyntaxHighlighter
from PySide6.QtGui import QColor
from PySide6.QtGui import QFont
from PySide6.QtGui import QTextCharFormat


class TreeSitterSyntaxHighlighter(QSyntaxHighlighter):

  def __init__(self, ctx, buffer, editor):
    QSyntaxHighlighter.__init__(self, buffer.document_)
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.editor_ = editor

  def highlightBlock(self, text):
    captures = self.buffer_.tree_sitter_tree_.highlight_query(
        self.currentBlock().position(),
        self.currentBlock().position() + self.currentBlock().length())

    if captures is None or len(captures) == 0:
      return

    #tc = self.editor_.textCursor()

    #select_begin = -1
    #select_end = -1

    # if tc.hasSelection():
    #   select_begin = tc.selectionStart() - self.currentBlock().position()
    #   select_end = tc.selectionEnd() - self.currentBlock().position()

    #   print(f'select: {select_begin}, {select_end}, {tc.selectionStart()}, {tc.selectionEnd()}')

    prev_start = -1
    prve_key = None

    for c in captures:
      start_index, count, valid_capture = self.__normalize_capture_with_current_block(
          c)

      if not valid_capture:
        continue

      logging.debug(
          f'set format at {start_index} count:{count} using {c[1]}, {text}')

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

      if prev_start == start_index:
        self.__merge_format(start_index, f, c[1], prev_key)

      prev_start = start_index
      prev_key = c[1]

      self.setFormat(start_index, count, f)

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

  def __merge_format(self, start_index, f, key, prev_key):
    merge = key == 'property' and prev_key == 'method.call'

    if not merge:
      return

    prev_f = self.format(start_index)
    f.setForeground(prev_f.foreground())
    f.setBackground(prev_f.background())

  def __normalize_capture_with_current_block(self, c):
    if c[0].start_byte > (self.currentBlock().position() +
                          self.currentBlock().length()):
      logging.debug(f'captures {c} exceed current block')
      return None, None, False

    start_index = c[0].start_byte - self.currentBlock().position()
    count = c[0].end_byte - c[0].start_byte

    if start_index > self.currentBlock().length():
      logging.debug(
          f'captures {c} exceed current block, start:{start_index} > block lenght:{self.currentBlock().length()}'
      )
      return None, None, False

    if start_index < 0:
      count += start_index
      start_index = 0

    if count <= 0:
      logging.debug(f'captures {c} exceed current block, count <= 0')
      return None, None, False

    if (start_index + count) > self.currentBlock().length():
      count = (self.currentBlock().length() - start_index)

    return start_index, count, True
