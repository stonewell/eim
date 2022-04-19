import logging


class BehaviorContext(object):

  def __init__(self, ctx, parent_context=None):
    super().__init__()

    self.ctx_ = ctx
    self.parent_context_ = parent_context
    self.cmds_ = {}
    self.keys_ = {}
    self.hooked_commands_ = {}

  def bind_key(self, key_seq, cmd_or_callable):
    self.keys_[key_seq] = cmd_or_callable

  def register_command(self, cmd_name, callable, save_history=True):
    self.cmds_[cmd_name] = (callable, save_history)

  def __get_command(self, cmd_name):
    if cmd_name in self.hooked_commands_:
      logging.debug('context:{}, return hooked cmd:{}'.format(
          self.name, cmd_name))
      return self.hooked_commands_[cmd_name]

    try:
      return self.cmds_[cmd_name]
    except (KeyError):
      logging.debug(
          'context:{}, cmd:{} is not registered locally, try parent'.format(
              self.name, cmd_name))
      return self.parent_context_.__get_command(
          cmd_name) if self.parent_context_ else None

  def get_keybinding(self, key_seq):
    try:
      return self.keys_[key_seq]
    except (KeyError):
      if self.parent_context_:
        logging.debug('context:{}, key seq:{} is not found, try parent'.format(
            self.name, key_seq))
        return self.parent_context_.get_keybinding(key_seq)
      else:
        logging.debug('context:{}, key seq:{} is not found, no parent'.format(
            self.name, key_seq))
        return None

  def get_keybinding_callable(self, key_seq):
    cmd_or_callable = self.get_keybinding(key_seq)

    if callable(cmd_or_callable):
      return cmd_or_callable

    return self.get_command_callable(cmd_or_callable)

  def get_command_callable(self, cmd_name):

    def __run_command(ctx, *args):
      c = cmd_name
      logging.debug('context:{}, run command:{}'.format(self.name, cmd_name))

      while True:

        v = self.__get_command(c)

        if v is None:
          break

        c, save_history = v

        if c is None or callable(c):
          break

        logging.debug('context:{}, run command:{}, get next command:{}'.format(
            self.name, cmd_name, c))

      if callable(c):
        ctx.run_command(cmd_name, c, save_history, *args)
      else:
        logging.error('context:{}, cmd:{} is not map to a callable:{}'.format(
            self.name, cmd_name, c))

    return __run_command

  def get_commands(self):
    commands = set(self.cmds_.keys())

    if self.parent_context_:
      commands.update(self.parent_context_.get_commands())

    return list(commands)

  def hook_command(self, cmd_name, cmd_or_callable, save_history=True):
    logging.debug('context:{}, cmd:{} hooked,save history:{}'.format(
        self.name, cmd_name, save_history))
    self.hooked_commands_[cmd_name] = (cmd_or_callable, save_history)
