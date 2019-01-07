#include "key_binding_cmds.h"

#include <unordered_map>
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

using key_binding_cmd_map = std::unordered_map<std::string, uint32_t>;

static
key_binding_cmd_map g_default_cmd_msg_map {
    {"next_line", SCI_LINEDOWN},
    {"prev_line", SCI_LINEUP},
    {"prev_char", SCI_CHARLEFT},
    {"next_char", SCI_CHARRIGHT},
    {"kill_line_right", SCI_DELLINERIGHT},
    {"kill_line_left", SCI_DELLINELEFT},
    {"page_down", SCI_PAGEDOWN},
    {"page_up", SCI_PAGEUP},
    {"line_end", SCI_LINEEND},
    {"line_home", SCI_VCHOME},
    {"copy_sel", SCI_COPY},
    {"cut_sel", SCI_CUT},
    {"paste_text", SCI_PASTE},
    {"sel_all", SCI_SELECTALL},
    {"del_char_right", SCI_CLEAR},
    {"del_char_left", SCI_DELETEBACK},
    {"cancel", SCI_CANCEL},
    {"undo", SCI_UNDO},
};

static
key_binding_cmd_map g_default_cmd_menu_map {
    {"save_buffer", IDM_SAVE},
    {"kill_buffer", IDM_CLOSE},
    {"find_file", IDM_OPEN},
    {"revert_buffer", IDM_REVERT},
    {"quit", IDM_QUIT},
    {"goto_line", IDM_GOTO},
    {"find_next", IDM_INCSEARCH},
    {"find_prev", IDM_FINDNEXTBACK},
};


KeyBindingCmdResultEnum key_binding_cmd_to_id(const std::string & cmd, uint32_t & msg) {
    auto it = g_default_cmd_msg_map.find(cmd);

    if (it != g_default_cmd_msg_map.end()) {
        msg = it->second;
        return KeyBindingCmdResultEnum::MsgCommand;
    } else {
        it = g_default_cmd_menu_map.find(cmd);

        if (it != g_default_cmd_menu_map.end()) {
            msg = it->second;
            return KeyBindingCmdResultEnum::MenuCommand;
        }
    }

    msg = 0;

    return KeyBindingCmdResultEnum::NotFound;
}
