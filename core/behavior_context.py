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

  def apply_key_bindings(self, binding_widget = None):
    for key_seq in self.keys_:
      self.apply_key_binding(key_seq, binding_widget)

  def revoke_key_bindings(self):
    for key_seq in self.keys_:
      self.revoke_key_binding(key_seq)

  def apply_key_binding(self, key_seq, binding_widget = None):
    if key_seq in self.keys_:
      self.ctx_.ui_helper.bind_key(key_seq,
                                   self.get_keybinding_callable(self.keys_[key_seq]),
                                   binding_widget)

  def revoke_key_binding(self, key_seq):
    if self.parent_context_:
      self.parent_context_.apply_key_binding(key_seq)

  def get_command(self, cmd_name):
    try:
      return self.cmds_[cmd_name]
    except(KeyError):
      return self.parent_context_.get_command(cmd_name) if self.parent_context_ else None

  def get_keybinding_callable(self, cmd_or_callable):
    if callable(cmd_or_callable):
      return cmd_or_callable

    def run_command():
      c = self.get_command(cmd_or_callable)

      if callable(c):
        c()

    return run_command
