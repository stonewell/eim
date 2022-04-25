import logging

from PySide6.QtWidgets import QTextEdit, QHBoxLayout
from PySide6.QtWidgets import QAbstractSlider
from PySide6.QtGui import QTextCursor

from .list_content_window import ListContentWindow


class ListWithPreviewContentWindow(ListContentWindow):

  def __init__(self, ctx, parent=None):
    ListContentWindow.__init__(self, ctx, parent)

    lc = self.ctx_.get_behavior_context('list_content_window')
    lpc = self.ctx_.get_behavior_context('list_with_preview_content_window')
    lpc.set_parent_context(lc)

  def create_content_widget(self):
    list_widget = super().create_content_widget()

    self.preview_edit_ = QTextEdit()
    self.preview_edit_.verticalScrollBar().setHidden(True)

    layout = QHBoxLayout()
    layout.addWidget(list_widget)
    layout.addWidget(self.preview_edit_)
    return layout

  def _page_up_down(self, ctx, pageDown):
    logging.debug('preview window up down')

    pe = self.preview_edit_

    pe.verticalScrollBar().triggerAction(
        QAbstractSlider.SliderPageStepAdd if pageDown else QAbstractSlider.
        SliderPageStepSub)
    cursor = pe.textCursor()
    moved = cursor.movePosition(
        QTextCursor.Down if pageDown else QTextCursor.Up,
        QTextCursor.MoveAnchor,
        pe.verticalScrollBar().pageStep())

    logging.debug('preview window cursor moved:{}, steps:{}'.format(
        moved,
        pe.verticalScrollBar().pageStep()))

    if moved:
      pe.setTextCursor(cursor)
      pe.ensureCursorVisible()
