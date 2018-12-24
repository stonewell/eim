#pragma once

#include "ScintillaView.h"

extern "C"
Scintilla::ScintillaBase * get_backend(ScintillaView * view);
