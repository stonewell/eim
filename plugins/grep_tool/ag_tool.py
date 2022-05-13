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
              StringIO(self.__run_cmd(cmd_args, dir)).readlines()))
    except:
      return []
