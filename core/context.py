import os
import sys
import argparse
import logging
import pathlib

from appdirs import AppDirs
from .app_config import default_config, load_config
from yapsy.PluginManager import PluginManager

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

        self.validate_args(args)

        self.__load_config()

        self.__load_plugins()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--debug", help="print debug information", action="count", default=0)
        parser.add_argument("-v", "--version", action="version", version='%(prog)s 1.0')
        parser.add_argument("-c", "--config", type=pathlib.Path, help='config file path', required=False,
                            metavar='<config file path>')
        parser.add_argument('-p', "--plugins", help="directory to load plugins", required=False,
                            type=pathlib.Path, metavar='<plugins directory>')

        return parser.parse_args()

    @staticmethod
    def validate_args(args):
        pass

    def __load_config_file(self, config):
        if config and config.is_file():
            logging.debug('load {} and merge'.format(config))
            self.config.update(load_config(config))
        else:
            logging.debug('config file:{} is not exists'.format(config.resolve() if config else 'None'))

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
            logging.debug('plugin directory:{} is not exists'.format(plugin_dir.resolve() if plugin_dir else 'None'))
            return

        pm = PluginManager()
        pm.setPluginPlaces([plugin_dir])

        # Load all plugins
        pm.collectPlugins()

        for pluginInfo in pm.getAllPlugins():
            self.plugins_[pluginInfo.name] = pluginInfo

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
        pass
