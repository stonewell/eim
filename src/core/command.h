#pragma once

#include "eim_core.h"
#include <string>

namespace eim
{
class Command {
public:
    Command() = default;
    virtual ~Command() = default;

public:
    virtual std::string Execute(EIMContextPtr context, const std::string & json_args) = 0;
    virtual const std::string & GetName() = 0;
    virtual CommandPtr NewInstance() = 0;
};

class UndoableCommand : public virtual Command {
public:
    UndoableCommand() = default;
    virtual ~UndoableCommand() = default;

public:
    virtual void Undo() = 0;
};

}; //namespace eim
