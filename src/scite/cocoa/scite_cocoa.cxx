#include "scite_cocoa.h"

static
MultiplexExtension g_MultiExtender;

SciTECocoa::SciTECocoa() {
}

void SciTECocoa::Run(int argc, char * argv[]) {
#ifdef NO_EXTENSIONS
	m_Extender = 0;
#else
	m_Extender = &g_MultiExtender;

#ifndef NO_LUA
	g_MultiExtender.RegisterExtension(LuaExtension::Instance());
#endif
#endif

	// Load the default session file
	if (props.GetInt("save.session") || props.GetInt("save.position") || props.GetInt("save.recent")) {
		LoadSessionFile("");
	}

	// Find the SciTE executable, first trying to use argv[0] and converting
	// to an absolute path and if that fails, searching the path.
    FilePath sciteExecutable = FilePath(argv[0]).AbsolutePath();
	if (!sciteExecutable.Exists()) {
	}

	// Collect the argv into one string with each argument separated by '\n'
	GUI::gui_string args;
	for (int arg = 1; arg < argc; arg++) {
		if (arg > 1)
			args += '\n';
		args += argv[arg];
	}

	// Process any initial switches
	ProcessCommandLine(args, 0);

	// Check if SciTE is already running.
	if ((props.GetString("ipc.director.name").size() == 0) && props.GetInt ("check.if.already.open")) {
		// if (CheckForRunningInstance (argc, argv)) {
		// 	// Returning from this function exits the program.
		// 	return;
		// }
	}

	ProcessCommandLine(args, 1);

	CheckMenus();
	SizeSubWindows();
	// SetFocus(wEditor);
}