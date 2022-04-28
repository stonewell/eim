import logging
import re
import pathlib


def convert(content):
  v = content
  v = re.sub(';;\\s+.*$', '', v, flags=re.MULTILINE)
  v = re.sub(';\\s+.*$', '', v, flags=re.MULTILINE)
  v = re.sub('\\s+', ' ', v, flags=re.MULTILINE)

  vv = re.split(r'([()" \\])', v)

  if v != ''.join(vv):
    raise ValueError()

  in_string = False
  in_anyof = False
  in_contains = False
  back_slash = False

  new_vv = []

  for entry in vv:
    if len(entry) == 0:
      continue

    if entry == '(':
      pass
    elif entry == ')':
      if not in_string:
        if in_anyof:
          match_value = ''.join(['"^(', match_value, ')$"'])
          new_vv.append(match_value)
        elif in_contains:
          match_value = ''.join(['"^.*(', match_value, ').*$"'])
          new_vv.append(match_value)
        in_anyof = False
        in_contains = False
    elif entry == '"':
      if in_string and back_slash:
        pass
      else:
        in_string = not in_string

        if (in_anyof or in_contains) and in_string:
          if match_value != '':
            match_value += '|'
    elif entry == ' ':
      pass
    elif entry == '\\':
      pass
    else:
      if not in_string:
        if entry == '#lua-match?' or entry == '#match?' or entry == '#vim-match?':
          entry = '.match?'
        elif entry == '#any-of?':
          entry = '.match?'
          in_anyof = True
          match_value = ''
        elif entry == '#eq?':
          entry = '.eq?'
        elif entry == '#contains?':
          entry = '.match?'
          in_anyof = True
          match_value = ''

    if in_anyof or in_contains:
      if in_string:
        if entry != '"' or (entry == '"' and back_slash):
          match_value += entry
      elif entry != '"':
        new_vv.append(entry)
    else:
      new_vv.append(entry)

    if in_string:
      if entry == '\\':
        back_slash = not back_slash
      else:
        back_slash = False
    else:
      back_slash = False

  return ''.join(new_vv)

if __name__ == '__main__':
  a = pathlib.Path(r'/home/stone/.config/eim/neovim_tree_sitter/data/./queries/python/highlights.scm')
  print(convert(a.read_text()))
