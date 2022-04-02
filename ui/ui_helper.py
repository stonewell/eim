import logging

from PySide6.QtGui import QFont

class UIHelper(object):
    def __init__(self, ctx):
        super().__init__()

        self.ctx_ = ctx

    def get_font(self):
        fConfig = self.ctx_.config.get('app/font')

        f = None

        if isinstance(fConfig, str):
            f = QFont()
            f.fromString(fConfig)
        else:
            family = fConfig.get('family', QFont().defaultFamily())
            ptSize = fConfig.get('size', 14)
            bold = fConfig.get('bold', False)
            italic = fConfig.get('italic', False)

            logging.debug('family:{}, ptSize:{}, bold:{}, italic:{}'.format(family, ptSize, bold, italic))

            f = QFont(family, ptSize, QFont.Bold if bold else -1, italic)

        return f

    def set_current_window(self, editor):
      self.editor_ = editor

      self.ctx_.update_plugins_with_current_window(editor)
