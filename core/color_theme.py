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
    self.default_theme_def_ = self.get_theme_def(
        'default') or self.base_theme_def_

  def get_theme_def(self, theme_key):
    if theme_key.startswith('keyword.'):
      theme_key = 'keyword'

    v = self.data_.get(f'theme/{theme_key}', None)

    if v is None:
      m = self.theme_def_mapping()

      try:
        mapped_theme_def = m[theme_key]
        if isinstance(mapped_theme_def, dict):
          if 'name' in mapped_theme_def:
            name = mapped_theme_def['name']
          else:
            name = None
        else:
          name = mapped_theme_def

        if name is not None:
          tmp = self.get_theme_def(name)
        else:
          tmp = {}

        if isinstance(mapped_theme_def, dict):
          tmp.update(mapped_theme_def)

        return tmp
      except:
        return None

    tmp = {}
    tmp.update(self.default_theme_def_)
    tmp.update(v)

    return tmp

  def get_color_def(self, color_key):
    return self.data_.get(f'color/{color_key}', None)

  def theme_def_mapping(self):
    return {
        'function': 'function-name',
        'function.call': 'function-name',
        'function.builtin': 'builtin',
        'function.special': 'preprocessor',
        'function.macro': 'preprocessor',
        'method': 'function',
        'method.call': 'function.call',
        'type.parameter': 'variable-name',
        'type.argument': 'type',
        'type.builtin': 'builtin',
        'type.super': 'type',
        'constructor': 'type',
        'variable': 'variable-name',
        'variable.parameter': 'variable',
        'variable.builtin': 'builtin',
        'variable.special': 'warning',
        "property": {
            "name": "constant",
            "italic": True
        },
        'property.definition': 'variable.parameter',
        'string.special': {
            "name": 'string',
            "weight": 'bold',
        },
        'escape': 'keyword',
        'embedded': 'default',
        'operator': 'keyword',
        'label': 'preprocessor',
        'constant.builtin': 'constant',
        'number': 'constant',
        'punctuation': 'default',
        'punctuation.bracket': 'punctuation',
        'punctuation.delimiter': 'punctuation',
        'punctuation.special': 'keyword',
        'tag': 'builtin',
        'attribute': 'preprocessor',
        'character': 'string',
        'number': 'constant',
        'boolean': 'constant',
        'float': 'constant',
        'conditional': 'keyword',
        'repeat': 'keyword',
        'exception': 'keyword',
        'include': 'preprocessor',
        'define': 'preprocessor',
        'macro': 'define',
        'precondit': 'preprocessor',
        'storageclass': 'keyword',
        'structure': 'type',
        'typedef': 'type',
        'specialchar': 'constant',
        'delimiter': 'comment-delimiter',
        'sepcialcomment': 'comment-delimiter',
        'debug': 'preprocessor',
        'parameter': 'variable',
        '_isinstance': 'builtin',
        'none': 'builtin',
        'error': 'warning',
    }
