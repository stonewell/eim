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
	return true;
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
