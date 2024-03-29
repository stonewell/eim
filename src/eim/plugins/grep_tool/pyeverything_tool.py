import logging
from io import StringIO
from pathlib import Path
import re

try:
  from pyeverything.frontend.cmd.run import run_with_args_iter as pyeverything_run_with_args
  NO_PYEVERYTHING = False
  logging.info('using pyeverything tool for grep')
except:
  logging.info('using ag tool for grep')
  NO_PYEVERYTHING = True

from .ag_tool import AgTool


class PyEverythingTool(AgTool):

  def __init__(self, ctx):
    super().__init__(ctx)

  def is_working(self):
    return not NO_PYEVERYTHING

  def _get_list_match_file_name_cmd_args(self, dir, pattern):
    if not self.__has_pyeverything_index(dir):
      return super()._get_list_match_file_name_cmd_args(dir, pattern)

    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.extend(['query', '--no_color', '--limit', '50', '-p'])

    if len(pattern) > 0:
      cmd_args.append(f'{pattern}')
    else:
      cmd_args.append(f'{dir.resolve().as_posix()}/.*')

    return cmd_args

  def _get_list_match_files_cmd_args(self, dir, pattern):
    if not self.__has_pyeverything_index(dir):
      return super()._get_list_match_files_cmd_args(dir, pattern)

    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.extend(['query', '--ackmate', '--no_color', '--limit', '50'])

    cmd_args.extend(['-c', pattern])

    if dir is not None:
      cmd_args.extend(['-p', f'{dir.resolve().as_posix()}'])

    return cmd_args

  def _run_cmd(self, cmd_args, dir=None):
    if not self.__has_pyeverything_index(dir):
      return super()._run_cmd(cmd_args, dir)

    try:
      return pyeverything_run_with_args(cmd_args, True)
    except:
      logging.exception('run pyeverything failed')

  @staticmethod
  def __find_pyeverything(path: Path) -> Path:
    found = list(path.glob('.pyeverything'))

    if len(found) > 0:
      return path.resolve() / '.pyeverything'

    if path.parent == path:
      return None

    return PyEverythingTool.__find_pyeverything(path.parent)

  def __prepare_everything_cmds(self, dir):
    everything_path = None

    if dir is not None:
      everything_path = PyEverythingTool.__find_pyeverything(dir)

    cmd_args = []
    if everything_path is not None:
      loc = everything_path.read_text(encoding='utf-8').strip('\n').strip('\r')
      if len(loc) > 0:
        logging.debug(f'pyeverything use index at {loc}')
        cmd_args.extend(['-l', loc])

    return cmd_args

  def __has_pyeverything_index(self, dir):
    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.append('list')

    pyeverything_run_with_args(cmd_args, True)

    for line in pyeverything_run_with_args(cmd_args, True):
      if dir is None:
        return True

      matches = re.match(r'path:(.*), modified time:(.*)', line)

      if matches is not None:
        logging.debug(f'index for path:{matches[1]}')

        if dir.resolve().as_posix().startswith(matches[1]):
          return True

    logging.info('using ag tool for grep')
    return False
