import os

os.environ['QT_QPA_PLATFORMTHEME'] = 'eim'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(
    os.path.dirname(__file__), 'plugins', 'qpa')

from .eim import EIM


def main():
  eim = EIM()

  eim.process_cmd_line_and_run()


if __name__ == "__main__":
  main()
