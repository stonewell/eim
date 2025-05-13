#pragma once

#include <memory>
#include <string>

#include "toml++/toml.hpp"

class Context;

class PluginManager
{
public:
    using Ptr = std::shared_ptr<PluginManager>;

    static Ptr create();

public:
    PluginManager() = default;
    virtual ~PluginManager() = default;

    int initialize(std::shared_ptr<Context> spContext);

protected:
    int init_plugins();
    int load_plugin(std::string_view name, const toml::table & plugin_info);
    std::string find_plugin_path(std::string_view name);

    std::shared_ptr<Context> context_{};
};
