import logging
from io import StringIO
from pathlib import Path
import re

from .ag_tool import AgTool


class PyEverythingTool(AgTool):

  def __init__(self, ctx):
    super().__init__(ctx)

  def is_working(self):
    cmd_args = ['pyeverything', '--help']

    try:
      return len(self._run_cmd(cmd_args)) > 0
    except:
      return False

  def _get_list_match_file_name_cmd_args(self, dir, pattern):
    if not self.__has_pyeverything_index(dir):
      return super()._get_list_match_file_name_cmd_args(dir, pattern)

    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.extend(['query', '--no_color', '-p'])

    if len(pattern) > 0:
      cmd_args.append(f'{dir.resolve().as_posix()}/.*{pattern}')
    else:
      cmd_args.append(f'{dir.resolve().as_posix()}/.*')

    return cmd_args

  def _get_list_match_files_cmd_args(self, dir, pattern):
    if not self.__has_pyeverything_index(dir):
      return super()._get_list_match_files_cmd_args(dir, pattern)

    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.extend(['query', '--ackmate', '--no_color'])

    cmd_args.extend(['-c', pattern])

    if dir is not None:
      cmd_args.extend(['-p', f'{dir.resolve().as_posix()}'])

    return cmd_args

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

    cmd_args = ['pyeverything']
    if everything_path is not None:
      loc = everything_path.read_text(encoding='utf-8').strip('\n').strip('\r')
      if len(loc) > 0:
        logging.debug(f'pyeverything use index at {loc}')
        cmd_args.extend(['-l', loc])

    return cmd_args

  def __has_pyeverything_index(self, dir):
    cmd_args = self.__prepare_everything_cmds(dir)

    cmd_args.append('list')

    lines = StringIO(self._run_cmd(cmd_args, dir)).readlines()

    for line in lines:
      if dir is None:
        return True

      matches = re.match(r'path:(.*), modified time:(.*)', line)

      if matches is not None:
        logging.debug(f'index for path:{matches[1]}')

        if dir.resolve().as_posix().startswith(matches[1]):
          return True

    return False
