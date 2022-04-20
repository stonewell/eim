import os
import sys
import logging
import pathlib
import tarfile
import platform
import datetime

from yapsy.IPlugin import IPlugin

TREE_SITTER_LANGS_LATEST_URL = r'https://github.com/emacs-tree-sitter/tree-sitter-langs/releases/latest'
TREE_SITTER_LANGS_LATEST_TAG_PREFIX = r'https://github.com/emacs-tree-sitter/tree-sitter-langs/releases/tag/'
TREE_SITTER_LANGS_FILE_NAME = r'tree-sitter-grammars{platform}{latest_tag}.tar.gz'
TREE_SITTER_LANGS_URL = r'https://github.com/emacs-tree-sitter/tree-sitter-langs/releases/download/{latest_tag}/{langs_file_name}'
TREE_SITTER_GRAMMAS_GIT_URL = r'https://github.com/emacs-tree-sitter/tree-sitter-langs.git'
SEVEN_DAYS_SECONDS = (3600 * 24 * 7)

class Plugin(IPlugin):

  def __init__(self):
    IPlugin.__init__(self)

  def activate(self):
    IPlugin.activate(self)

    self.ensure_tree_sitter_langs()

  def deactivate(self):
    IPlugin.deactivate(self)

  def set_current_window(self, editor):
    self.editor_ = editor

  def ensure_tree_sitter_langs(self):
    try:
      langs_dir = pathlib.Path(
          self.ctx.appdirs_.user_config_dir) / 'tree_sitter_langs'
      langs_dir.mkdir(parents=True, exist_ok=True)

      ver_file = langs_dir / 'vers.txt'

      if ver_file.exists():
        mtime = ver_file.stat().st_mtime + SEVEN_DAYS_SECONDS

        if (mtime > datetime.datetime.now().timestamp()):
          logging.info('tree sitter next update check will be on:{}'.format(datetime.datetime.fromtimestamp(mtime)))
          return

      with self.ctx.open_url(TREE_SITTER_LANGS_LATEST_URL) as response:
        latest_tag_url = response.geturl()

        if latest_tag_url.find(TREE_SITTER_LANGS_LATEST_TAG_PREFIX) != 0:
          raise ValueError('tree sitter invalid latest tag url:{}'.format(latest_tag_url))

        latest_tag = latest_tag_url[len(TREE_SITTER_LANGS_LATEST_TAG_PREFIX):]

        if ver_file.exists():
          content = f.read_text()

          if content == latest_tag:
            logging.info(
                'tree sitter langs version {} is the latest'.format(content))

            self.update_grammas(langs_dir / 'data')
            return

          logging.info(
              'tree sitter download latest version:{}, upgrade from version:{}'
              .format(latest_tag, content))
        else:
          logging.info(
              'tree sitter download latest version:{}'.format(latest_tag))

        platform = self.get_platform()
        langs_file_name = TREE_SITTER_LANGS_FILE_NAME.format(
            platform=platform, latest_tag=latest_tag)
        langs_url = TREE_SITTER_LANGS_URL.format(
            latest_tag=latest_tag, langs_file_name=langs_file_name)

        langs_file_path = langs_dir / langs_file_name

        logging.info('tree sitter downloading from url:{}'.format(langs_url))

        with self.ctx.open_url(langs_url) as langs_resp:
          langs_file_path.write_bytes(langs_resp.read())

        logging.info('tree sitter langs downloaded to:{}'.format(
            langs_file_path.resolve()))

        langs_data_path = langs_dir / 'data'
        langs_data_bin_path = langs_data_path / 'bin'
        langs_data_bin_path.mkdir(parents=True, exist_ok=True)

        tarfile.open(langs_file_path).extractall(langs_data_bin_path)

        logging.info('tree sitter langs binary extracted to:{}'.format(
            langs_data_bin_path.resolve()))

        self.clone_grammas(langs_data_path)

        ver_file.write_text(latest_tag)
    except:
      logging.exception('failed ensure tree sitter langs')

  @staticmethod
  def get_platform():
    is_64bits = sys.maxsize > 2**32

    if platform.system() == 'Linux':
      return '.x86_64-unknown-linux-gnu.v' if is_64bits else '-linux-'
    if platform.system() == 'Windows':
      return '.x86_64-pc-windows-msvc.v' if is_64bits else '-windows-'
    if platform.system() == 'Darwin':
      arch, _ = platform.architecture()

      if arch.lower() == 'aarch64':
        return '.aarch64-apple-darwin.v'
      return '.x86_64-apple-darwin.v' if is_64bits else '-macos-'

    raise ValueError('unspported platform:{}'.format(platform.system()))

  @staticmethod
  def clone_grammas(langs_data_path):
    from git import Repo
    try:
      repo = Repo.init(langs_data_path)
      origin = repo.create_remote('origin', TREE_SITTER_GRAMMAS_GIT_URL)
      origin.fetch()
      repo.create_head('master', origin.refs.master)
      repo.heads.master.set_tracking_branch(origin.refs.master)
      repo.heads.master.checkout()
      origin.pull()

      logging.info('tree sitter grammer clone from:{}, to:{}'.format(
          TREE_SITTER_GRAMMAS_GIT_URL, langs_data_path.resolve()))
    except:
      logging.exception('tree sitter grammer clone repo failed')

  @staticmethod
  def update_grammas(langs_data_dir):
    from git import Repo

    try:
      repo = Repo(langs_data_dir)
      repo.remotes.origin.pull()
      logging.info('tree sitter grammars pulled latest version')
    except:
      Plugin.clone_grammas(langs_data_dir)
