import os
import sys
import logging

from .ui.ui_helper import UIHelper
from .core.context import EditorContext

GLOBAL_APP = None

__g_all_eims = []


def get_current_active_eim():
  for _eim in __g_all_eims:
    if _eim.is_active():
      return _eim

  raise ValueError('must have an active eim')


def get_next_eim(eim):
  try:
    index = __g_all_eims.index(eim)

    index += 1

    if index >= len(__g_all_eims):
      index = 0

    return __g_all_eims[index]
  except (ValueError):
    return __g_all_eims[0]


def add_eim(eim):
  __g_all_eims.append(eim)


class EIM(object):

  def __init__(self):
    self.ctx_ = ctx = EditorContext()

    ctx.ui_helper = UIHelper(ctx)
    ctx.ui_helper.eim_ = self

    add_eim(self)

  def initialize(self):
    global GLOBAL_APP
    if GLOBAL_APP is None:
      GLOBAL_APP = self.ctx_.ui_helper.create_application()

    self.editor_ = self.ctx_.ui_helper.create_editor()

    self.ctx_.init_commands_and_key_bindings()

    self.ctx_.switch_behavior_context()

  def process_cmd_line_and_run(self):
    if self.ctx_.process_cmd_line_client_args():
      logging.debug(
          '''command line argument processed, won't start main window''')
      sys.exit(0)

    self.initialize()

    if self.ctx_.process_cmd_line_args():
      self.editor_.show()

      global GLOBAL_APP
      sys.exit(GLOBAL_APP.exec())
    else:
      logging.debug(
          '''command line argument processed, won't start main window''')
      sys.exit(0)

  def is_active(self):
    return (self.ctx_.ui_helper.editor_has_focus()
            or self.ctx_.has_content_window_active())

  def process_key_binding(self, key_seq):
    self.ctx_.process_key_binding(key_seq)

  def activate(self):
    self.ctx_.ui_helper.activate_editor()
