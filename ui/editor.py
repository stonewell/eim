import logging

from pubsub import pub

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QTextCursor, QPalette
from PySide6.QtWidgets import QPlainTextEdit, QApplication
from PySide6.QtWidgets import QAbstractSlider

from core.builtin_commands import BuiltinCommands
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

    self.verticalScrollBar().setHidden(True)

    pub.subscribe(lambda buf: self.verticalScrollBar().setHidden(True),
                  'buffer_changed')

    self.__apply_theme()

    self.register_commands()
    self.bind_keys()

  def resizeEvent(self, e):
    super().resizeEvent(e)

  def sizeHint(self):
    return QSize(1024, 768)

  def focusInEvent(self, e):
    super().focusInEvent(e)

    self.ctx_.close_content_window()

    self.ctx_.switch_behavior_context('editor')

  def keyPressEvent(self, evt):
    if (evt.keyCombination().toCombined()
        == Qt.Key_Tab) or (evt.keyCombination().toCombined()
                           == (Qt.Key.Key_Backtab | Qt.SHIFT)):
      evt.accept()

      back_tab = evt.keyCombination().toCombined() == (Qt.Key.Key_Backtab
                                                       | Qt.SHIFT)

      indent = self.ctx_.run_command('calculate_indent')

      if indent is not None:
        return

    super().keyPressEvent(evt)

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
