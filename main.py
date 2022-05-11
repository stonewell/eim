import os
import sys
import logging

os.environ['QT_QPA_PLATFORMTHEME'] = 'eim'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(__file__), 'plugins', 'qpa')

from ui.editor import Editor
from ui.ui_helper import UIHelper

from core.context import EditorContext

if __name__ == "__main__":
  ctx = EditorContext()
  ctx.ui_helper = UIHelper(ctx)

  app = ctx.ui_helper.create_application()

  editor = Editor(ctx)

  ctx.init_commands_and_key_bindings()

  ctx.switch_behavior_context()

  if ctx.process_cmd_line_args():
    editor.bind_keys()
    editor.show()

    sys.exit(app.exec())
  else:
    logging.debug(
        '''command line argument processed, won't start main window''')
    sys.exit(0)
