#pragma once

#include <memory>
#include <deque>
#include <vector>

namespace eim {
class EIMContext;
using EIMContextPtr = std::shared_ptr<EIMContext>;
class Command;
using CommandPtr = std::shared_ptr<Command>;
using CommandStack = std::deque<CommandPtr>;
using StringVector = std::vector<std::string>;
};
