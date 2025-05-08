#include <filesystem>
#include <fstream>
#include <iostream>

#include "context.h"
#include "platform_folders.h"
#include "spdlog/spdlog.h"
#include "toml++/toml.hpp"

namespace fs = std::filesystem;

namespace
{
constexpr char DEFAULT_CONFIG[] = R"(
    loading_path = []

    [logging]
    level="Debug"

    [plugins]

    [plugins.buffer]
    name="buffer"
    path="/opt/eim/plugins/libbuffer.so"

    [plugins.buffer.config]
    use_mmap = true

    [plugins.ui]
    name="ui"

    [plugins.ui.config]
    use_opengl = true
)";
}

fs::path get_default_config_path()
{
    fs::path default_config{sago::getConfigHome()};

    return default_config / "eim" / "eim.toml";
}

Context::Ptr Context::Create()
{
    return std::make_shared<Context>();
}

int Context::load_default_config()
{
    auto default_config = get_default_config_path();

    if (!fs::exists(default_config))
    {
        auto r = create_default_config(default_config);
        if (r)
        {
            return r;
        }
    }

    return load_config(default_config);
}

int Context::load_config(const fs::path & config_file)
{
    try
    {
        const auto config = toml::parse_file(config_file.string());

        std::cout << toml::json_formatter(config) << std::endl;
    }
    catch (const toml::parse_error& err)
    {
        spdlog::error("unable to parse config file:{}, error:{}",
                      config_file.string(),
                      err.what());
        return 1;
    }
    return 0;
}

int Context::create_default_config(const std::filesystem::path & config_file)
{
    std::error_code ec{};

    fs::create_directories(config_file.parent_path(), ec);

    if (ec)
    {
        spdlog::error("unable to create default config file parent path:{}, error:{}",
                      config_file.parent_path().string(),
                      ec.message());
        return 1;
    }

    std::ofstream ofs(config_file);

    if (!ofs.is_open())
    {
        spdlog::error("unable to write default config file:{}",
                      config_file.string());

        return 2;
    }

    ofs << DEFAULT_CONFIG;

    return 0;
}
