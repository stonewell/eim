#pragma once

namespace eim {

template<class T>
class CommandRegister {
public:
    CommandRegister() {
        RegisterCommand(m_Command.NewInstance());
    }

    T m_Command;
};

#define REG_CMD(T) \
    static eim::CommandRegister<T> __reg_cmd_##T;

}; //namespace eim
