from PySide6.QtCore import Slot, Qt, QRect, QSize
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

    self.textEdit_.setFocus(Qt.ActiveWindowFocusReason)
    self.update_geometry()

  def update_geometry(self):
    cr = self.parentWidget().contentsRect()

    self.setGeometry(QRect(cr.left(),
                           cr.bottom() - cr.height() / 4,
                           cr.width(),
                           cr.height() / 4))

  def sizeHint(self):
    cr = self.parentWidget().contentsRect()

    return QSize(cr.width(), cr.height() / 4)

class ListContentWindow(ContentWindow):
  def __init__(self, parent=None):
    super().__init__(QListWidget(), parent)

