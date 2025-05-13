#pragma once

#include <memory>
#include <string>
#include <filesystem>

#include "toml++/toml.hpp"

std::filesystem::path get_default_config_path();

class PluginManager;

class Context : public std::enable_shared_from_this<Context>
{
public:
    using Ptr = std::shared_ptr<Context>;

    static Ptr create();

public:
    Context() = default;
    virtual ~Context() = default;

public:
    int load_config(const std::filesystem::path & config_file);
    int load_default_config();
    int initialize();

    const toml::table & get_config() const { return config_; }

protected:
    int create_default_config(const std::filesystem::path & config_file);
    int init_logging();
    int init_plugin_manager();

    toml::table config_{};
    std::shared_ptr<PluginManager> plugin_manager_{};
};
