import logging
import re
from PySide6.QtGui import QTextCursor


class TreeSitterAutoIndent(object):

  def __init__(self, ctx):
    self.ctx_ = ctx

    self.ctx_.hook_command('calculate_indent', self.__calculate_indent,
                           'editor', False)
    self.ctx_.hook_command('calculate_line_indent_info',
                           self.__calculate_line_indent_info, 'editor', False)

  def __calculate_line_indent_info(self, ctx, editor):
    buffer = ctx.current_buffer_
    c = editor.textCursor()
    current_block_number = editor.textCursor().blockNumber()

    current_block = buffer.document_.findBlockByNumber(current_block_number)

    pos_in_block = c.positionInBlock()
    l = current_block.layout().lineForTextPosition(pos_in_block)

    empty_line = self.__is_empty_line(current_block, l)
    line_indent = self.__get_first_non_empty_char(current_block, l)

    return (
        l.textStart(),  #line start pos
        line_indent,  #line indents end pos
        empty_line  # if line is empty
    )

  def __calculate_indent(self, ctx, editor):
    buffer = ctx.current_buffer_

    indents = self.__get_indents(buffer, editor)

    if indents is None:
      return None

    c = editor.textCursor()
    current_block_number = editor.textCursor().blockNumber()

    current_block = buffer.document_.findBlockByNumber(current_block_number)

    pos_in_block = c.positionInBlock()
    l = current_block.layout().lineForTextPosition(pos_in_block)

    node = None

    # always check last line indent
    # it seems to get better behavior
    if self.__is_empty_line(current_block, l) or True:
      last_block, last_line = self.__find_last_non_empty_line(current_block, l)

      if last_block is None:
        logging.warning(
            f'unable to find last non empty line:{current_block_number}:{l.lineNumber()}'
        )
        return None

      node = self.__get_last_node_at_line(buffer, editor, last_block,
                                          last_line)

      if node.id in indents['indent_end']:
        node = self.__get_first_node_at_line(buffer, editor, current_block, l)
        logging.debug(
            f'last line:{last_line.lineNumber()} indent_end, get line:{l.lineNumber()} first node:{node}'
        )
      else:
        logging.debug(
            f'last line:{last_line.lineNumber()} get last node:{node}')
    else:
      node = self.__get_first_node_at_line(buffer, editor, current_block, l)
      logging.debug(
          f'non empty line get line:{l.lineNumber()} first node:{node}')

    if node is None:
      logging.warning(
          f'unable to find a node to check indent:{current_block_number}:{l.lineNumber()}'
      )
      return None

    if node.id in indents['zero_indent']:
      return (0, 0)

    indent_char, indent_size = buffer.get_indent_options()
    logging.debug(
        f'indent using char:[{indent_char}], indent size:{indent_size}')
    indent = 0

    aligned_indent_char = ' '
    aligned_indent = 0

    root_start = 0
    is_processed_by_row = {}

    lnum = self.__get_line_number(editor, current_block, l)

    while node is not None:
      end_row, end_col = node.end_point
      start_row, start_col = node.start_point

      logging.debug(
          f'{node}, {start_row}, {end_row}, {lnum}, {node.id in indents["indent"]}, {node.id in indents["branch"]}, {node.id in indents["aligned_indent"]}'
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

      if ((not is_processed_by_row.get(start_row, False))
          and ((node.id in indents['branch'] and start_row == lnum) or
               (node.id in indents['dedent'] and start_row != lnum))):
        indent = indent - indent_size
        is_processed = True

      if ((not is_processed_by_row.get(start_row, False))
          and node.id in indents['indent']
          #and start_row != end_row
          and (start_row != lnum)):
        indent = indent + indent_size
        is_processed = True

      if ((node.id in indents['aligned_indent']) and (start_row != lnum)
          and (start_row != end_row)):
        aligned_block = buffer.document_.findBlock(node.start_byte)
        aligned_line = aligned_block.layout().lineForTextPosition(
            node.start_byte - aligned_block.position())
        aligned_line_indent = self.__get_first_non_empty_char(
            aligned_block, aligned_line)

        indent = max(aligned_line_indent, 0)
        indent_char = ' ' if indent == 0 else aligned_block.text()[
            aligned_line.textStart()]

        if indent == 0:
          indent = start_col + 1
        else:
          aligned_indent_char = ' '
          aligned_indent = start_col - aligned_line_indent + 1
        break

      is_processed_by_row[start_row] = is_processed_by_row.get(
          start_row, False) or is_processed

      node = node.parent

    logging.debug(
        f'indent:{indent} at line:{lnum}, aligned indent:{aligned_indent}')

    if indent > 0:
      line_indent = self.__get_first_non_empty_char(current_block, l)

      if line_indent != indent:
        c.beginEditBlock()
        c.clearSelection()
        c.setPosition(current_block.position() + l.textStart())
        c.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, line_indent)
        c.insertText(indent_char * indent + aligned_indent_char * aligned_indent)
        c.endEditBlock()
    elif indent < 0:
      logging.warning(f'invalid indent:{indent} at line:{lnum}')

    return (1, indent)

  def __get_indents(self, buffer, editor):
    captures, state = buffer.tree_sitter_tree_.indent_query(
        0, buffer.document_.characterCount())

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

  def __find_last_non_empty_line(self, current_block, l):
    l_exclude = l
    while True:
      if not self.__is_empty_line(current_block, l) and l != l_exclude:
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

  def __get_first_node_at_line(self, buffer, editor, b, l):
    lnum = self.__get_line_number(editor, b, l)
    col = self.__get_first_non_empty_char(b, l)

    return buffer.tree_sitter_tree_.node_descendant_for_point_range(
        lnum, col, lnum, col)

  def __get_last_node_at_line(self, buffer, editor, b, l):
    lnum = self.__get_line_number(editor, b, l)
    col = l.textLength() - 1

    return buffer.tree_sitter_tree_.node_descendant_for_point_range(
        lnum, col, lnum, col)

  def __get_last_node_at_pos(self, buffer, pos):
    return buffer.tree_sitter_tree_.node_descendant_for_byte_range(pos, pos)

  def __is_empty_line(self, b, l):
    if l.textLength() == 0:
      return True

    return re.fullmatch('^\\s*$',
                        b.text()[l.textStart():l.textStart() + l.textLength()],
                        flags=re.MULTILINE) is not None

  def __get_line_number(self, editor, b, l):
    lnum = l.lineNumber()

    for b_c in range(editor.blockCount()):
      if b_c == b.blockNumber():
        break

      lnum += editor.document().findBlockByNumber(b_c).lineCount()

    return lnum

  def __get_first_non_empty_char(self, b, l):
    result = re.search('^\\s*',
                       b.text()[l.textStart():l.textStart() + l.textLength()],
                       flags=re.MULTILINE)

    if result is None:
      return 0

    return result.end()
