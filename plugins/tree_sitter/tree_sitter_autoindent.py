import logging


class TreeSitterAutoIndent(object):

  def __init__(self, ctx, buffer, editor):
    self.buffer_ = buffer
    self.ctx_ = ctx
    self.editor_ = editor

    self.ctx_.hook_command('calculate_indent', self.calculate_indent, 'editor',
                           False)

  def calculate_indent(self, ctx):
    c = self.editor_.textCursor()
    current_block_number = self.editor_.textCursor().blockNumber()

    current_block = self.buffer_.document_.findBlockByNumber(
        current_block_number)
    last_block = current_block

    if current_block_number - 1 >= 0:
      last_block = self.buffer_.document_.findBlockByNumber(
          current_block_number - 1)

    pos_in_block = c.positionInBlock()
    l = current_block.layout().lineForTextPosition(pos_in_block)

#    if l.textLength() == 0:
#      last_block, last_l = self.find_last_non_empty_line(current_block, l)

    nn = self.__get_last_node_at_pos(current_block.position() + pos_in_block - 2)

    while nn is not None:
      print(nn.id, nn)
      nn = nn.parent

    captures, state = self.buffer_.tree_sitter_tree_.indent_query(
        last_block.position(),
        current_block.position() + pos_in_block)

    if captures is None:
      return None

    for capture in captures:
      print(capture[0].id, capture[1], capture[0])

    return None

  def find_last_non_empty_line(self, current_block, l):
    return None, None

  def __get_first_node_at_line(self, line_number):
    pass

  def __get_last_node_at_line(self, line_number):
    pass

  def __get_last_node_at_pos(self, pos):
    return self.buffer_.tree_sitter_tree_.node_descendant_for_byte_range(pos, pos)
