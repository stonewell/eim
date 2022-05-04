def default_editor_config():
  return dict([('indent_style', 'space'), ('indent_size', '2'),
               ('charset', 'utf-8'), ('trim_trailing_whitespace', 'true'),
               ('insert_final_newline', 'true'), ('tab_width', '2')])

if __name__ == '__main__':
  print(default_editor_config())
