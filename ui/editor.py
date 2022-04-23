import logging

from PySide6.QtCore import QSize
from PySide6.QtGui import QTextCursor, QPalette
from PySide6.QtWidgets import QPlainTextEdit
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
    super().paste()

  def clear_selection(self):
    c = self.textCursor()
    c.clearSelection()
    self.setTextCursor(c)

  def __save_selection(self):
    c = self.textCursor()

    txt = c.selectedText()

    if len(txt) == 0:
      return

    self.update_kill_ring(txt)

  def update_kill_ring(self, txt):
    try:
      self.kill_ring_.remove(txt)
    except:
      pass

    self.kill_ring_.insert(0, txt)
