#pragma once

#include <memory>
#include <string>
#include <filesystem>

std::filesystem::path get_default_config_path();

class Context
{
public:
    using Ptr = std::shared_ptr<Context>;

    static Ptr Create();

public:
    Context() = default;
    virtual ~Context() = default;

public:
    int load_config(const std::filesystem::path & config_file);
    int load_default_config();

protected:
    int create_default_config(const std::filesystem::path & config_file);
};
