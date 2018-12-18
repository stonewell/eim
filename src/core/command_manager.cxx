#include "command_manager.h"
#include <unordered_map>
#include <iostream>

namespace eim {
namespace impl {

using CommandMap = std::unordered_map<std::string, CommandPtr>;

static
std::shared_ptr<CommandMap> g_CommandMap{nullptr};
}; //namespace impl

bool RegisterCommand(CommandPtr cmd) {
    std::cout << "register command: " << cmd->GetName() << std::endl;

    if (!impl::g_CommandMap)
        impl::g_CommandMap = std::make_shared<impl::CommandMap>();

    return impl::g_CommandMap->insert(std::make_pair(cmd->GetName(), cmd)).second;
}

}; //namespace eim
