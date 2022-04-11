import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from ui.editor import Editor
from ui.ui_helper import UIHelper

from core.context import EditorContext


class EIMApplication(QApplication):

  def __init__(self, *args):
    super().__init__(*args)


if __name__ == "__main__":
  ctx = EditorContext()
  ctx.ui_helper = UIHelper(ctx)

  ctx.app = app = EIMApplication(sys.argv[1:])

  font = ctx.ui_helper.get_font()

  if font:
    app.setFont(font)

  editor = Editor(ctx)
  ctx.ui_helper.set_current_window(editor)

  ctx.init_commands_and_key_bindings()

  ctx.switch_behavior_context()

  editor.show()

  sys.exit(app.exec())
