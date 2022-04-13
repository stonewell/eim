from .builtin_commands import BuiltinCommands


def default_key_bindings():
  return {
      'Ctrl+X, Ctrl+C': BuiltinCommands.QUIT,
      'Ctrl+P': BuiltinCommands.PREV_LINE,
      'Ctrl+N': BuiltinCommands.NEXT_LINE,
      'Ctrl+B': BuiltinCommands.PREV_CHAR,
      'Ctrl+F': BuiltinCommands.NEXT_CHAR,
      'Esc': BuiltinCommands.CANCEL,
  }
