from .eim import EIM


def main():
  eim = EIM()

  eim.process_cmd_line_and_run()


if __name__ == "__main__":
  main()
