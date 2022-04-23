import logging

from PySide6.QtWidgets import QListWidgetItem, QListWidget

from fuzzywuzzy import fuzz

from core.builtin_commands import BuiltinCommands
from .content_windows import ContentWindow


class ListContentWindow(ContentWindow):

  def __init__(self, ctx, parent=None):
    ContentWindow.__init__(self, ctx, parent)

    cc = self.ctx_.get_behavior_context('content_window')
    lc = self.ctx_.get_behavior_context('list_content_window')
    lc.set_parent_context(cc)

    self.need_update_text_ = False

    self.ctx_.switch_behavior_context('list_content_window')

    self.list_window_delegate_ = None

    self.list_widget_.itemSelectionChanged.connect(
        self.__item_selection_changed)
    self.text_edit_.textEdited[str].connect(self.__on_text_edited)
    self.text_edit_.returnPressed.connect(self.__execute_command)
    self.list_widget_.itemDoubleClicked[QListWidgetItem].connect(
        self.__execute_command)

    self.list_widget_.verticalScrollBar().setHidden(True)

  def create_content_widget(self):
    self.list_widget_ = QListWidget()
    return self.list_widget_

  def __execute_command(self):
    self.need_update_text_ = True

  def register_commands(self):
    super().register_commands()

    self.ctx_.hook_command(BuiltinCommands.PREV_LINE, self.__prev_item,
                           'list_content_window', False)
    self.ctx_.hook_command(BuiltinCommands.NEXT_LINE, self.__next_item,
                           'list_content_window', False)

  def bind_keys(self):
    super().bind_keys()

  def __prev_item(self, ctx):
    self.need_update_text_ = True

    count = self.list_widget_.count()
    cur_row = self.list_widget_.currentRow()

    for row in range(cur_row - 1, -1, -1):
      item = self.list_widget_.item(row)
      if not item.isHidden():
        self.list_widget_.setCurrentRow(row)
        return

    for row in range(count - 1, cur_row - 1, -1):
      item = self.list_widget_.item(row)
      if not item.isHidden():
        self.list_widget_.setCurrentRow(row)
        return

  def __next_item(self, ctx):
    self.need_update_text_ = True

    count = self.list_widget_.count()
    cur_row = self.list_widget_.currentRow()

    for row in range(cur_row + 1, count):
      item = self.list_widget_.item(row)
      if not item.isHidden():
        self.list_widget_.setCurrentRow(row)
        return

    for row in range(0, cur_row + 1):
      item = self.list_widget_.item(row)
      if not item.isHidden():
        self.list_widget_.setCurrentRow(row)
        return

  def __get_item_text(self, item, for_display=False):
    if self.list_window_delegate_ is not None:
      if for_display and hasattr(self.list_window_delegate_,
                                 'get_item_display_text'):
        txt = self.list_window_delegate_.get_item_display_text(item)
      else:
        txt = self.list_window_delegate_.get_item_text(item)
    else:
      txt = item.text()

    return txt

  def __item_selection_changed(self):
    if self.need_update_text_:
      txt = self.__get_item_text(self.list_widget_.currentItem(), True)
      self.text_edit_.setText(txt)

  def __get_new_lt(self, item):

    def new_lt(other):
      if item.ratio_ == other.ratio_:
        if hasattr(item, 'custom_lt'):
          return item.custom_lt(other)
        return self.__get_item_text(item) < self.__get_item_text(other)

      return item.ratio_ > other.ratio_

    return new_lt

  def __item_match_text_ratio(self, item, text):
    if self.list_window_delegate_ is not None:
      item_text = self.list_window_delegate_.get_item_text(item)
    else:
      item_text = item.text()

    return fuzz.ratio(text, item_text)

  def __update_match_ratio(self, item, txt):
    ratio = self.__item_match_text_ratio(item, txt)

    item.ratio_ = ratio if len(txt) > 0 else 0
    item.__lt__ = self.__get_new_lt(item)

    logging.debug('ratio:{} for {} -> {}'.format(ratio, txt, item.text()))
    item.setHidden(ratio == 0 and len(txt) > 0)

  def __on_text_edited(self, txt):
    self.__remove_mock_item()

    if self.list_window_delegate_ is not None and hasattr(
        self.list_window_delegate_, 'on_text_edited'):
      if self.list_window_delegate_.on_text_edited(txt):
        logging.debug('list window delegate handled on text edited')
        return

    self.match_txt_and_mock_item(txt)

  def match_txt_and_mock_item(self, txt):
    for row in range(self.list_widget_.count()):
      item = self.list_widget_.item(row)
      self.__update_match_ratio(item, txt)

    self.list_widget_.sortItems()
    self.need_update_text_ = False

    self.select_first_visible_item()

    if self.list_window_delegate_ is not None:
      if not self.list_window_delegate_.should_add_mock_item(txt):
        return

      logging.debug('add mock item for:{}'.format(txt))
      self.__add_mock_item(txt)

  def select_first_visible_item(self):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if not item.isHidden():
          self.list_widget_.setCurrentItem(item)
          break
    except:
      logging.exception('set current item failed')

  def __add_mock_item(self, txt):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if txt == self.list_window_delegate_.get_item_text(item):
          logging.debug('find {} in items, do nothing'.format(txt))
          return

      mock_item = self.list_window_delegate_.create_mock_item(txt)
      self.__update_match_ratio(mock_item, txt)

      self.list_widget_.sortItems()

      if not self.__has_non_mock_item_visible():
        self.list_widget_.setCurrentItem(mock_item)
    except:
      logging.exception('add mock item error')

  def __remove_mock_item(self):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if hasattr(item, 'mock_'):
          self.list_widget_.takeItem(row)
    except:
      logging.exception('remove mock item failed')

  def __has_non_mock_item_visible(self):
    try:
      for row in range(self.list_widget_.count()):
        item = self.list_widget_.item(row)

        if not hasattr(item, 'mock_') and not item.isHidden():
          return True
    except:
      logging.exception('has_non_mock_item_visible failed')

    return False
