import logging
import subprocess
from io import StringIO
from pathlib import Path


class AgTool(object):

  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

  def is_working(self):
    cmd_args = ['ag', '--version']

    try:
      return len(self.__run_cmd(cmd_args)) > 0
    except:
      return False

  def __run_cmd(self, cmd_args, dir=None):
    proc = subprocess.run(cmd_args, capture_output=True, cwd=dir)

    if proc.stderr:
      logging.error(
          f'running ag failed:{proc.stderr.decode("utf-8", errors="ignore")}')

    proc.check_returncode()

    return proc.stdout.decode('utf-8', errors='ignore')

  def list_match_file_name(self, dir, pattern):
    cmd_args = ['ag', '-l', '--nocolor']

    if len(pattern) > 0:
      cmd_args.extend(['-G', pattern])

    try:
      return filter(
          lambda x: x.is_file(),
          map(lambda x: Path(x.strip()),
              stringio(self.__run_cmd(cmd_args, dir)).readlines()))
    except:
      return []

  def list_match_files(self, dir, pattern):
    cmd_args = [
        'ag', '--ackmate', '--nocolor', pattern,
        dir.resolve().as_posix()
    ]

    try:
      lines = map(lambda x: x.strip(),
                  StringIO(self.__run_cmd(cmd_args, dir)).readlines())

      matches = []
      file = None
      for line in lines:
        if len(line) == 0:
          file = None
          continue

        if line[0] == ':':
          file = line[1:]
        else:
          if file is None:
            logging.warning(f'no file found for line:[{line}]')
            continue

          logging.debug(f'processing line:{line}')

          parts = line.split(':')

          pos_parts = parts[0].split(';')

          line = int(pos_parts[0])

          col_lengths = []

          for col_len_parts in pos_parts[1].split(','):
            pp = col_len_parts.split(' ')
            column = int(pp[0])
            length = int(pp[1])

            col_lengths.append((column, length))

          logging.debug(
              f'file:{file}, line:{line}, col_len:{col_lengths}')

          matches.append((Path(file), line, col_lengths, parts[1]))

      return matches
    except:
      logging.exception('fail to agrep')
      return []


if __name__ == '__main__':
  t = AgTool(None)
  for m in t.list_match_files(Path('.').cwd(), 'ask_for'):
    print(m)
