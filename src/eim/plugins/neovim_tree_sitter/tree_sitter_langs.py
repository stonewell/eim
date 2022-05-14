import os
import sys
import logging
import pathlib
import tarfile
import platform
import datetime

TREE_SITTER_GRAMMAS_GIT_URL = r'https://github.com/nvim-treesitter/nvim-treesitter.git'
SEVEN_DAYS_SECONDS = (3600 * 24 * 7)


def ensure_tree_sitter_langs(ctx):
  try:
    langs_dir = pathlib.Path(
        ctx.appdirs_.user_config_dir) / 'neovim_tree_sitter'
    langs_dir.mkdir(parents=True, exist_ok=True)

    ver_file = langs_dir / 'timestamp.txt'

    if ver_file.exists():
      mtime = ver_file.stat().st_mtime + SEVEN_DAYS_SECONDS

      if (mtime > datetime.datetime.now().timestamp()):
        logging.info('tree sitter next update check will be on:{}'.format(
            datetime.datetime.fromtimestamp(mtime)))
        return

    langs_data_dir = langs_dir / 'data'

    if (langs_data_dir / '.git').is_dir():
      update_grammas(langs_data_dir)
    else:
      langs_data_dir.mkdir(parents=True, exist_ok=True)
      clone_grammas(langs_data_dir)

    ver_file.write_text(f'{datetime.datetime.now().timestamp()}')
  except:
    logging.exception('failed ensure neovim tree sitter langs')


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

    logging.info('neovim tree sitter grammer clone from:{}, to:{}'.format(
        TREE_SITTER_GRAMMAS_GIT_URL, langs_data_path.resolve()))
  except:
    logging.exception('neovim tree sitter grammer clone repo failed')


def update_grammas(langs_data_dir):
  from git import Repo

  try:
    repo = Repo(langs_data_dir)
    repo.remotes.origin.pull()
    logging.info('neovim tree sitter grammars pulled latest version')
  except:
    clone_grammas(langs_data_dir)
