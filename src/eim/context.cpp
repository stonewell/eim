#include <filesystem>

#include "context.h"
#include "platform_folders.h"

namespace fs = std::filesystem;

fs::path get_default_config_path()
{
    fs::path default_config{sago::getConfigHome()};
    default_config /= "eim";
    default_config /= "eim.toml";

    return default_config;
}

Context::Ptr Context::Create()
{
    return std::make_shared<Context>();
}

int Context::load_default_config()
{
    return load_config(get_default_config_path());
}

int Context::load_config(const fs::path & config_file)
{
    (void)config_file;
    return 0;
}
