import os
import sys
import argparse
import logging
import pathlib

from appdirs import AppDirs
from yapsy.PluginManager import PluginManager

from .app_config import default_config, load_config
from .behavior_context import BehaviorContext

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

  def __load_config_file(self, config):
    if config and config.is_file():
      logging.debug('load {} and merge'.format(config))
      self.config.update(load_config(config))
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

    self.content_window_ = None
    logging.debug('close previous content window done')

  def show_list_content_window(self):
    self.close_content_window()

    self.content_window_ = self.ui_helper.show_list_content_window()
    logging.debug('show new list content window')

  def bind_key(self, key_seq, cmd_or_callable, binding_context=None):
    binding_context = self.get_behavior_context(binding_context)

    binding_context.bind_key(key_seq, cmd_or_callable)

    self.ui_bind_key(key_seq)

  def register_command(self, cmd_name, cmd_callable, cmd_context=None):
    binding_context = self.get_behavior_context(cmd_context)

    binding_context.register_command(cmd_name, cmd_callable)

  def get_behavior_context(self, behavior_context=None):
    if behavior_context is None:
      return self.global_behavior_context_

    try:
      return self.behavior_contexts_[behavior_context]
    except (KeyError):
      bc = BehaviorContext(self, self.global_behavior_context_)
      self.behavior_contexts_[behavior_context] = bc

    return bc

  def switch_behavior_context(self, behavior_context=None):
    if behavior_context is None:
      self.current_behavior_context_ = self.global_behavior_context_
    else:
      behavior_context = self.get_behavior_context(behavior_context)
      self.current_behavior_context_ = behavior_context

  def ui_bind_key(self, key_seq):
    if key_seq in self.ui_key_bindings_:
      return

    sc = self.ui_helper.bind_key(key_seq,
                                 lambda: self.key_binding_func(key_seq))
    self.ui_key_bindings_[key_seq] = sc

  def key_binding_func(self, key_seq):
    c = self.current_behavior_context_.get_keybinding_callable(key_seq)

    if callable(c):
      c()
    else:
      logging.warn('key seq:{} binding function is not callable:{}'.format(
          key_seq, c))

  def init_commands_and_key_bindings(self):
    self.ui_helper.init_commands_and_key_bindings()
    self.register_commands()
    self.bind_keys()

  def register_commands(self):
    self.register_command('close_content_window',
                          lambda c: c.close_content_window(), 'content_window')

  def bind_keys(self):
    self.bind_key('Esc', 'close_content_window', 'content_window')
