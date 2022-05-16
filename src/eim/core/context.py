import os
import sys
import argparse
import logging
import pathlib
import json
import datetime
from pubsub import pub

from appdirs import AppDirs
from yapsy.PluginManager import PluginManager

from .app_config import default_config, load_config
from .behavior_context import BehaviorContext
from .builtin_commands import BuiltinCommands
from .buffer import EditorBuffer
from .url_helper import open_url as eim_open_url
from .color_theme import ColorTheme
from .editor_server import EditorServer
from .editor_client import EditorClient
from .project_root import find_project_root as eim_find_project_root

EIM_CONFIG = 'eim.json'
EIM_PLUGINS = 'plugins'

__g_all_buffers = []


def all_buffers():
  return __g_all_buffers


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
    logging.debug(f'running as server:{args.server}, client:{args.client}')
    logging.debug(f'running with editor argument:{args.args}')

    self.content_window_ = None
    self.global_behavior_context_ = BehaviorContext(self)
    self.behavior_contexts_ = {}
    self.ui_key_bindings_ = {}
    self.current_behavior_context_ = self.global_behavior_context_
    self.command_history_ = []
    self.current_buffer_ = None
    self.editor_view_port_handlers_ = []
    self.editor_server_ = None

    self.validate_args(args)

    if not (self.args.client is False):
      return

    self.__load_config()

    self.__load_plugins()

    self.__load_langs_mapping()

    self.__load_project_root_files()

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
    parser.add_argument('--server',
                        help="start the server",
                        required=False,
                        type=EditorContext.validate_server_addr,
                        nargs='?',
                        metavar='<SERVER_ADDR:SERVER_PORT>',
                        default=False)
    parser.add_argument('--client',
                        help="connect to server and send command, then quit",
                        required=False,
                        type=EditorContext.validate_server_addr,
                        nargs='?',
                        metavar='<SERVER_ADDR:SERVER_PORT>',
                        default=False)
    parser.add_argument('args',
                        help="editor argument such as files to be opened",
                        nargs='*',
                        metavar='<Editor Arguments>')

    return parser.parse_args()

  @staticmethod
  def validate_server_addr(value):
    if isinstance(value, str):
      parts = value.split(':')
      if len(parts) != 2 or int(parts[1]) == 0:
        raise argparse.ArgumentTypeError(
            'Value has to be in SERVER_ADDR:SERVER_PORT format')

      return (parts[0], int(parts[1]))

    return value

  @staticmethod
  def validate_args(args):
    pass

  def __deep_merge(self, old_dict, new_dict):
    for key in new_dict:
      if key in old_dict:
        if isinstance(old_dict[key], dict) and isinstance(new_dict[key], dict):
          self.__deep_merge(old_dict[key], new_dict[key])
        else:
          old_dict[key] = new_dict[key]
      else:
        old_dict[key] = new_dict[key]

  def __load_config_file(self, config):
    if config and config.is_file():
      logging.debug('load {} and merge'.format(config))
      new_config = load_config(config)

      self.__deep_merge(self.config, new_config)
    else:
      logging.debug('config file:{} is not exists'.format(
          config.resolve() if config else 'None'))

  def __load_config(self):
    args = self.args

    self.config = default_config()

    # try site config
    site_config = pathlib.Path(self.appdirs_.site_config_dir) / EIM_CONFIG

    self.__load_config_file(site_config)

    # try user config
    user_config = pathlib.Path(self.appdirs_.user_config_dir) / EIM_CONFIG

    self.__load_config_file(user_config)

    # try local config
    local_config = pathlib.Path(os.path.dirname(__file__)) / '..' / EIM_CONFIG

    self.__load_config_file(local_config)

    # load custom config
    self.__load_config_file(args.config)

    logging.debug('config:{}'.format(self.config.get('/app/font')))
    logging.debug('config keys:{}'.format(self.config.get('/app/keys')))
    logging.debug(
        f'config color-theme:{self.config.get("/app/color-theme", "zenburn")}')

    self.__load_color_theme()

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

    # try local plugin
    local_plugin = pathlib.Path(os.path.dirname(__file__)) / '..' / EIM_PLUGINS

    self.__load_plugin_dir(local_plugin)

    # try site plugin
    site_plugin = pathlib.Path(self.appdirs_.site_data_dir) / EIM_PLUGINS

    self.__load_plugin_dir(site_plugin)

    # try user plugin
    user_plugin = pathlib.Path(self.appdirs_.user_data_dir) / EIM_PLUGINS

    self.__load_plugin_dir(user_plugin)

    #load custom plugin
    self.__load_plugin_dir(args.plugins)

    self.__activate_plugins()

  def __activate_plugins(self):
    for key in self.plugins_:
      logging.debug('activate plugin:{}'.format(key))
      self.plugins_[key].plugin_object.ctx = self
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
      self.ui_helper.focus_editor()

    self.content_window_ = None
    logging.debug('close previous content window done')

  def create_list_content_window(self):
    self.close_content_window()

    self.content_window_ = self.ui_helper.create_list_content_window()

    return self.content_window_

  def create_input_content_window(self):
    self.close_content_window()

    self.content_window_ = self.ui_helper.create_input_content_window()

    return self.content_window_

  def create_list_with_preview_content_window(self):
    self.close_content_window()

    self.content_window_ = \
      self.ui_helper.create_list_with_preview_content_window()

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
    if behavior_context is None or behavior_context == 'global':
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
                                 lambda: self.process_key_binding(key_seq))
    self.ui_key_bindings_[key_seq] = sc

  def process_key_binding(self, key_seq):
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
    self.register_command(BuiltinCommands.SAVE,
                          lambda c: c.save_current_buffer())
    self.register_command(BuiltinCommands.SAVE_AS,
                          lambda c: c.save_current_buffer_as())

    self.register_command(BuiltinCommands.CLOSE_BUFFER,
                          lambda c: c.close_current_buffer())

    self.register_command('apply_editor_config', self.__apply_editor_config)
    self.register_command(BuiltinCommands.RELOAD_BUFFER,
                          self.__reload_current_buffer)

  def __reload_current_buffer(self, ctx):
    ctx.close_content_window()

    self.ui_helper.save_editing_state(self.current_buffer_)

    ctx.current_buffer_.reload_file()

    self.ui_helper.update_document(self.current_buffer_, True)
    self.ui_helper.load_editing_state(self.current_buffer_)
    self.current_buffer_.update_mode_line()
    self.current_buffer_.apply_editor_config()

    pub.sendMessage('buffer_changed', buf=self.current_buffer_)

  def __apply_editor_config(self, ctx):
    ctx.close_content_window()
    ctx.current_buffer_.apply_editor_config()

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

  def run_command(self,
                  cmd_name,
                  cmd_callable=None,
                  save_history=True,
                  *cmd_args):
    logging.debug(
        f'running command:{cmd_name}, callable:{cmd_callable}, save history:{save_history}, args:{cmd_args}'
    )

    if cmd_callable is None:
      cmd_callable = self.current_behavior_context_.get_command_callable(
          cmd_name)
      #command callable will handle save history
      save_history = False
      logging.debug(f'get callable from behaivor context:{cmd_callable}')

    if not callable(cmd_callable):
      logging.warning('cmd:{} is not found'.format(cmd_name))
      return None

    result = cmd_callable(self, *cmd_args)

    if save_history:
      try:
        self.command_history_.remove(cmd_name)
      except (ValueError):
        pass

      self.command_history_.append(cmd_name)
    else:
      logging.debug('run cmd:{} skip history'.format(cmd_name))

    return result

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
    if self.current_buffer_ is None or self.current_buffer_.file_path_ is None:
      return pathlib.Path('.')

    return self.current_buffer_.file_path_.parent

  def create_document(self, content):
    return self.ui_helper.create_document(content)

  def load_buffer(self, file_path):
    for buf in all_buffers():
      if file_path == buf.file_path_:
        self.__set_current_buffer(buf)
        return

    buffer = EditorBuffer(self)

    buffer.load_file(file_path)

    self.__set_current_buffer(buffer)

  def __set_current_buffer(self, buffer):
    try:
      all_buffers().remove(buffer)
    except:
      pass

    all_buffers().insert(0, buffer)

    if self.current_buffer_ is not None:
      self.ui_helper.save_editing_state(self.current_buffer_)

    self.current_buffer_ = buffer

    self.ui_helper.update_document(self.current_buffer_, True)
    self.ui_helper.load_editing_state(self.current_buffer_)
    self.current_buffer_.update_mode_line()
    self.current_buffer_.apply_editor_config()

    pub.sendMessage('buffer_changed', buf=buffer)

  def switch_to_buffer(self, buf_name):
    for buf in all_buffers():
      logging.debug('switch buf:{} -> {}'.format(buf_name, buf.name()))

      if buf_name == buf.name():
        self.__set_current_buffer(buf)
        return

    buf = EditorBuffer(self, buf_name)

    self.__set_current_buffer(buf)

  def buffer_names(self):
    return [buf.name() for buf in all_buffers()]

  def ask_for_file_path(self, on_get_path):
    self.run_command(BuiltinCommands.OPEN, None, False,
                     {'directory_content_file_path_selected': on_get_path})

  def get_document_content(self, document):
    return self.ui_helper.get_document_content(document)

  def save_current_buffer_as(self):
    self.current_buffer_.save_file_as()

  def save_current_buffer(self):
    self.current_buffer_.save_file()

  @staticmethod
  def open_url(url, timeout=30, extra_headers={}, disable_ssl_check=False):
    return eim_open_url(url, timeout, extra_headers, disable_ssl_check)

  def __load_color_theme(self):
    color_theme_name = self.config.get('/app/color-theme', 'zenburn')

    # try site config
    theme_paths = [
        pathlib.Path(self.appdirs_.user_config_dir),
        pathlib.Path(self.appdirs_.site_config_dir),
        pathlib.Path(os.path.dirname(__file__)) / '..',
        pathlib.Path(os.path.dirname(__file__)) / '..' / '..',
        pathlib.Path(os.path.dirname(__file__)) / '..' / '..' / '..',
    ]

    for dir in theme_paths:
      theme_path = dir / 'themes' / color_theme_name

      if theme_path.is_dir():
        logging.info(f'load color theme from {theme_path.resolve()}')
        self.color_theme_ = ColorTheme(theme_path)
        return

    logging.warn(f'color theme with name:{color_theme_name} is not found')
    self.color_theme_ = None

  def get_theme_def(self, theme_key):
    return self.color_theme_.get_theme_def(theme_key)

  def get_color(self, theme_def, color_key):
    c = self.color_theme_.get_color_def(theme_def[color_key])

    return self.ui_helper.get_color(
        theme_def[color_key]) if c is None else self.ui_helper.get_color(c)

  def get_theme_def_color(self, theme_key, color_key, default_color=None):
    theme_def = self.color_theme_.get_theme_def(theme_key)

    if theme_def is None:
      if default_color is None:
        return self.get_theme_def_color('default', color_key)
      return default_color

    return self.get_color(theme_def, color_key)

  def __load_langs_mapping(self):
    LANGS_MAP_URL = r'https://raw.githubusercontent.com/jonschlinkert/lang-map/master/lib/lang.json'
    SEVEN_DAYS_SECONDS = (3600 * 24 * 7)

    langs_file = pathlib.Path(self.appdirs_.user_config_dir) / 'lang.json'
    try:
      download_file = True

      if langs_file.exists():
        mtime = langs_file.stat().st_mtime + SEVEN_DAYS_SECONDS

        if (mtime > datetime.datetime.now().timestamp()):
          logging.info('langs mapping next update check will be on:{}'.format(
              datetime.datetime.fromtimestamp(mtime)))
          download_file = False

      if download_file:
        logging.info(
            'langs mapping downloading from url:{}'.format(LANGS_MAP_URL))

        with self.open_url(LANGS_MAP_URL) as langs_resp:
          langs_file.write_bytes(langs_resp.read())

        logging.info('langs mapping downloaded to:{}'.format(
            langs_file.resolve()))
    except:
      logging.exception('unable to load langs mapping')
    finally:
      if langs_file.exists():
        self.langs_mapping_ = json.loads(langs_file.read_text('utf-8'))
      else:
        self.langs_mapping_ = {}

  def register_editor_viewport_handler(self, handler):
    self.editor_view_port_handlers_.append(handler)

  def get_margins_for_handler(self, handler):
    vms = None

    for h in self.editor_view_port_handlers_:
      if h == handler:
        break

      vms = h.get_editor_margin() if vms is None \
        else vms + h.get_editor_margin()

    return vms

  def close_current_buffer(self):
    if self.prompt_for_buffer_save(self.close_current_buffer):
      logging.debug('close current buffer handled by prompt_for_buffer_save')
      return

    try:
      all_buffers().remove(self.current_buffer_)
    except:
      pass

    if len(all_buffers()) > 0:
      self.__set_current_buffer(all_buffers()[0])
    else:
      self.switch_to_buffer('Untitiled')

  def set_tab_width(self, tab_width):
    self.ui_helper.set_tab_width(tab_width)

  def get_row_and_col(self):
    return self.ui_helper.get_row_and_col()

  def prompt_for_buffer_save(self, action):
    if not self.current_buffer_.is_modified():
      return False

    cw = self.create_input_content_window()

    t = cw.text_edit_
    l = cw.label_widget_

    l.setText(
        f'Buffer {self.current_buffer_.name()} modified, save? (Yes or No)')

    t.returnPressed.connect(
        lambda: self.__do_prompt_for_buffer_save(cw, action))

    cw.show()

    return True

  def __do_prompt_for_buffer_save(self, cw, action):
    t = cw.text_edit_
    txt = t.text()

    if len(txt) == 0:
      self.close_content_window()
      return

    if txt.lower() != 'yes':
      self.close_content_window()

      self.current_buffer_.set_modified(False)

      if callable(action):
        action()
      return

    self.close_content_window()
    self.current_buffer_.save_file(action=action)

  def confirm_overwrite_file(self, file_path, action=None):
    cw = self.create_input_content_window()

    t = cw.text_edit_
    l = cw.label_widget_

    l.setText(
        f'File {file_path.resolve().as_posix()} exists, overwrite? (Yes or No)'
    )

    t.returnPressed.connect(lambda: self.__do_confirm_overwrite(cw, action))

    cw.show()

  def __do_confirm_overwrite(self, cw, action):
    t = cw.text_edit_
    txt = t.text()

    if txt.lower() == 'yes':
      if callable(action):
        action()

    self.close_content_window()

  def update_document_content(self, document, content):
    self.ui_helper.update_document_content(document, content)

  def process_cmd_line_client_args(self):
    if not (self.args.client is False):
      if not self.__call_server():
        raise ValueError()

      return True

    return False

  def process_cmd_line_args(self,
                            cur_dir=pathlib.Path('.'),
                            args=None,
                            process_client_server_arg=True):
    try:
      return self.__process_cmd_line_args(cur_dir, args,
                                          process_client_server_arg)
    except:
      logging.exception('process cmd line argument failed')

  def __process_cmd_line_args(self, cur_dir, args, process_client_server_arg):
    if isinstance(cur_dir, str):
      cur_dir = pathlib.Path(cur_dir)

    if args is None:
      args = self.args.args

    if process_client_server_arg and not (self.args.client is False):
      if not self.__call_server():
        raise ValueError()

      return False

    if args is not None and len(args) > 0:
      for arg in args:
        self.__handle_cmd_line_argument(arg, cur_dir)
    else:
      self.switch_to_buffer('Untitled')

    if process_client_server_arg and not (self.args.server is False):
      self.__start_server()

    return self.args.client is False

  def __handle_cmd_line_argument(self, arg, cur_dir):
    if len(arg) == 0:
      return

    if arg[0] == '+':
      try:
        self.run_command(BuiltinCommands.GOTO_LINE, None, False, int(arg[1:]))
      except:
        logging.exception(f'invalid command line argument:{arg}')
    else:
      p = pathlib.Path(arg)

      if p.is_absolute():
        self.load_buffer(p)
      else:
        self.load_buffer(cur_dir / arg)

  def __call_server(self):
    client = EditorClient(self)

    return client.call_server()

  def __start_server(self):
    self.editor_server_ = EditorServer(self)
    self.editor_server_.start()

  def quit_editing(self):
    if self.editor_server_ is not None:
      self.editor_server_.shutdown()

  def run_in_ui_thread(self, obj):
    self.ui_helper.run_in_ui_thread(obj)

  def __load_project_root_files(self):
    PROJECT_ROOT_FILES_URL = \
      r'https://raw.githubusercontent.com/stonewell/eim/from_scratch_pyside6/src/eim/core/project_root.json'
    SEVEN_DAYS_SECONDS = (3600 * 24 * 7)

    project_root_file = pathlib.Path(
        self.appdirs_.user_config_dir) / 'project_root.json'
    try:
      download_file = True

      if project_root_file.exists():
        mtime = project_root_file.stat().st_mtime + SEVEN_DAYS_SECONDS

        if (mtime > datetime.datetime.now().timestamp()):
          logging.info(
              'project root files next update check will be on:{}'.format(
                  datetime.datetime.fromtimestamp(mtime)))
          download_file = False

      if download_file:
        logging.info(
            f'project root files downloading from url:{PROJECT_ROOT_FILES_URL}'
        )

        with self.open_url(PROJECT_ROOT_FILES_URL) as _resp:
          project_root_file.write_bytes(_resp.read())

        logging.info(
            f'project root file downloaded to:{project_root_file.resolve()}')

    except:
      logging.exception('unable to load project root file')
    finally:
      if project_root_file.exists():
        self.project_root_files_ = json.loads(
            project_root_file.read_text('utf-8'))
      else:
        self.project_root_files_ = []

  def find_project_root(self, p, project_files=[]):
    _files = set(self.project_root_files_)
    _files.update(project_files)

    return eim_find_project_root(p, _files)

  def get_current_buffer_project_root(self):
    return self.find_project_root(
        self.get_current_buffer_dir()) or pathlib.Path('.').cwd()

  def has_content_window_active(self):
    return (self.content_window_ is not None
            and self.content_window_.has_focus())

  def get_buffers(self):
    for buf in all_buffers():
      yield buf

    return None
