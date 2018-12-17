#pragma once

#include "command.h"
#include <memory>

namespace eim {
class CommandManager {
};

using CommandManagerPtr = std::shared_ptr<CommandManager>;
void RegisterCommand(CommandPtr cmd);
}; //namespace eim
