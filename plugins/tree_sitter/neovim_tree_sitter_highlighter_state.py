import logging

from .tree_sitter_highlighter_state import TreeSitterHighlightState

class NeovimTreeSitterHighlightState(TreeSitterHighlightState):

  def __init__(self, ctx):
    super().__init__(ctx)

  def should_update_format(self, current_block, capture):
    start_index, count, valid_capture = self._normalize_capture_with_current_block(
        current_block, capture)

    return start_index, count, valid_capture
