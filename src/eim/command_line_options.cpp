#include <format>
#include <filesystem>

#include "command_line_options.h"

#include "CLI/CLI.hpp"
#include "platform_folders.h"

namespace fs = std::filesystem;

int process_command_line(int argc, char ** argv, Context::Ptr spContext)
{
    CLI::App app{"EIM(Editor Improved) description"};
    argv = app.ensure_utf8(argv);

    fs::path default_config = get_default_config_path();

    std::string filename{""};
    app.add_option("-c,--config_file",
                   filename,
                   std::format("A alternative config file to use, default path:{}", default_config.string()))
        ->check(CLI::ExistingFile);

    try
    {
        app.parse(argc, argv);
    } catch (const CLI::Success &e) {
        (void)app.exit(e);
        return 1;
    } catch (const CLI::ParseError &e) {
        return app.exit(e);
    }

    if (filename.empty())
    {
        return spContext->load_default_config();
    }
    else
    {
        return spContext->load_config(filename);
    }
}
