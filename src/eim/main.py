import os
import sys
import logging

os.environ['QT_QPA_PLATFORMTHEME'] = 'eim'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(__file__), 'plugins', 'qpa')

from .ui.ui_helper import UIHelper

from .core.context import EditorContext


def main():
  ctx = EditorContext()

  if ctx.process_cmd_line_client_args():
    logging.debug(
        '''command line argument processed, won't start main window''')
    sys.exit(0)

  ctx.ui_helper = UIHelper(ctx)

  app = ctx.ui_helper.create_application()

  editor = ctx.ui_helper.create_editor()

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


if __name__ == "__main__":
  main()
