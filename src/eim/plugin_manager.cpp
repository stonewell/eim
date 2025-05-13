#include "plugin_manager.h"
#include "context.h"

#include <iostream>

#include "spdlog/spdlog.h"
#include "helper_macros.h"

namespace fs = std::filesystem;
using namespace std::string_view_literals;


int PluginManager::initialize(Context::Ptr spContext)
{
    context_ = spContext;

    return init_plugins();
}

PluginManager::Ptr PluginManager::create()
{
    return std::make_shared<PluginManager>();
}

int PluginManager::init_plugins()
{
    const auto & config = context_->get_config();

    config["plugins"].as_table()->for_each([&](auto && key, auto && value) {
        auto r = load_plugin(key.str(), *value.as_table());

        if (r)
        {
            spdlog::error("unable load plugin:{}, ret:{}", key.str(), r);
            return false;
        }

        return true;
    });
    return 0;
}

int PluginManager::load_plugin(std::string_view name, const toml::table & plugin_info)
{
    auto plugin_path = plugin_info.at_path("path").value_or(""sv);

    if (plugin_path.empty())
    {
        plugin_path = find_plugin_path(name);
    }

    if (plugin_path.empty() || !fs::exists(plugin_path))
    {
        spdlog::error("unable to load plugin {}, invalid path: <{}>", name, plugin_path);
        return 1;
    }

    auto config = plugin_info.at_path("config");

    std::string json_config{"{}"};

    if (config)
    {
        json_config = to_string(toml::json_formatter(*config.node()));
    }

    std::cout << name << "," << json_config << std::endl;
    return 1;
}

std::string PluginManager::find_plugin_path(std::string_view name)
{
    (void)name;
    return std::string{name};
}
