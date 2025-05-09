#include "context.h"
#include "command_line_options.h"
#include "spdlog/spdlog.h"
#include "helper_macros.h"

int main(int argc, char **argv) {
    Context::Ptr spContext = Context::Create();

    RETURN_ON_ERROR(process_command_line(argc, argv, spContext));

    RETURN_ON_ERROR(spContext->initialize());
    spdlog::info("eim started");

    return 0;
}
