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

#include <gtk/gtk.h>

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
#include "keybinding_extension.h"


KeyBindingExtension &KeyBindingExtension::Instance() {
	static KeyBindingExtension singleton;
	return singleton;
}

bool KeyBindingExtension::Initialise(ExtensionAPI *host_) {
	m_Host = host_;

    m_BindingConfig = m_Host->Property("ext.keybinding.config");

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

    printf("OnKey:%c, m:%d\n", (char)(keyval&0xFF), modifier);
    return false;
}

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
    (void)file_path;
    std::cout << "load keybinding file:" << file_path << std::endl;
    return false;
}
