#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <time.h>
#include <errno.h>

#include <string>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <iostream>

#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>

#include "ILexer.h"
#include "Scintilla.h"

#include "GUI.h"
#include "ScintillaWindow.h"
#include "StringList.h"
#include "StringHelpers.h"
#include "FilePath.h"
#include "StyleDefinition.h"
#include "PropSetFile.h"
#include "Extender.h"
#include "SciTE.h"
#include "Mutex.h"
#include "JobQueue.h"
#include "Cookie.h"
#include "Worker.h"
#include "MatchMarker.h"
#include "SciTEBase.h"
#include "KeyMap.h"

#include "keybinding_extension.h"
#include "key_binding_cmds.h"
#include "tao/json.hpp"

static
bool Exists(const GUI::gui_char *dir, const GUI::gui_char *path, FilePath *resultPath) {
	FilePath copy(path);
	if (!copy.IsAbsolute() && dir) {
		copy.SetDirectory(dir);
	}
	if (!copy.Exists())
		return false;
	if (resultPath) {
		resultPath->Set(copy.AbsolutePath());
	}
	return true;
}

KeyBindingExtension &KeyBindingExtension::Instance() {
	static KeyBindingExtension singleton;
	return singleton;
}

bool KeyBindingExtension::Initialise(ExtensionAPI *host_) {
	m_Host = host_;

    m_BindingConfig = m_Host->Property("ext.keybinding.config");

    InitCommandFunc();

	return LoadBindingConfig(m_BindingConfig);
}

bool KeyBindingExtension::Finalise() {
    return false;
}

bool KeyBindingExtension::Clear() {
    return false;
}

bool KeyBindingExtension::Load(const char *filename) {
    (void)filename;
    return false;
}

bool KeyBindingExtension::OnKey(int keyval, int modifier) {
    (void)keyval;
    (void)modifier;

    key_binding_u kb = from(keyval, modifier);

    auto km = &m_KeyMap;

    if (m_CurKeyMap) {
        km = &m_CurKeyMap->sub_key_map;
    }

    printf("OnKey:%c, m:%d, cur_key_map:%p, %zu", (char)(keyval&0xFF), modifier, km, km->size());
    std::cout <<", kb:" << kb.v << ", " << kb.key_data.keyval << ", " << (int)kb.key_data.keyval << ", " << (int)kb.key_data.modifier.m;

    auto it = km->find(kb.v);

    bool cmd = false;
    if (it != km->end()) {
        printf(", found keymap");
        cmd = true;

        if (it->second->command.length() > 0) {
            printf(", Command:%s", it->second->command.c_str());
            m_CurKeyMap = nullptr;

            key_binding_func func;

            if (key_binding_cmd_to_func(it->second->command, func)) {
                func(m_Host);
            } else {
                uint32_t msg = 0;
                KeyBindingCmdResultEnum result =
                        key_binding_cmd_to_id(it->second->command, msg);

                if (result == KeyBindingCmdResultEnum::MsgCommand) {
                    m_Host->Send(ExtensionAPI::Pane::paneEditor, msg, 0, 0);
                } else if (result == KeyBindingCmdResultEnum::MenuCommand) {
                    m_Host->DoMenuCommand(msg);
                } else {
                    printf(" is not found!!!");
                    //reset key binding tree
                    m_CurKeyMap = nullptr;
                }
            }
        } else {
            m_CurKeyMap = it->second;
        }
    } else {
        //if no mapping found, reset key map tree
        m_CurKeyMap = nullptr;
    }

    printf("\n");

    return cmd;
}

bool KeyBindingExtension::LoadBindingConfig(const std::string & config) {
    if (config.length() == 0)
        return false;

    FilePath defaultDir(m_Host->Property("SciteDefaultHome"));
    FilePath scriptPath;

    std::cout << "default home:" << defaultDir.AsUTF8() << std::endl;

    // find file in local directory
	if (Exists(defaultDir.AsInternal(), config.c_str(), &scriptPath)) {
    } else if (Exists(GUI_TEXT(""), config.c_str(), &scriptPath)) {
    } else {
        return false;
    }

    return LoadFile(scriptPath.AsUTF8());
}

bool KeyBindingExtension::LoadFile(const std::string & file_path) {
    try {
        const tao::json::value v = tao::json::parse_file(file_path);

        const auto & key_bindings = v.get_array();

        auto kmap = &m_KeyMap;
        key_map_ptr kp{};

        for(const auto & key_binding : key_bindings) {
            const auto & keys = key_binding.at("keys").get_array();
            const auto & command = key_binding.at("command").get_string();

            for(const auto & key : keys) {
                const auto & data = key.get_string();
                auto kb = from(data.c_str(), data.length());

                std::cout << key_binding
                          << ", key:" << key
                          << ", cmd:" << command
                          << ", kb:" << kb.v << ", " << kb.key_data.keyval << ", " << (int)kb.key_data.keyval << ", " << (int)kb.key_data.modifier.m
                          << std::endl;

                auto it = kmap->emplace(kb.v, std::make_shared<key_map_s>());

                kp = it.first->second;
                kmap = &kp->sub_key_map;
            }

            if (kp) {
                kp->command = command;
            }

            kmap = &m_KeyMap;
        }

    } catch(const std::exception & e) {
        std::cout << "load keybinding file:" << file_path << " failed!" << e.what() << std::endl;
    }
    return false;
}


void KeyBindingExtension::InitCommandFunc() {
    assign_key_binding_cmd_func("push_mark", [](ExtensionAPI * host) {
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_CANCEL, 0, 0);
                                                 auto pos = host->Send(ExtensionAPI::Pane::paneEditor, SCI_GETCURRENTPOS, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_SETEMPTYSELECTION, pos, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_SETSELECTIONMODE, SC_SEL_STREAM, 0);
                                             });
    assign_key_binding_cmd_func("exec_command", [](ExtensionAPI * host) {
                                                    host->UserStripShow("execute command:");
                                             });
    assign_key_binding_cmd_func("cancel", [](ExtensionAPI * host) {
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_CANCEL, 0, 0);
                                                 auto pos = host->Send(ExtensionAPI::Pane::paneEditor, SCI_GETCURRENTPOS, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_SETEMPTYSELECTION, pos, 0);
                                             });
    assign_key_binding_cmd_func("copy_sel", [](ExtensionAPI * host) {
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_COPY, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_CANCEL, 0, 0);
                                                 auto pos = host->Send(ExtensionAPI::Pane::paneEditor, SCI_GETCURRENTPOS, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_SETEMPTYSELECTION, pos, 0);
                                             });
   assign_key_binding_cmd_func("cut_sel", [](ExtensionAPI * host) {
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_CUT, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_CANCEL, 0, 0);
                                                 auto pos = host->Send(ExtensionAPI::Pane::paneEditor, SCI_GETCURRENTPOS, 0, 0);
                                                 host->Send(ExtensionAPI::Pane::paneEditor, SCI_SETEMPTYSELECTION, pos, 0);
                                             });
}
