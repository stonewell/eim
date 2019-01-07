#pragma once

#include <string>

enum KeyBindingCmdResultEnum {
    NotFound,
    MsgCommand,
    MenuCommand
};

KeyBindingCmdResultEnum key_binding_cmd_to_id(const std::string & cmd, uint32_t & msg);
