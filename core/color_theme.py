import json
import logging
from .app_config import DictQuery


class ColorTheme(object):

  def __init__(self, theme_path):
    self.theme_path_ = theme_path

    self.__load_theme()

  def __load_theme(self):
    data = {'color': {}, 'theme': {}}
    for f in self.theme_path_.iterdir():
      try:
        if f.is_file() and f.suffix.lower() == '.json':
          tmp = json.loads(f.read_text('utf-8'))

          for key in ['color', 'theme']:
            try:
              data[key].update(tmp[key])
            except (KeyError):
              pass
      except:
        logging.exception(f'load theme file:{f.resolve()} failed')

    self.data_ = DictQuery(data)
    self.base_theme_def_ = self.default_theme_def_ = {
        'foreground': '#3F3F3F',
        'background': '#DCDCDC',
        'weight': 'normal',
    }
    self.default_theme_def_ = self.get_theme_def('default') or self.base_theme_def_

  def get_theme_def(self, theme_key):
    v = self.data_.get(f'theme/{theme_key}', None)

    if v is None:
      return None

    tmp = {}
    tmp.update(self.default_theme_def_)
    tmp.update(v)

    return tmp

  def get_color_def(self, color_key):
    return self.data_.get(f'color/{color_key}', None)
