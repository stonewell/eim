#pragma once

#include <memory>
#include <deque>

namespace eim {
class EIMContext;
using EIMContextPtr = std::shared_ptr<EIMContext>;
class Command;
using CommandPtr = std::shared_ptr<Command>;
using CommandStack = std::deque<CommandPtr>;
};
