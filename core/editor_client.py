import logging
import os

import xmlrpc.client
from multiprocessing import shared_memory

class EditorClient(object):
  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx

    if ctx.args.client == True or ctx.args.client is None:
      self.server_addr_ = self.__read_from_sharedmemory()
    else:
      self.server_addr_ = ctx.args.client

    if self.server_addr_ is None:
      logging.error('unable to connect to server')

  def call_server(self):
    if self.server_addr_ is None:
      logging.error('unable to connect to server')
      return

    cur_dir = os.path.abspath('.')
    args = self.ctx_.args.args

    logging.debug(f'connect to server:{self.server_addr_}')
    s = xmlrpc.client.ServerProxy(f'http://{self.server_addr_}')

    s.process_cmd_line_args(cur_dir, args, False)

  def __read_from_sharedmemory(self):
    shm_server_addr = None
    try:
      shm_server_addr = shared_memory.SharedMemory(name='eim_server_addr',
                                                 create=False)

      server_addr = bytes(shm_server_addr.buf[:shm_server_addr.size]).decode('utf-8')

      parts = server_addr.split(':')[:2]

      if parts[0] == '0.0.0.0':
        parts[0] = 'localhost'

      return ':'.join(parts[:2])
    except:
      logging.exception('unable to connect to server')
      return None
    finally:
      if shm_server_addr is not None:
        shm_server_addr.close()
