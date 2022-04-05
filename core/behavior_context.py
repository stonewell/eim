import logging


class BehaviorContext(object):
  def __init__(self, ctx, parent_context = None):
    super().__init__()

    self.ctx_ = ctx
    self.parent_context_ = parent_context
    self.cmds_ = {}
    self.keys_ = {}

  def bind_key(self, key_seq, cmd_or_callable):
    self.keys_[key_seq] = cmd_or_callable

  def register_command(self, cmd_name, callable):
    self.cmds_[cmd_name] = callable

  def get_command(self, cmd_name):
    try:
      return self.cmds_[cmd_name]
    except(KeyError):
      return self.parent_context_.get_command(cmd_name) if self.parent_context_ else None

  def get_keybinding_callable(self, key_seq):
    if not key_seq in self.keys_:
      if self.parent_context_:
        logging.debug('key seq:{} is not found, try parent'.format(key_seq))
        return self.parent_context_.get_keybinding_callable(key_seq)
      else:
        logging.debug('key seq:{} is not found, no parent'.format(key_seq))
        return None

    cmd_or_callable = self.keys_[key_seq]

    if callable(cmd_or_callable):
      return lambda: cmd_or_callable(self.ctx_)

    def run_command():
      logging.debug('run command:{}'.format(cmd_or_callable))
      c = self.get_command(cmd_or_callable)

      if callable(c):
        c(self.ctx_)
      else:
        logging.error('cmd:{} is not map to a callable:{}'.format(cmd_or_callable, c))

    return run_command
