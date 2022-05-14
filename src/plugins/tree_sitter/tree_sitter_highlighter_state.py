import logging


class TreeSitterHighlightState(object):

  def __init__(self, ctx):
    self.ctx_ = ctx
    self.capture_cache_ = {}

  def should_update_format(self, current_block, capture):
    start_index, count, valid_capture = self._normalize_capture_with_current_block(
        current_block, capture)

    if not valid_capture:
      return start_index, count, False

    if not (start_index, count) in self.capture_cache_:
      self.capture_cache_[(start_index, count)] = capture[1]
      return start_index, count, True

    if (len(self.capture_cache_[(start_index, count)]) < len(capture[1])):
      self.capture_cache_[(start_index, count)] = capture[1]
      return start_index, count, True

    if self.ctx_.args.debug > 2:
      logging.debug(
          f'not set format at {start_index} count:{count} using {capture[1]}, using {self.capture_cache_[(start_index, count)]}'
      )
    return start_index, count, False

  def _normalize_capture_with_current_block(self, current_block, c):
    if self.ctx_.args.debug > 2:
      logging.debug(
          f'normalizes capture:{c}, start:{c[0].start_byte}, end:{c[0].end_byte}')

    if c[0].start_byte > (current_block.position() + current_block.length()):
      if self.ctx_.args.debug > 2:
        logging.debug(f'captures {c} exceed current block')
      return None, None, False

    start_index = c[0].start_byte - current_block.position()
    count = c[0].end_byte - c[0].start_byte

    if start_index > current_block.length():
      if self.ctx_.args.debug > 2:
        logging.debug(
            f'captures {c} exceed current block, start:{start_index} > block lenght:{current_block.length()}'
        )
      return None, None, False

    if start_index < 0:
      count += start_index
      start_index = 0

    if count <= 0:
      if self.ctx_.args.debug > 2:
        logging.debug(f'captures {c} exceed current block, count <= 0')
      return None, None, False

    if (start_index + count) > current_block.length():
      count = (current_block.length() - start_index)

    if self.ctx_.args.debug > 2:
      logging.debug(
          f'normalizes capture:{c}, start:{c[0].start_byte}, end:{c[0].end_byte}, start_index:{start_index}, count:{count}'
      )
    return start_index, count, True
