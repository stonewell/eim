#include "command_manager.h"
#include <unordered_map>
#include <iostream>

namespace eim {
namespace impl {

using CommandMap = std::unordered_map<std::string, CommandPtr>;

static
std::shared_ptr<CommandMap> g_CommandMap{nullptr};

class CommandManagerImpl : public virtual CommandManager {
public:
    using CommandManager::CommandManager;
    virtual ~CommandManagerImpl() = default;

public:
    virtual CommandPtr GetCommand(const std::string & name);
    virtual void GetCommandNames(StringVector & cmds);
};

CommandPtr CommandManagerImpl::GetCommand(const std::string & name) {
    if (!g_CommandMap) {
        std::cout << "cmd:" << name << " is not found" << std::endl;
        return CommandPtr{};
    }

    auto it = g_CommandMap->find(name);

    if (it == g_CommandMap->end()) {
        std::cout << "cmd:" << name << " is not found" << std::endl;
        return CommandPtr{};
    }

    std::cout << "cmd:" << name << " found" << std::endl;
    return it->second->NewInstance();
}

void CommandManagerImpl::GetCommandNames(StringVector & cmds) {
    cmds.clear();

    if (!g_CommandMap) return;

    for(auto it = g_CommandMap->begin(),
                it_end = g_CommandMap->end();
        it != it_end;
        it++) {
        cmds.push_back(it->first);
    }
}
}; //namespace impl

bool RegisterCommand(CommandPtr cmd) {
    std::cout << "register command: " << cmd->GetName() << std::endl;

    if (!impl::g_CommandMap)
        impl::g_CommandMap = std::make_shared<impl::CommandMap>();

    return impl::g_CommandMap->insert(std::make_pair(cmd->GetName(), cmd)).second;
}

CommandManagerPtr CreateCommandManager() {
    return std::make_shared<impl::CommandManagerImpl>();
}

}; //namespace eim
