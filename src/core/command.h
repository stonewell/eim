#pragma once

#include "eim_core.h"
#include <string>
#include <deque>

namespace eim
{
class Command {
public:
    Command() = default;
    virtual ~Command() = default;

public:
    virtual std::string Execute(EIMContextPtr context, const std::string & json_args) = 0;
    virtual const std::string & GetName() = 0;
};

class UndoableCommand : public virtual Command {
public:
    UndoableCommand() = default;
    virtual ~UndoableCommand() = default;

public:
    virtual void Undo() = 0;
};

using CommandPtr = std::shared_ptr<Command>;
using CommandStack = std::deque<CommandPtr>;
}; //namespace eim
