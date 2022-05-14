import logging
import threading

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from multiprocessing import shared_memory


# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
  rpc_paths = ('/RPC2', )


class EditorServer(threading.Thread):

  def __init__(self, ctx):
    super().__init__()

    self.ctx_ = ctx
    self.random_server_addr_ = \
      ctx.args.server == True or ctx.args.server is None
    self.server_ = SimpleXMLRPCServer(
        ('', 0) if self.random_server_addr_ else ctx.args.server,
        requestHandler=RequestHandler)

    self.server_.register_function(self.__process_cmd_line_args,
                                   'process_cmd_line_args')

    self.shm_server_addr_ = None
    if self.random_server_addr_:
      self.__save_random_server_addr()

  def run(self):
    self.server_.serve_forever()

  def shutdown(self):
    self.__remove_random_server_addr()
    self.server_.shutdown()

  def __save_random_server_addr(self):
    ip, port = self.server_.server_address

    server_addr = bytearray(f'{ip}:{port}:', 'utf-8')

    self.shm_server_addr_ = shared_memory.SharedMemory(name='eim_server_addr',
                                                       create=True,
                                                       size=len(server_addr))

    logging.debug(
        f'save server addr:{server_addr} to {self.shm_server_addr_.name}')

    self.shm_server_addr_.buf[:] = server_addr[:]

  def __remove_random_server_addr(self):
    try:
      if self.shm_server_addr_ is None:
        return

      self.shm_server_addr_.unlink()
      self.shm_server_addr_ = None
    except:
      logging.exception('remove server addr failed')

  def __process_cmd_line_args(self, cur_dir, args, process_client_server_arg):
    self.ctx_.run_in_ui_thread(lambda: self.ctx_.process_cmd_line_args(
        cur_dir, args, process_client_server_arg))

    return True
