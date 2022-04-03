from PySide6.QtCore import Slot, Qt
from PySide6.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QListWidget


class ContentWindow(QWidget):
  def __init__(self, content_widget, parent=None):
    super().__init__(parent)

    self.content_widget_ = content_widget

    self.textEdit_ = QLineEdit()

    layout = QVBoxLayout()
    layout.addWidget(self.content_widget_)
    layout.addWidget(self.textEdit_)
    self.setLayout(layout)

class ListContentWindow(ContentWindow):
  def __init__(self, parent=None):
    super().__init__(QListWidget(), parent)

