import os
import sys
import argparse
import logging
import pathlib

from appdirs import AppDirs
from yapsy.PluginManager import PluginManager

from .app_config import default_config, load_config
from .behavior_context import BehaviorContext
from .builtin_commands import BuiltinCommands
from .buffer import EditorBuffer

EIM_CONFIG = 'eim.json'
EIM_PLUGINS = 'plugins'


class EditorContext(object):

  def __init__(self):
    super().__init__

    self.appdirs_ = AppDirs('eim', 'angsto-tech')

    self.args = args = self.parse_arguments()
    if args.debug > 0:
      logging.getLogger('').setLevel(logging.DEBUG)
    else:
      logging.getLogger('').setLevel(logging.INFO)

    logging.debug('debug level:{}'.format(args.debug))

    self.content_window_ = None
    self.global_behavior_context_ = BehaviorContext(self)
    self.behavior_contexts_ = {}
    self.ui_key_bindings_ = {}
    self.current_behavior_context_ = self.global_behavior_context_
    self.command_history_ = []
    self.current_buffer_ = None
    self.buffers_ = []

    self.validate_args(args)

    self.__load_config()

    self.__load_plugins()

  @staticmethod
  def parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("-d",
                        "--debug",
                        help="print debug information",
                        action="count",
                        default=0)
    parser.add_argument("-v",
                        "--version",
                        action="version",
                        version='%(prog)s 1.0')
    parser.add_argument("-c",
                        "--config",
                        type=pathlib.Path,
                        help='config file path',
                        required=False,
                        metavar='<config file path>')
    parser.add_argument('-p',
                        "--plugins",
                        help="directory to load plugins",
                        required=False,
                        type=pathlib.Path,
                        metavar='<plugins directory>')

    return parser.parse_args()

  @staticmethod
  def validate_args(args):
    pass

  def __merge_keys(self, old_keys, new_keys):
    for key in old_keys:
      if key in new_keys:
        if isinstance(old_keys[key], dict) and isinstance(new_keys[key], dict):
          old_keys[key].update(new_keys[key])
          new_keys[key].update(old_keys[key])

    old_keys.update(new_keys)
    new_keys.update(old_keys)

  def __load_config_file(self, config):
    if config and config.is_file():
      logging.debug('load {} and merge'.format(config))
      new_config = load_config(config)

      old_keys = self.config.get('/app/keys', {})
      new_keys = new_config.get('/app/keys', {})
      self.__merge_keys(old_keys, new_keys)
      self.config.update(new_config)
    else:
      logging.debug('config file:{} is not exists'.format(
          config.resolve() if config else 'None'))

  def __load_config(self):
    args = self.args

    self.config = default_config()

    #try site config
    site_config = pathlib.Path(self.appdirs_.site_config_dir) / EIM_CONFIG

    self.__load_config_file(site_config)

    #try user config
    user_config = pathlib.Path(self.appdirs_.user_config_dir) / EIM_CONFIG

    self.__load_config_file(user_config)

    #try local config
    local_config = pathlib.Path(os.path.dirname(__file__)) / '..' / EIM_CONFIG

    self.__load_config_file(local_config)

    #load custom config
    self.__load_config_file(args.config)

    logging.debug('config:{}'.format(self.config.get('/app/font')))
    logging.debug('config keys:{}'.format(self.config.get('/app/keys')))

  def __load_plugin_dir(self, plugin_dir):
    if not plugin_dir or not plugin_dir.is_dir():
      logging.debug('plugin directory:{} is not exists'.format(
          plugin_dir.resolve() if plugin_dir else 'None'))
      return

    pm = PluginManager()
    pm.setPluginPlaces([plugin_dir])

    # Load all plugins
    pm.collectPlugins()

    for pluginInfo in pm.getAllPlugins():
      if self.config.get('plugins/{}/enabled'.format(pluginInfo.name), True):
        self.plugins_[pluginInfo.name] = pluginInfo
      else:
        logging.debug('plugin:{} disabled'.format(pluginInfo.name))

  def __load_plugins(self):
    args = self.args
    self.plugins_ = {}

    #try local plugin
    local_plugin = pathlib.Path(os.path.dirname(__file__)) / '..' / EIM_PLUGINS

    self.__load_plugin_dir(local_plugin)

    #try site plugin
    site_plugin = pathlib.Path(self.appdirs_.site_data_dir) / EIM_PLUGINS

    self.__load_plugin_dir(site_plugin)

    #try user plugin
    user_plugin = pathlib.Path(self.appdirs_.user_data_dir) / EIM_PLUGINS

    self.__load_plugin_dir(user_plugin)

    #load custom plugin
    self.__load_plugin_dir(args.plugins)

    self.__activate_plugins()

  def __activate_plugins(self):
    for key in self.plugins_:
      logging.debug('activate plugin:{}'.format(key))
      self.plugins_[key].plugin_object.activate()
      self.plugins_[key].plugin_object.ctx = self

  def update_plugins_with_current_window(self, editor):
    for key in self.plugins_:
      try:
        self.plugins_[key].plugin_object.set_current_window(editor)
      except:
        pass

  def close_content_window(self):
    if self.content_window_:
      self.content_window_.close()
      logging.debug('close previous content window')
      self.ui_helper.focus_editor()

    self.content_window_ = None
    logging.debug('close previous content window done')

  def create_list_content_window(self):
    self.close_content_window()

    self.content_window_ = self.ui_helper.create_list_content_window()

    return self.content_window_

  def bind_key(self, key_seq, cmd_or_callable, binding_context=None):
    binding_context = self.get_behavior_context(binding_context)

    binding_context.bind_key(key_seq, cmd_or_callable)

    self.ui_bind_key(key_seq)

  def register_command(self,
                       cmd_name,
                       cmd_callable,
                       cmd_context=None,
                       save_history=True):
    binding_context = self.get_behavior_context(cmd_context)

    binding_context.register_command(cmd_name, cmd_callable, save_history)

  def get_behavior_context(self, behavior_context=None, parent_context=None):
    if behavior_context is None:
      self.global_behavior_context_.name = 'global'
      return self.global_behavior_context_

    try:
      return self.behavior_contexts_[behavior_context]
    except (KeyError):
      bc = BehaviorContext(
          self,
          parent_context if parent_context else self.global_behavior_context_)
      bc.name = behavior_context
      self.behavior_contexts_[behavior_context] = bc

    return bc

  def switch_behavior_context(self, behavior_context=None):
    if behavior_context is None:
      self.current_behavior_context_ = self.global_behavior_context_
    else:
      self.current_behavior_context_ = self.get_behavior_context(
          behavior_context)

    logging.debug(
        'switch behavior context:{}, now behavior context is:{}'.format(
            behavior_context, self.current_behavior_context_.name))

  def ui_bind_key(self, key_seq):
    if key_seq in self.ui_key_bindings_:
      return

    sc = self.ui_helper.bind_key(key_seq,
                                 lambda: self.key_binding_func(key_seq))
    self.ui_key_bindings_[key_seq] = sc

  def key_binding_func(self, key_seq):
    logging.debug('call key binding on context:{}'.format(
        self.current_behavior_context_.name))
    c = self.current_behavior_context_.get_keybinding_callable(key_seq)

    if callable(c):
      c(self)
    else:
      logging.warn('key seq:{} binding function is not callable:{}'.format(
          key_seq, c))

  def init_commands_and_key_bindings(self):
    self.ui_helper.init_commands_and_key_bindings()
    self.register_commands()
    self.bind_keys()

  def register_commands(self):
    self.register_command(BuiltinCommands.CANCEL,
                          lambda c: c.close_content_window(), 'content_window',
                          False)

  def __bind_config_keys(self, keys, binding_context=None):
    for key in keys:
      b = keys[key]

      if isinstance(b, dict):
        self.__bind_config_keys(b, key)
      else:
        logging.debug('binding key:{} to {} in context:{}'.format(
            key, b, binding_context))
        self.bind_key(key, b, binding_context)

  def bind_keys(self):
    keys = self.config.get('/app/keys', {})

    self.__bind_config_keys(keys)

  def run_command(self, cmd_name, cmd_callable=None, save_history=True):
    logging.debug('running command:{}'.format(cmd_name))

    if cmd_callable is None:
      cmd_callable = self.current_behavior_context_.get_command_callable(
          cmd_name)
      #command callable will handle save history
      save_history = False

    if not callable(cmd_callable):
      logging.warning('cmd:{} is not found'.format(cmd_name))
      return

    cmd_callable(self)

    if save_history:
      try:
        self.command_history_.remove(cmd_name)
      except (ValueError):
        pass

      self.command_history_.append(cmd_name)
    else:
      logging.debug('run cmd:{} skip history'.format(cmd_name))

  def get_commands(self):
    commands = self.command_history_[:]

    all_cmds = self.current_behavior_context_.get_commands()

    all_cmds = [cmd for cmd in all_cmds if cmd not in commands]

    commands.extend(all_cmds)

    return commands

  def hook_command(self,
                   cmd_name,
                   cmd_or_callable,
                   binding_context=None,
                   save_history=True):
    if binding_context is None:
      self.current_behavior_context_.hook_command(cmd_name, cmd_or_callable,
                                                  save_history)
    else:
      self.get_behavior_context(binding_context).hook_command(
          cmd_name, cmd_or_callable, save_history)

  def get_current_buffer_dir(self):
    return pathlib.Path('.')

  def create_document(self, content):
    return self.ui_helper.create_document(content)

  def load_buffer(self, file_path):
    for buf in self.buffers_:
      if file_path == buf.file_path_:
        self.__set_current_buffer(buf)
        return

    buffer = EditorBuffer(self)

    buffer.load_file(file_path)

    self.__set_current_buffer(buffer)

  def __set_current_buffer(self, buffer):
    self.buffers_.insert(0, buffer)
    self.current_buffer_ = buffer

    self.ui_helper.update_document(self.current_buffer_, True)

  def switch_to_buffer(self, buf_name):
    for buf in self.buffers_:
      if buf_name == buf.name():
        self.ui_helper.update_document(self.current_buffer_, False)
        self.current_buffer_ = buf
        self.ui_helper.update_document(self.current_buffer_, True)
        return

    buf = EditorBuffer(self, buf_name)

    self.__set_current_buffer(buf)

  def buffer_names(self):
    return [buf.name() for buf in self.buffers_]
