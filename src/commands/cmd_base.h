#pragma once

#include "command.h"

namespace eim
{
class CommandBase : public virtual Command {
public:
    CommandBase(const std::string & name)
        : m_Name(name) {
    }

    virtual ~CommandBase() = default;

public:
    virtual const std::string & GetName() {
        return m_Name;
    }

protected:
    std::string m_Name;
};
} //namespace eim
