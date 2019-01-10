#pragma once
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <fcntl.h>
#include <stdarg.h>
#include <sys/stat.h>

#include <string>
#include <vector>
#include <deque>
#include <set>
#include <map>
#include <algorithm>
#include <memory>
#include <sstream>
#include <iomanip>

#include "Scintilla.h"
#include "ILoader.h"

#include "GUI.h"
#include "ScintillaWindow.h"
#include "MultiplexExtension.h"
#include "LuaExtension.h"

#include "StringList.h"
#include "StringHelpers.h"
#include "FilePath.h"
#include "StyleDefinition.h"
#include "PropSetFile.h"
#include "StyleWriter.h"
#include "Extender.h"
#include "SciTE.h"
#include "Mutex.h"
#include "JobQueue.h"
#include "Cookie.h"
#include "Worker.h"
#include "FileWorker.h"
#include "MatchMarker.h"
#include "SciTEBase.h"
#include "SciTEKeys.h"
#include "StripDefinition.h"

#include "Platform.h"
#include "ILexer.h"

#ifdef SCI_LEXER
#include "SciLexer.h"
#include "PropSetSimple.h"
#endif

#include "Position.h"
#include "UniqueString.h"
#include "SplitVector.h"
#include "Partitioning.h"
#include "RunStyles.h"
#include "ContractionState.h"
#include "CellBuffer.h"
#include "CallTip.h"
#include "KeyMap.h"
#include "Indicator.h"
#include "LineMarker.h"
#include "Style.h"
#include "ViewStyle.h"
#include "CharClassify.h"
#include "Decoration.h"
#include "CaseFolder.h"
#include "Document.h"
#include "CaseConvert.h"
#include "UniConversion.h"
#include "DBCS.h"
#include "Selection.h"
#include "PositionCache.h"
#include "EditModel.h"
#include "MarginView.h"
#include "EditView.h"
#include "Editor.h"

#include "AutoComplete.h"
#include "ScintillaBase.h"

extern "C" {
    void quit_progam();
}

class SciTECocoa : public SciTEBase {
public:
    SciTECocoa();
    virtual ~SciTECocoa() = default;
	virtual void Find() {}
	virtual MessageBoxChoice WindowMessageBox(GUI::Window &, const GUI::gui_string &, MessageBoxStyle style = mbsIconWarning) {(void)style; return mbOK;}
	virtual void FindMessageBox(const std::string &, const std::string *findItem = 0) {(void)findItem;}
	virtual void FindIncrement() {}
	virtual void FindInFiles() {}
	virtual void Replace() {}
	virtual void DestroyFindReplace() {}
	virtual void GoLineDialog() {}
	virtual bool AbbrevDialog() {return false;}
	virtual void TabSizeDialog() {}
	virtual bool ParametersOpen() {return false;}
	virtual void ParamGrab() {}
	virtual bool ParametersDialog(bool) {return false;}
	virtual void FindReplace(bool) {}
	virtual void StopExecute() {}
	virtual void SetFileProperties(PropSetFile &) {}
	virtual void AboutDialog() {}
	virtual void QuitProgram() {
        quit_progam();
    }
	virtual void SetStatusBarText(const char *) {}
	virtual void ShowToolBar() {}
	virtual void ShowTabBar() {}
	virtual void ShowStatusBar() {}
	virtual void ActivateWindow(const char *) {}
	virtual void SizeContentWindows() {}
	virtual void SizeSubWindows() {}

	virtual void SetMenuItem(int, int , int ,
                             const GUI::gui_char *, const GUI::gui_char *mnemonic = 0) {(void)mnemonic;}
	virtual void DestroyMenuItem(int, int) {}
	virtual void CheckAMenuItem(int, bool) {}
	virtual void EnableAMenuItem(int, bool) {}
	virtual void AddToPopUp(const char *, int cmd = 0, bool enabled = true) {(void)cmd;(void)enabled;}
	virtual void TabInsert(int, const GUI::gui_char *) {}
	virtual void TabSelect(int) {}
	virtual void RemoveAllTabs() {}
	virtual void WarnUser(int) {}
	virtual bool OpenDialog(const FilePath &, const GUI::gui_char *) {return false;}
	virtual bool SaveAsDialog() {return false;}
	virtual void SaveACopy() {}
	virtual void SaveAsHTML() {}
	virtual void SaveAsRTF() {}
	virtual void SaveAsPDF() {}
	virtual void SaveAsTEX() {}
	virtual void SaveAsXML() {}
	virtual bool PerformOnNewThread(Worker *) {return false;}
	// WorkerListener
	virtual void PostOnMainThread(int, Worker *) {}
	virtual void GetWindowPosition(int *, int *, int *, int *, int *) {}
    virtual bool PreOpenCheck(const GUI::gui_char *) {return false;}
	virtual FilePath GetDefaultDirectory();
	virtual FilePath GetSciteDefaultHome();
	virtual FilePath GetSciteUserHome();

    void Run(const char * exe_path, Scintilla::ScintillaBase * pEditor, Scintilla::ScintillaBase* pOutput, int argc, char * argv[]);
    void Command(unsigned long wParam, long);
    bool Key(int keyval, int modifier);

    FilePath m_SciteExecutable;
    Scintilla::ScintillaBase* mEditor;
    Scintilla::ScintillaBase* mOutput;
};
