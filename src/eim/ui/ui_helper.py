import os
import logging
import platform
from pubsub import pub
from functools import reduce

from PySide6.QtGui import QFont, QKeySequence, QShortcut, QTextDocument
from PySide6.QtGui import QColor, QPalette, QFontDatabase, QFontInfo
from PySide6.QtWidgets import QApplication, QPlainTextDocumentLayout
from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import QObject, QCoreApplication, Qt, QRect, Slot, Signal

from .list_content_window import ListContentWindow
from .list_with_preview_content_window import ListWithPreviewContentWindow
from .input_content_window import InputContentWindow
from .editor import Editor
from eim.core.builtin_commands import BuiltinCommands


class EIMApplication(QApplication):

  def __init__(self, *args):
    super().__init__(*args)


class UIHelper(QObject):
  run_in_ui_thread_signal_ = Signal(object)

  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

    if self.ctx_.args.debug > 2:
      os.environ['QT_DEBUG_PLUGINS'] = '1'

    self.run_in_ui_thread_signal_.connect(self.__run_in_ui_thread)

  def create_application(self):
    self.ctx_.app = app = EIMApplication()

    self.__apply_theme(app)

    return app

  def init_commands_and_key_bindings(self):
    self.register_commands()
    self.bind_keys()

  def get_font(self):
    fConfig = self.ctx_.config.get('app/font')

    f = None

    if isinstance(fConfig, str):
      f = QFont()
      f.fromString(fConfig)
    else:
      family = fConfig.get('family', QFont().defaultFamily())
      ptSize = fConfig.get('size', 14)
      bold = fConfig.get('bold', False)
      italic = fConfig.get('italic', False)
      monospace = fConfig.get('monospace', True)

      logging.debug(
          f'family:{family}, ptSize:{ptSize}, bold:{bold}, italic:{italic}, monospace:{monospace}'
      )

      f = QFont(family, ptSize, QFont.Bold if bold else -1, italic)

      if monospace:
        f.setStyleHint(QFont.Monospace, QFont.PreferAntialias)
      else:
        f.setStyleHint(QFont.AnyStyle, QFont.PreferAntialias)

      f.setHintingPreference(QFont.PreferFullHinting)

      c_info = QFontInfo(f)

      if monospace and not c_info.fixedPitch():
        fontFamilies = QFontDatabase.families()

        new_font = QFont(f)

        for family in fontFamilies:
          new_font.setFamily(family)

          info = QFontInfo(new_font)

          if info.fixedPitch():
            logging.debug(
                f'resolve to family:{info.family()}, ptSize:{info.pointSize()}, bold:{info.weight()}, italic:{info.italic()}, monospace:{info.fixedPitch()}'
            )
            return new_font

    logging.debug(
        f'resolve to family:{c_info.family()}, ptSize:{c_info.pointSize()}, bold:{c_info.weight()}, italic:{c_info.italic()}, monospace:{c_info.fixedPitch()}'
    )
    return f

  def set_current_window(self, editor):
    self.editor_ = editor

    self.ctx_.update_plugins_with_current_window(editor)
    self.editor_.updateRequest[QRect,
                               int].connect(self.update_editor_viwe_port)
    self.editor_.cursorPositionChanged.connect(lambda: pub.sendMessage(
        'cursor_position_changed', pos=self.get_row_and_col()))

    pub.subscribe(lambda: self.update_editor_viwe_port(None, None),
                  'viewport_changed')

  def bind_key(self, keyseq, callable, binding_widget=None):
    logging.debug('bind keyseq:{}, {}'.format(keyseq, self.editor_))
    seq = QKeySequence(keyseq)
    sc = QShortcut(seq,
                   self.editor_ if binding_widget is None else binding_widget)
    sc.activated.connect(callable)
    sc.activatedAmbiguously.connect(
        lambda: self.__activated_ambiguously(keyseq))

  def __activated_ambiguously(self, key_seq):
    from eim.eim import get_current_active_eim

    _eim = get_current_active_eim()

    _eim.process_key_binding(key_seq)

  def create_list_content_window(self):
    content_window = ListContentWindow(self.ctx_, self.editor_)
    content_window.register_commands()
    content_window.bind_keys()

    return content_window

  def create_input_content_window(self):
    content_window = InputContentWindow(self.ctx_, self.editor_)
    content_window.register_commands()
    content_window.bind_keys()

    return content_window

  def create_list_with_preview_content_window(self):
    content_window = ListWithPreviewContentWindow(self.ctx_, self.editor_)
    content_window.register_commands()
    content_window.bind_keys()

    return content_window

  def register_commands(self):
    self.ctx_.register_command(BuiltinCommands.QUIT, self.__quit_app)

  def __quit_app(self, ctx):
    self.ctx_.quit_editing()

    def get_buffers():
      for buf in self.ctx_.buffers_:
        yield buf

      return None

    buffers = get_buffers()

    def check_modified_buffer():
      while True:
        try:
          buf = next(buffers)

          if buf.is_modified():
            self.ctx_.switch_to_buffer(buf.name())

            if self.ctx_.prompt_for_buffer_save(check_modified_buffer):
              return
        except (StopIteration):
          break

      QCoreApplication.quit()

    check_modified_buffer()

  def bind_keys(self):
    self.ctx_.bind_key('Ctrl+X,3', self.__split_horz)

  def __split_horz(self, ctx):
    from eim.eim import EIM

    eim = EIM()
    eim.initialize()

    self.splitter_.addWidget(eim.editor_)

  def focus_editor(self):
    self.editor_.setFocus(Qt.ActiveWindowFocusReason)

  def create_document(self, content):
    doc = QTextDocument(parent=None)
    layout = QPlainTextDocumentLayout(doc)
    doc.setDocumentLayout(layout)

    doc.setPlainText(content)
    return doc

  def update_document_content(self, document, content):
    document.setPlainText(content)

  def update_document(self, buffer, load_doc):
    if load_doc:
      self.editor_.setDocument(buffer.document_)
    else:
      buffer.document_ = self.editor_.document()

  def save_editing_state(self, buffer):
    buffer.text_cursor_ = self.editor_.textCursor()
    buffer.text_cursor_position_ = buffer.text_cursor_.position()

  def load_editing_state(self, buffer):
    if buffer.text_cursor_ is not None:
      buffer.text_cursor_.setPosition(buffer.text_cursor_position_)
      self.editor_.setTextCursor(buffer.text_cursor_)
      self.editor_.ensureCursorVisible()

  def get_document_content(self, document):
    return document.toPlainText()

  def get_color(self, c):
    color = QColor()

    color.setNamedColor(c)

    return color

  def __apply_theme(self, app):
    font = self.get_font()

    if font:
      app.setFont(font)

    p = app.palette()

    f_c = self.ctx_.get_theme_def_color('default', 'foreground')
    b_c = self.ctx_.get_theme_def_color('default', 'background')

    p.setColor(QPalette.Active, QPalette.Base, b_c)
    p.setColor(QPalette.Active, QPalette.Text, f_c)
    p.setColor(QPalette.Inactive, QPalette.Base, b_c)
    p.setColor(QPalette.Inactive, QPalette.Text, f_c)

    if platform.system() == 'Windows':
      # on windows platform repla
      c = QColor()
      c.setNamedColor('#308cc6')
      p.setColor(QPalette.Active, QPalette.Highlight, c)

      c = QColor()
      c.setNamedColor('#ffffff')
      p.setColor(QPalette.Active, QPalette.HighlightedText, c)

    app.setPalette(p)

  @Slot()
  def update_editor_viwe_port(self, rect, dy):
    if self.editor_ is None or len(self.ctx_.editor_view_port_handlers_) == 0:
      return

    v = reduce(
        lambda x, y: y + x,
        map(lambda x: x.get_editor_margin(),
            self.ctx_.editor_view_port_handlers_))

    if v != self.editor_.viewportMargins():
      self.editor_.setViewportMargins(v)

  def get_row_and_col(self):
    c = self.editor_.textCursor()
    current_block_number = c.blockNumber()
    current_block = self.editor_.document().findBlockByNumber(
        current_block_number)
    pos_in_block = c.positionInBlock()
    l = current_block.layout().lineForTextPosition(pos_in_block).lineNumber()

    for b_c in range(self.editor_.blockCount()):
      if b_c == current_block_number:
        break

      l += self.editor_.document().findBlockByNumber(b_c).lineCount()

    return (l + 1, c.columnNumber(), self.editor_.document().lineCount())

  def set_tab_width(self, tab_width):
    if self.editor_ is None:
      return

    distance = self.editor_.fontMetrics().horizontalAdvance(' ' * tab_width)

    logging.debug(f'set tab width:{distance} for {tab_width} spaces')
    self.editor_.setTabStopDistance(distance)

  @Slot(object)
  def __run_in_ui_thread(self, obj):
    if callable(obj):
      obj()

  def run_in_ui_thread(self, obj):
    self.run_in_ui_thread_signal_.emit(obj)

  def create_editor(self):
    self.splitter_ = QSplitter()
    editor = Editor(self.ctx_)
    editor.bind_keys()

    self.splitter_.addWidget(editor)

    return self.splitter_

  def editor_has_focus(self):
    return (self.editor_ is not None and self.editor_.hasFocus())
