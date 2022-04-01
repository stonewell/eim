import sys

from PySide6.QtWidgets import QApplication

from ui.editor import Editor
from ui.ui_helper import UIHelper

from core.context import EditorContext

if __name__ == "__main__":
  ctx = EditorContext()
  ctx.ui_helper = UIHelper(ctx)

  app = QApplication(sys.argv)

  font = ctx.ui_helper.get_font()

  if font:
    app.setFont(font)

  editor = Editor(ctx)
  editor.setWindowTitle("EIM")
  editor.show()
  sys.exit(app.exec())
