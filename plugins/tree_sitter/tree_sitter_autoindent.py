import logging
import re
from PySide6.QtGui import QTextCursor


class TreeSitterAutoIndent(object):

  def __init__(self, ctx, buffer, editor):
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.editor_ = editor

    self.ctx_.hook_command('calculate_indent', self.calculate_indent, 'editor',
                           False)

  def calculate_indent(self, ctx):
    indents = self.__get_indents()

    if indents is None:
      return None

    c = self.editor_.textCursor()
    current_block_number = self.editor_.textCursor().blockNumber()

    current_block = self.buffer_.document_.findBlockByNumber(
        current_block_number)

    pos_in_block = c.positionInBlock()
    l = current_block.layout().lineForTextPosition(pos_in_block)

    node = None
    if self.__is_empty_line(current_block, l):
      last_block, last_line = self.find_last_non_empty_line(current_block, l)

      if last_block is None:
        logging.warning(
            f'unable to find last non empty line:{current_block_number}:{l.lineNumber()}'
        )
        return None

      node = self.__get_last_node_at_line(last_block, last_line)

      if node.id in indents['indent_end']:
        node = self.__get_first_node_at_line(current_block, l)
        logging.debug(f'last line:{last_line.lineNumber()} indent_end, get line:{l.lineNumber()} first node:{node}')
      else:
        logging.debug(f'last line:{last_line.lineNumber()} get last node:{node}')
    else:
      node = self.__get_first_node_at_line(current_block, l)
      logging.debug(f'non empty line get line:{l.lineNumber()} first node:{node}')

    if node is None:
      logging.warning(
          f'unable to find a node to check indent:{current_block_number}:{l.lineNumber()}'
      )
      return None

    if node.id in indents['zero_indent']:
      return (0, 0)

    indent_size = 2
    indent = 0

    root_start = 0
    is_processed_by_row = {}

    lnum = self.__get_line_number(current_block, l)

    while node is not None:
      end_row, end_col = node.end_point
      start_row, start_col = node.start_point

      logging.debug(
          f'{node}, {start_row}, {end_row}, {lnum}, {node.id in indents["indent"]}, {node.id in indents["branch"]}'
      )

      if ((not node.id in indents['indent']) and (node.id in indents['auto'])
          and (start_row < lnum and end_row >= lnum)):
        logging.warning(f'auto indent for ${lnum}')
        return (-1, indent)

      if ((not node.id in indents['indent']) and (node.id in indents['ignore'])
          and (start_row < lnum and end_row >= lnum)):
        logging.debug(f'ignore indent for ${lnum}')
        return (0, indent)

      is_processed = False

      if ((start_row not in is_processed_by_row
           or not is_processed_by_row[start_row])
          and ((node.id in indents['branch'] and start_row == lnum) or
               (node.id in indents['dedent'] and start_row != lnum))):
        indent = indent - indent_size
        is_processed = True

      if ((start_row not in is_processed_by_row
           or not is_processed_by_row[start_row])
          and node.id in indents['indent']
          #and start_row != end_row
          and (start_row != lnum)):
        indent = indent + indent_size
        is_processed = True

      if start_row in is_processed_by_row:
        is_processed_by_row[
            start_row] = is_processed_by_row[start_row] or is_processed
      else:
        is_processed_by_row[start_row] = is_processed

      node = node.parent

    logging.debug(f'indent:{indent} at line:{lnum}')

    if indent > 0:
      line_indent = self.__get_first_non_empty_char(current_block, l)

      if line_indent != indent:
        c.beginEditBlock()
        c.clearSelection()
        c.setPosition(current_block.position() + l.textStart())
        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, line_indent)
        c.insertText(' ' * indent)
        c.endEditBlock()
    elif indent < 0:
      logging.warning(f'invalid indent:{indent} at line:{lnum}')

    return (1, indent)

  def __get_indents(self):
    captures, state = self.buffer_.tree_sitter_tree_.indent_query(
        0, self.buffer_.document_.characterCount())

    if captures is None or len(captures) == 0:
      return None

    indents = {
        'auto': {},
        'indent': {},
        'indent_end': {},
        'dedent': {},
        'branch': {},
        'ignore': {},
        'aligned_indent': {},
        'zero_indent': {},
    }

    for capture in captures:
      try:
        indents[capture[1]][capture[0].id] = {}
      except (KeyError):
        indents[capture[1]] = {}
        indents[capture[1]][capture[0].id] = {}

    return indents

  def find_last_non_empty_line(self, current_block, l):
    while True:
      if not self.__is_empty_line(current_block, l):
        return current_block, l

      cur_lnum = l.lineNumber()
      if cur_lnum > 0:
        l = current_block.layout().lineAt(cur_lnum - 1)
      elif current_block.blockNumber() > 0:
        current_block = current_block.previous()
        last_lnum = current_block.layout().lineCount() - 1
        l = current_block.layout().lineAt(last_lnum)
      else:
        return None, None

  def __get_first_node_at_line(self, b, l):
    lnum = self.__get_line_number(b, l)
    col = self.__get_first_non_empty_char(b, l)

    return self.buffer_.tree_sitter_tree_.node_descendant_for_point_range(
        lnum, col, lnum, col)

  def __get_last_node_at_line(self, b, l):
    lnum = self.__get_line_number(b, l)
    col = l.textLength() - 1

    return self.buffer_.tree_sitter_tree_.node_descendant_for_point_range(
        lnum, col, lnum, col)

  def __get_last_node_at_pos(self, pos):
    return self.buffer_.tree_sitter_tree_.node_descendant_for_byte_range(
        pos, pos)

  def __is_empty_line(self, b, l):
    if l.textLength() == 0:
      return True

    return re.fullmatch('^\\s*$',
                        b.text()[l.textStart():l.textStart() + l.textLength()],
                        flags=re.MULTILINE) is not None

  def __get_line_number(self, b, l):
    lnum = l.lineNumber()

    for b_c in range(self.editor_.blockCount()):
      if b_c == b.blockNumber():
        break

      lnum += self.editor_.document().findBlockByNumber(b_c).lineCount()

    return lnum

  def __get_first_non_empty_char(self, b, l):
    result = re.search('^\\s*',
                       b.text()[l.textStart():l.textStart() + l.textLength()],
                       flags=re.MULTILINE)

    if result is None:
      return 0

    return result.end()
