import logging

from PySide6.QtWidgets import QTextEdit, QHBoxLayout

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
