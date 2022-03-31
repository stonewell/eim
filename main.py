import sys
from PySide6.QtWidgets import QApplication
from ui.editor import Editor

"""PySide6 port of the widgets/codeeditor example from Qt5"""

if __name__ == "__main__":
  app = QApplication([])
  editor = Editor()
  editor.setWindowTitle("Code Editor Example")
  editor.show()
  sys.exit(app.exec())
