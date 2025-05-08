#include "context.h"
#include "command_line_options.h"
#include "spdlog/spdlog.h"

int main(int argc, char **argv) {
    Context::Ptr spContext = Context::Create();

    auto r = process_command_line(argc, argv, spContext);
    if (r)
    {
        return r;
    }

    spdlog::info("eim started");
    return 0;
}
