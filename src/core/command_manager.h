#pragma once

#include "command.h"
#include <memory>

namespace eim {
class CommandManager {
public:
    CommandManager() = default;
    virtual ~CommandManager() = default;

public:
    virtual CommandPtr GetCommand(const std::string & name) = 0;
    virtual void GetCommandNames(StringVector & cmds) = 0;
};

using CommandManagerPtr = std::shared_ptr<CommandManager>;
bool RegisterCommand(CommandPtr cmd);
CommandManagerPtr CreateCommandManager();
}; //namespace eim
