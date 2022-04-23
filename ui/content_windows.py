import logging
import platform

from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
from PySide6.QtGui import QTextCursor

from core.builtin_commands import BuiltinCommands
from .textedit_mixin import TextEditMixin


class ContentWindowLineEdit(QLineEdit):

  def __init__(self, ctx, *args):
    QLineEdit.__init__(self, *args)

    self.ctx_ = ctx

    self.setFrame(True)
    self.setAutoFillBackground(True)

    self.__apply_theme()

  def keyPressEvent(self, evt):
    key = evt.keyCombination().toCombined()
    if key == Qt.Key_Return or key == Qt.Key_Enter:
      evt.accept()
      self.returnPressed.emit()
      return

    super().keyPressEvent(evt)

  def __apply_theme(self):
    # palette seems not working for line edit on windows
    if platform.system() == 'Windows':
      f_c = self.ctx_.get_theme_def_color('default', 'foreground')
      b_c = self.ctx_.get_theme_def_color('default', 'background')

      bc_name = b_c.name()

      # stylesheet seems need a ARGB hex value
      if len(bc_name) == 7:
        bc_name = f'#00{bc_name[1:]}'

      self.setStyleSheet(f'background-color:{bc_name};')


class ContentWindow(QWidget, TextEditMixin):

  def __init__(self, ctx, parent=None):
    QWidget.__init__(self, parent)
    TextEditMixin.__init__(self)

    self.parent_widget_ = parent
    self.ctx_ = ctx
    self.content_widget_ = self.create_content_widget()

    self.text_edit_ = ContentWindowLineEdit(ctx)

    layout = QVBoxLayout()
    layout.addWidget(self.content_widget_)
    layout.addWidget(self.text_edit_)
    self.setLayout(layout)

    self.text_edit_.setFocus(Qt.ActiveWindowFocusReason)
    self.update_geometry()

    ctx.switch_behavior_context('content_window')

  def cursor_position(self):
    return self.text_edit_.cursorPosition()

  def move_cursor(self, op, mode):
    if op == QTextCursor.Left:
      self.text_edit_.cursorBackward(self.is_marker_active())
    elif op == QTextCursor.Right:
      self.text_edit_.cursorForward(self.is_marker_active())
    elif op == QTextCursor.EndOfLine:
      self.text_edit_.end(self.is_marker_active())
    elif op == QTextCursor.StartOfLine:
      self.text_edit_.home(self.is_marker_active())
    elif op == QTextCursor.PreviousWord:
      self.text_edit_.cursorWordBackward(self.is_marker_active())
    elif op == QTextCursor.NextWord:
      self.text_edit_.cursorWordForward(self.is_marker_active())
    else:
      logging.debug('content window ignore cursor op:{}, mode:{}'.format(
          op, mode))

  def kill_char(self):
    self.__kill_text(QTextCursor.Right)

  def kill_word(self):
    self.__kill_text(QTextCursor.NextWord)

  def kill_end_of_line(self):
    self.__kill_text(QTextCursor.EndOfLine)

  def kill_start_of_line(self):
    self.__kill_text(QTextCursor.StartOfLine)

  def __kill_text(self, op):
    if op == QTextCursor.Left:
      self.text_edit_.cursorBackward(True)
    elif op == QTextCursor.Right:
      self.text_edit_.cursorForward(True)
    elif op == QTextCursor.EndOfLine:
      self.text_edit_.end(True)
    elif op == QTextCursor.StartOfLine:
      self.text_edit_.home(True)
    elif op == QTextCursor.PreviousWord:
      self.text_edit_.cursorWordBackward(True)
    elif op == QTextCursor.NextWord:
      self.text_edit_.cursorWordForward(True)
    else:
      logging.debug('content window ignore cursor op:{}, mode:{}'.format(
          op, mode))
    self.text_edit_.cut()

  def undo(self):
    self.text_edit_.undo()

  def redo(self):
    self.text_edit_.redo()

  def select_all(self):
    self.text_edit_.selectAll()

  def paste(self):
    self.text_edit_.paste()

  def copy(self):
    self.text_edit_.copy()

  def cut(self):
    self.text_edit_.cut()

  def register_commands(self):
    super().register_commands()

  def update_geometry(self):
    cr = self.parent_widget_.contentsRect()
    vm = self.parent_widget_.viewportMargins()

    self.setGeometry(
        QRect(cr.left(),
              cr.bottom() - cr.height() / 4, cr.width(),
              cr.height() / 4) - vm)

  def sizeHint(self):
    cr = self.parent_widget_.contentsRect()
    vm = self.parent_widget_.viewportMargins()

    return QSize(cr.width(), cr.height() / 4) - vm

  def close(self):
    super().close()

    self.ctx_.switch_behavior_context()

  def _page_up_down(self, ctx, pageDown):
    logging.debug('content window ignore page up down')

  def create_content_widget(self):
    return None
