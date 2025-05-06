#include "command_line_options.h"

#include "CLI/CLI.hpp"

int process_command_line(int argc, char ** argv)
{
  CLI::App app{"EIM(Editor Improved) description"};
  argv = app.ensure_utf8(argv);

  std::string filename = "default";
  app.add_option("-f,--file", filename, "A help string");

  try
  {
    app.parse(argc, argv);
  } catch (const CLI::Success &e) {
    (void)app.exit(e);
    return 1;
  } catch (const CLI::ParseError &e) {
    return app.exit(e);
  }

  return 0;
}
