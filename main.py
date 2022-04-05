import sys

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QEvent, QObject, QCoreApplication

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

  ctx.bind_key('Alt+X',
               lambda c: c.show_list_content_window())
  ctx.bind_key('Alt+W',
               lambda c: c.close_content_window())
  ctx.register_command('close_content_window',
                       lambda c: c.close_content_window(),
                       'content_window')
  ctx.bind_key('Esc', 'close_content_window', 'content_window')
  ctx.bind_key('Alt+X', 'close_content_window', 'content_window')

  ctx.switch_behavior_context()

  editor.show()

  sys.exit(app.exec())
