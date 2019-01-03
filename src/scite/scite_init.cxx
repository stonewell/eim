#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdarg.h>
#include <time.h>
#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <signal.h>

#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <memory>

#include "ILexer.h"
#include "Scintilla.h"

#include "GUI.h"
#include "ScintillaWindow.h"
#include "StringList.h"
#include "StringHelpers.h"
#include "FilePath.h"
#include "StyleDefinition.h"
#include "PropSetFile.h"

#include "MultiplexExtension.h"

#include "SciTE.h"
#include "Mutex.h"
#include "JobQueue.h"
#include "Cookie.h"
#include "Worker.h"
#include "MatchMarker.h"
#include "SciTEBase.h"

#include "keybinding_extension.h"

extern "C"
bool InitializeScite(MultiplexExtension * extender,
                     SciTEBase * scite) {
    (void)extender;
    (void)scite;

    extender->RegisterExtension(KeyBindingExtension::Instance());

    return true;
}
