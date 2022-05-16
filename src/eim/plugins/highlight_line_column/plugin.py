from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QColor, QTextFormat
from PySide6.QtWidgets import QTextEdit

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

      line_color = self.ctx.get_theme_def_color('highlight', 'background',
                                                QColor(Qt.yellow).lighter(120))
      selection.format.setBackground(line_color)

      selection.format.setProperty(QTextFormat.FullWidthSelection, True)

      selection.cursor = self.editor_.textCursor()
      selection.cursor.clearSelection()

      extra_selections.append(selection)

    self.editor_.setExtraSelections(extra_selections)
