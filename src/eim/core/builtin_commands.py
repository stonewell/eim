class BuiltinCommands(object):
  QUIT = 'quit'
  CANCEL = 'cancel'
  SAVE = 'save'
  SAVE_AS = 'save_as'
  OPEN = 'open'
  CLOSE_BUFFER = 'close_buffer'

  PREV_LINE = 'prev_line'
  NEXT_LINE = 'next_line'
  PREV_CHAR = 'prev_char'
  NEXT_CHAR = 'next_char'
  PREV_WORD = 'prev_word'
  NEXT_WORD = 'next_word'
  PREV_PAGE = 'prev_page'
  NEXT_PAGE = 'next_page'
  START_OF_LINE = 'start_of_line'
  END_OF_LINE = 'end_of_line'

  GOTO_LINE = 'go_to_line'

  SELECT_ALL = 'select_all'

  KILL_TO_END_OF_LINE = 'kill_to_end_of_line'
  KILL_TO_START_OF_LINE = 'kill_to_start_of_line'

  PUSH_MARK = 'push_mark'
  POP_MARK = 'pop_mark'

  COPY = 'copy'
  PASTE = 'paste'
  CUT = 'cut'
  COPY_PASTE_HISTORY = 'copy_paste_history'
  UNDO = 'undo'
  REDO = 'redo'

  KILL_CHAR = 'kill_char'
  KILL_WORD = 'kill_word'

  SEARCH = 'search'
  REVERSE_SEARCH = 'reverse_search'
  SEARCH_REGEX = 'search_regex'

  REPLACE = 'replace'
  REPLACE_REGEX = 'replace_regex'

  RELOAD_BUFFER = 'reload_buffer'
