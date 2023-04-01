import logging
import pathlib
import tarfile
import platform
import datetime
import shutil

SEVEN_DAYS_SECONDS = 3600 * 24 * 7
NVIM_TREESITTER_PARSER_QUERIES_FILE = r'https://github.com/stonewell/eim/releases/download/latest/nvim-treesitter-query-parsers-{platform}-nightly.tar.gz'


def ensure_tree_sitter_langs(ctx):
  try:
    langs_dir = pathlib.Path(
        ctx.appdirs_.user_config_dir) / 'neovim_tree_sitter'
    langs_dir.mkdir(parents=True, exist_ok=True)

    ver_file = langs_dir / 'timestamp.txt'

    if ver_file.exists():
      mtime = ver_file.stat().st_mtime + SEVEN_DAYS_SECONDS

      if mtime > datetime.datetime.now().timestamp():
        logging.info('tree sitter next update check will be on:%s',
                     datetime.datetime.fromtimestamp(mtime))
        return

    langs_data_dir = langs_dir / 'data'
    if langs_data_dir.exists():
      shutil.rmtree(langs_data_dir)
    langs_data_dir.mkdir(parents=True, exist_ok=True)

    langs_data_url = NVIM_TREESITTER_PARSER_QUERIES_FILE.format(
        platform=get_platform())
    langs_data_file = langs_data_dir / 'data.tar.gz'

    logging.info('download neovim tree sitter data:%s', langs_data_url)
    with ctx.open_url(langs_data_url) as response:
      langs_data_file.write_bytes(response.read())

    tarfile.open(langs_data_file).extractall(langs_data_dir)

    ver_file.write_text(f'{datetime.datetime.now().timestamp()}')
  except:
    logging.exception('failed ensure neovim tree sitter langs')


def get_platform():
  if platform.system() == 'Linux':
    return 'ubuntu-latest'
  if platform.system() == 'Windows':
    return 'windows-2022'
  if platform.system() == 'Darwin':
    return 'macos-latest'

  raise ValueError(f'unspported platform:{platform.system()}')


def get_lang_names(ctx):
  langs_bin_dir = pathlib.Path(
      ctx.appdirs_.user_config_dir) / 'neovim_tree_sitter' / 'data' / 'parser'

  if not langs_bin_dir.exists():
    return []

  lang_names = []
  for lang in langs_bin_dir.iterdir():
    if lang.is_file() and lang.suffix.lower() == '.so':
      lang_names.append(lang.stem)

  return lang_names
