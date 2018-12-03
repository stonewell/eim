#pragma once

#include <memory>
#include <string>
#include <deque>

namespace eim
{
class Command {
public:
    Command() = default;
    virtual ~Command() = default;

public:
    virtual void Execute() = 0;
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
