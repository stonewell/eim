from .builtin_commands import BuiltinCommands


def default_key_bindings():
  return {
      'Ctrl+X, Ctrl+C': BuiltinCommands.QUIT,
      'Ctrl+X, Ctrl+F': BuiltinCommands.OPEN,
      'Ctrl+X, Ctrl+S': BuiltinCommands.SAVE,
      'Ctrl+X, Ctrl+W': BuiltinCommands.SAVE_AS,
      'Ctrl+P': BuiltinCommands.PREV_LINE,
      'Ctrl+N': BuiltinCommands.NEXT_LINE,
      'Ctrl+B': BuiltinCommands.PREV_CHAR,
      'Ctrl+F': BuiltinCommands.NEXT_CHAR,
      'Alt+B': BuiltinCommands.PREV_WORD,
      'Alt+F': BuiltinCommands.NEXT_WORD,
      'Ctrl+D': BuiltinCommands.KILL_CHAR,
      'Alt+D': BuiltinCommands.KILL_WORD,
      'Ctrl+V': BuiltinCommands.NEXT_PAGE,
      'Alt+V': BuiltinCommands.PREV_PAGE,
      'Ctrl+A': BuiltinCommands.START_OF_LINE,
      'Ctrl+E': BuiltinCommands.END_OF_LINE,
      'Ctrl+K': BuiltinCommands.KILL_TO_END_OF_LINE,
      'Ctrl+Space': BuiltinCommands.PUSH_MARK,
      'Ctrl+W': BuiltinCommands.CUT,
      'Alt+W': BuiltinCommands.COPY,
      'Ctrl+Y': BuiltinCommands.PASTE,
      'Alt+Y': BuiltinCommands.COPY_PASTE_HISTORY,
      'Esc,Esc': BuiltinCommands.CANCEL,
      'Ctrl+G': BuiltinCommands.CANCEL,
      'Ctrl+X, H': BuiltinCommands.SELECT_ALL,
  }
