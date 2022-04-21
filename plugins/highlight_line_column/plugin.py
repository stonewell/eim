from PySide6.QtCore import Slot, Qt, QRect, QSize
from PySide6.QtGui import QColor, QPainter, QTextFormat
from PySide6.QtWidgets import QPlainTextEdit, QWidget, QTextEdit

from yapsy.IPlugin import IPlugin


class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)
    return

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor

    self.editor_.cursorPositionChanged.connect(self.highlight_current_line)
    self.highlight_current_line()

  @Slot()
  def highlight_current_line(self):
    extra_selections = []

    if not self.editor_.isReadOnly():
      selection = QTextEdit.ExtraSelection()

      line_color = self.__get_theme_highlight_color()
      selection.format.setBackground(line_color)

      selection.format.setProperty(QTextFormat.FullWidthSelection, True)

      selection.cursor = self.editor_.textCursor()
      selection.cursor.clearSelection()

      extra_selections.append(selection)

    self.editor_.setExtraSelections(extra_selections)

  def __get_theme_highlight_color(self):
    theme_def = self.ctx.color_theme_.get_theme_def('highlight')

    if theme_def is None:
      return QColor(Qt.yellow).lighter(120)

    return self.__get_color(theme_def, 'background')

  def __get_color(self, theme_def, color_key):
    c = self.ctx.color_theme_.get_color_def(theme_def[color_key])

    color = QColor()
    if c is None:
      color.setNamedColor(theme_def[color_key])
    else:
      color.setNamedColor(c)

    return color
