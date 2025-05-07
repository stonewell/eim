#include <iostream>
#include <string>
#include <sstream>

#include "platform_folders.h"
#include "spdlog/spdlog.h"
#include "toml++/toml.hpp"

#include "context.h"
#include "command_line_options.h"

template <typename T> std::string to_string(T v) {
    std::stringstream ss;
    ss << v;

    return ss.str();
}

int main(int argc, char **argv) {
    Context::Ptr spContext = Context::Create();

    auto r = process_command_line(argc, argv, spContext);
    if (r)
    {
        return r;
    }

    return 0;
}
