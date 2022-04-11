import os
import sys

os.environ['QT_QPA_PLATFORMTHEME'] = 'eim'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(os.path.dirname(__file__), 'plugins', 'qpa')

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QGuiApplication

from ui.editor import Editor
from ui.ui_helper import UIHelper

from core.context import EditorContext


class EIMApplication(QApplication):

  def __init__(self, *args):
    super().__init__(*args)


if __name__ == "__main__":
  ctx = EditorContext()
  ctx.ui_helper = UIHelper(ctx)

  ctx.app = app = EIMApplication()

  font = ctx.ui_helper.get_font()

  if font:
    app.setFont(font)

  editor = Editor(ctx)
  ctx.ui_helper.set_current_window(editor)

  ctx.init_commands_and_key_bindings()

  ctx.switch_behavior_context()

  editor.bind_keys()
  editor.show()

  sys.exit(app.exec())
