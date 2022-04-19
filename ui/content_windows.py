import traceback
import logging

from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QListWidgetItem
from PySide6.QtWidgets import QListWidget
from PySide6.QtGui import QTextCursor

from fuzzywuzzy import fuzz

from core.builtin_commands import BuiltinCommands
from .textedit_mixin import TextEditMixin


class ContentWindowLineEdit(QLineEdit):

  def __init__(self, ctx, *args):
    super().__init__(*args)

  def keyPressEvent(self, evt):
    key = evt.keyCombination().toCombined()
    if key == Qt.Key_Return or key == Qt.Key_Enter:
      evt.accept()
      self.returnPressed.emit()
      return

    super().keyPressEvent(evt)


class ContentWindow(QWidget, TextEditMixin):

  def __init__(self, content_widget, ctx, parent=None):
    QWidget.__init__(self, parent)
    TextEditMixin.__init__(self)

    self.parent_widget_ = parent
    self.ctx_ = ctx
    self.content_widget_ = content_widget

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

    self.setGeometry(
        QRect(cr.left(),
              cr.bottom() - cr.height() / 4, cr.width(),
              cr.height() / 4))

  def sizeHint(self):
    cr = self.parent_widget_.contentsRect()

    return QSize(cr.width(), cr.height() / 4)

  def close(self):
    super().close()

    self.ctx_.switch_behavior_context()

  def _page_up_down(self, ctx, pageDown):
    logging.debug('content window ignore page up down')


class ListContentWindow(ContentWindow):

  def __init__(self, ctx, parent=None):
    super().__init__(QListWidget(), ctx, parent)

    cc = self.ctx_.get_behavior_context('content_window')
    lc = self.ctx_.get_behavior_context('list_content_window', cc)

    self.need_update_text_ = False

    self.register_commands()
    self.bind_keys()

    self.ctx_.switch_behavior_context('list_content_window')

    self.list_window_delegate_ = None

    self.content_widget_.itemSelectionChanged.connect(
        self.item_selection_changed)
    self.text_edit_.textEdited[str].connect(self.on_text_edited)
    self.text_edit_.returnPressed.connect(self.execute_command)
    self.content_widget_.itemDoubleClicked[QListWidgetItem].connect(
        self.execute_command)

  def execute_command(self):
    self.need_update_text_ = True

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(BuiltinCommands.PREV_LINE, self.prev_item,
                           'list_content_window', False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_LINE, self.next_item,
                           'list_content_window', False)

  def bind_keys(self):
    pass

  def prev_item(self, ctx):
    self.need_update_text_ = True

    count = self.content_widget_.count()
    cur_row = self.content_widget_.currentRow()

    for row in range(cur_row - 1, -1, -1):
      item = self.content_widget_.item(row)
      if not item.isHidden():
        self.content_widget_.setCurrentRow(row)
        return

    for row in range(count - 1, cur_row - 1, -1):
      item = self.content_widget_.item(row)
      if not item.isHidden():
        self.content_widget_.setCurrentRow(row)
        return

  def next_item(self, ctx):
    self.need_update_text_ = True

    count = self.content_widget_.count()
    cur_row = self.content_widget_.currentRow()

    for row in range(cur_row + 1, count):
      item = self.content_widget_.item(row)
      if not item.isHidden():
        self.content_widget_.setCurrentRow(row)
        return

    for row in range(0, cur_row + 1):
      item = self.content_widget_.item(row)
      if not item.isHidden():
        self.content_widget_.setCurrentRow(row)
        return

  def __get_item_text(self, item):
    if self.list_window_delegate_ is not None:
      txt = self.list_window_delegate_.get_item_text(item)
    else:
      txt = item.text()

    return txt

  def item_selection_changed(self):
    if self.need_update_text_:
      txt = self.__get_item_text(self.content_widget_.currentItem())
      self.text_edit_.setText(txt)

  def __get_new_lt(self, item):

    def new_lt(other):
      if item.ratio_ == other.ratio_:
        if hasattr(item, 'custom_lt'):
          return item.custom_lt(other)
        return self.__get_item_text(item) < self.__get_item_text(other)

      return item.ratio_ > other.ratio_

    return new_lt

  def item_match_text_ratio(self, item, text):
    if self.list_window_delegate_ is not None:
      item_text = self.list_window_delegate_.get_item_text(item)
    else:
      item_text = item.text()

    return fuzz.ratio(text, item_text)

  def __update_match_ratio(self, item, txt):
    ratio = self.item_match_text_ratio(item, txt)

    item.ratio_ = ratio if len(txt) > 0 else 0
    item.__lt__ = self.__get_new_lt(item)

    logging.debug('ratio:{} for {} -> {}'.format(ratio, txt, item.text()))
    item.setHidden(ratio == 0 and len(txt) > 0)

  def on_text_edited(self, txt):
    self.__remove_mock_item()

    if self.list_window_delegate_ is not None and hasattr(
        self.list_window_delegate_, 'on_text_edited'):
      if self.list_window_delegate_.on_text_edited(txt):
        logging.debug('list window delegate handled on text edited')
        return

    for row in range(self.content_widget_.count()):
      item = self.content_widget_.item(row)
      self.__update_match_ratio(item, txt)

    self.content_widget_.sortItems()
    self.need_update_text_ = False

    self.select_first_visible_item()

    if self.list_window_delegate_ is not None:
      if not self.list_window_delegate_.should_add_mock_item(txt):
        return

      logging.debug('add mock item for:{}'.format(txt))
      self.__add_mock_item(txt)

  def select_first_visible_item(self):
    try:
      for row in range(self.content_widget_.count()):
        item = self.content_widget_.item(row)

        if not item.isHidden():
          self.content_widget_.setCurrentItem(item)
          break
    except:
      logging.exception('set current item failed')

  def __add_mock_item(self, txt):
    try:
      for row in range(self.content_widget_.count()):
        item = self.content_widget_.item(row)

        if txt == self.list_window_delegate_.get_item_text(item):
          logging.debug('find {} in items, do nothing'.format(txt))
          return

      mock_item = self.list_window_delegate_.create_mock_item(txt)
      self.__update_match_ratio(mock_item, txt)

      self.content_widget_.sortItems()

      if not self.__has_non_mock_item_visible():
        self.content_widget_.setCurrentItem(mock_item)
    except:
      logging.exception('add mock item error')

  def __remove_mock_item(self):
    try:
      for row in range(self.content_widget_.count()):
        item = self.content_widget_.item(row)

        if hasattr(item, 'mock_'):
          self.content_widget_.takeItem(row)
    except:
      logging.exception('remove mock item failed')

  def __has_non_mock_item_visible(self):
    try:
      for row in range(self.content_widget_.count()):
        item = self.content_widget_.item(row)

        if not hasattr(item, 'mock_') and not item.isHidden():
          return True
    except:
      logging.exception('has_non_mock_item_visible failed')

    return False
