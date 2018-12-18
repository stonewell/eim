#pragma once

#include "command.h"
#include "command_manager.h"

namespace eim
{
template<class T>
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

    virtual CommandPtr NewInstance() {
        return std::make_shared<T>();
    }

protected:
    std::string m_Name;
};

} //namespace eim
