import logging

from pubsub import pub

from PySide6.QtCore import QSize, Qt, QRect,Slot
from PySide6.QtGui import QTextCursor, QPalette, QKeySequence
from PySide6.QtWidgets import QPlainTextEdit, QApplication
from PySide6.QtWidgets import QAbstractSlider

from eim.core.builtin_commands import BuiltinCommands
from .textedit_mixin import TextEditMixin


class Editor(QPlainTextEdit, TextEditMixin):

  def __init__(self, ctx):
    QPlainTextEdit.__init__(self)
    TextEditMixin.__init__(self)

    self.setWindowTitle("EIM")

    self.ctx_ = ctx
    ctx.ui_helper.set_current_window(self)

    self.kill_ring_ = []

    ctx.switch_behavior_context('editor')

    self.__clear_scroll_bar()

    self.updateRequest[QRect,
                       int].connect(self.__update_request)
    pub.subscribe(self.__on_buffer_changed, 'buffer_changed')

    self.__apply_theme()

    self.register_commands()
    self.bind_keys()

  def __on_buffer_changed(self, buf, ctx):
    pass

  def __clear_scroll_bar(self):
    self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

  @Slot()
  def __update_request(self, rc, dy):
    pass

  def resizeEvent(self, e):
    super().resizeEvent(e)

  def sizeHint(self):
    return QSize(1024, 768)

  def focusInEvent(self, e):
    super().focusInEvent(e)

    self.ctx_.close_content_window()

    self.ctx_.switch_behavior_context('editor')

  def keyPressEvent(self, evt):
    if not self.__pre_key_press_event(evt):
      super().keyPressEvent(evt)

    self.__post_key_press_event(evt)

  def __pre_key_press_event(self, evt):
    key_combined = evt.keyCombination().toCombined()

    if key_combined == Qt.Key_Tab:
      evt.accept()

      self.__handle_tab_indent(evt)

      return True
    elif ((key_combined == Qt.Key_Backspace)
          or (key_combined == (Qt.Key.Key_Backtab | Qt.SHIFT))):
      line_start, line_indents_end, empty_line = self.ctx_.run_command(
          'calculate_line_indent_info', None, False, self)

      tc = self.textCursor()
      if tc.positionInBlock() == line_start:
        return False

      if empty_line or tc.positionInBlock() <= line_indents_end:
        indent_char, indent_size = \
          self.ctx_.current_buffer_.get_indent_options()

        del_char_count = (tc.positionInBlock() - line_start) % indent_size

        if del_char_count == 0:
          del_char_count = indent_size

        tc.beginEditBlock()
        tc.clearSelection()
        for i in range(del_char_count):
          tc.deletePreviousChar()
        tc.endEditBlock()

        return True
    elif (evt == QKeySequence.InsertLineSeparator
          or evt == QKeySequence.InsertParagraphSeparator):
      if self.is_marker_active() or self.textCursor().hasSelection():
        self.active_marker(False)

        return True

    return False

  def __handle_tab_indent(self, evt):
    key_combined = evt.keyCombination().toCombined()
    back_tab = key_combined == (Qt.Key.Key_Backtab | Qt.SHIFT)

    indent = self.ctx_.run_command('calculate_indent', None, False, self)

    if indent is None:
      indent_char, indent_size = self.ctx_.current_buffer_.get_indent_options()
      self.textCursor().insertText(indent_char * indent_size)

  def __post_key_press_event(self, evt):
    if (evt == QKeySequence.InsertLineSeparator
        or evt == QKeySequence.InsertParagraphSeparator):
      soft_line_break = evt == QKeySequence.InsertLineSeparator

      self.ctx_.run_command('calculate_indent', None, False, self)

  def cursor_position(self):
    return self.textCursor().position

  def move_cursor(self, op, mode):
    self.moveCursor(op, mode)

  def select_all(self):
    self.selectAll()

  def _page_up_down(self, ctx, pageDown):
    logging.debug('editor page up down')

    self.verticalScrollBar().triggerAction(
        QAbstractSlider.SliderPageStepAdd if pageDown else QAbstractSlider.
        SliderPageStepSub)
    cursor = self.textCursor()
    moved = cursor.movePosition(
        QTextCursor.Down if pageDown else QTextCursor.Up,
        QTextCursor.MoveAnchor
        if not self.is_marker_active() else QTextCursor.KeepAnchor,
        self.verticalScrollBar().pageStep())

    logging.debug('cursor moved:{}, steps:{}'.format(
        moved,
        self.verticalScrollBar().pageStep()))

    if moved:
      self.setTextCursor(cursor)
      self.ensureCursorVisible()

  def __apply_theme(self):
    pass

  def kill_char(self):
    self.textCursor().deleteChar()

  def kill_word(self):
    self.__kill_text(QTextCursor.NextWord)

  def kill_end_of_line(self):
    self.__kill_text(QTextCursor.EndOfLine)

  def kill_start_of_line(self):
    self.__kill_text(QTextCursor.StartOfLine)

  def __kill_text(self, op):
    c = self.textCursor()

    c.movePosition(op, QTextCursor.KeepAnchor)
    txt = c.selectedText()

    if len(txt) == 0:
      if op == QTextCursor.StartOfLine:
        c.deletePreviousChar()
      else:
        c.deleteChar()
      return

    self.copy()
    c.removeSelectedText()
    self.setTextCursor(c)

  def copy(self):
    self.__save_selection()
    super().copy()

  def cut(self):
    self.__save_selection()
    super().cut()

  def paste(self):
    self.__save_paste_history_from_clipboard()
    self.paste_from_history(0)

  def clear_selection(self):
    c = self.textCursor()
    c.clearSelection()
    self.setTextCursor(c)

  def __save_selection(self):
    c = self.textCursor()

    txt = c.selectedText()

    if len(txt) == 0:
      return

    self.__update_kill_ring(txt)

  def __update_kill_ring(self, txt):
    try:
      self.kill_ring_.remove(txt)
    except:
      pass

    self.kill_ring_.insert(0, txt)

  def paste_from_history(self, index):
    txt = None
    try:
      txt = self.kill_ring_[index]
    except:
      pass

    if txt is None:
      return

    c = self.textCursor()
    c.insertText(txt)

    self.__update_kill_ring(txt)

  def __save_paste_history_from_clipboard(self):
    clipboard = QApplication.clipboard()
    mimeData = clipboard.mimeData()

    txt = None
    if mimeData.hasText():
      txt = mimeData.text()
    elif mimeData.hasHtml():
      txt = mimeData.html()

    if txt is not None:
      self.__update_kill_ring(txt)
