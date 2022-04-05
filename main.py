import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from ui.editor import Editor
from ui.ui_helper import UIHelper

from core.context import EditorContext


if __name__ == "__main__":
  ctx = EditorContext()
  ctx.ui_helper = UIHelper(ctx)

  ctx.app = app = QApplication(sys.argv[1:])

  font = ctx.ui_helper.get_font()

  if font:
    app.setFont(font)

  editor = Editor(ctx)
  ctx.ui_helper.set_current_window(editor)

  ctx.ui_helper.bind_key('Alt+X',
                         ctx.show_list_content_window)

  editor.show()

  sys.exit(app.exec())
