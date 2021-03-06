#include "scite_cocoa.h"
#include <dlfcn.h>

static
MultiplexExtension g_MultiExtender;
typedef bool (*func_InitializeScite)(MultiplexExtension * extender,
                     SciTEBase * scite);

SciTECocoa::SciTECocoa() {
}

void SciTECocoa::Run(const char * exe_path, Scintilla::ScintillaBase* pEditor, Scintilla::ScintillaBase* pOutput, int argc, char * argv[]) {
    mEditor = pEditor;
    mOutput = pOutput;

#ifdef NO_EXTENSIONS
	this->extender = 0;
#else
	this->extender = &g_MultiExtender;

#ifndef NO_LUA
	g_MultiExtender.RegisterExtension(LuaExtension::Instance());
#endif
#endif

    func_InitializeScite pfn = (func_InitializeScite)dlsym(RTLD_DEFAULT, "InitializeScite");

    if (pfn) {
        if (!pfn(&g_MultiExtender, this)) {
            exit(4);
        }
    }

	CreateBuffers();

    wEditor.SetScintilla(pEditor);
    wOutput.SetScintilla(pOutput);

	// Load the default session file
	if (props.GetInt("save.session") || props.GetInt("save.position") || props.GetInt("save.recent")) {
		LoadSessionFile("");
	}

	// Find the SciTE executable, first trying to use argv[0] and converting
	// to an absolute path and if that fails, searching the path.
    m_SciteExecutable = FilePath(exe_path).AbsolutePath();
    assert(m_SciteExecutable.Exists());

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
    ReloadProperties();

    pEditor->WndProc(SCI_GRABFOCUS, 1, 0);

	UIAvailable();
}

void SciTECocoa::Command(unsigned long wParam, long) {
	int cmdID = ControlIDOfCommand(wParam);
    SciTEBase::MenuCommand(cmdID, 0);
}

FilePath SciTECocoa::GetDefaultDirectory() {
	const char *where = getenv("SciTE_HOME");
#ifdef SYSCONF_PATH
	if (!where) {
		where = SYSCONF_PATH;
	}
#else
	if (!where) {
		where = getenv("HOME");
	}
#endif

	if (where) {
		return FilePath(where);
	}

	return FilePath("");
}

FilePath SciTECocoa::GetSciteDefaultHome() {
	const char *where = getenv("SciTE_HOME");
#ifdef SYSCONF_PATH
	if (!where) {
		where = SYSCONF_PATH;
	}
#else
	if (!where) {
		where = getenv("HOME");
	}
#endif
	if (where) {
		return FilePath(where);

	}
	return FilePath("");
}

FilePath SciTECocoa::GetSciteUserHome() {
	// First looking for environment variable $SciTE_USERHOME
	// to set SciteUserHome. If not present we look for $SciTE_HOME
	// then defaulting to $HOME
	char *where = getenv("SciTE_USERHOME");
	if (!where) {
		where = getenv("SciTE_HOME");
		if (!where) {
			where = getenv("HOME");
		}
	}

	return FilePath(where);
}

bool SciTECocoa::Key(int keyval, int modifier) {
    (void)keyval;
    (void)modifier;
    printf("key val:%d, modi:%d\n", keyval, modifier);

	if (extender && extender->OnKey(keyval, modifier))
		return true;
    return false;
}
