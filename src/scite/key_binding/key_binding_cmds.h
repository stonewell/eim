#pragma once

#include <string>
#include <functional>

#include "Extender.h"

enum KeyBindingCmdResultEnum {
    NotFound,
    MsgCommand,
    MenuCommand
};

using key_binding_func = std::function<void (ExtensionAPI *)>;

KeyBindingCmdResultEnum key_binding_cmd_to_id(const std::string & cmd, uint32_t & msg);
bool key_binding_cmd_to_func(const std::string & cmd, key_binding_func & func);
bool assign_key_binding_cmd_func(const std::string & cmd, key_binding_func func);
