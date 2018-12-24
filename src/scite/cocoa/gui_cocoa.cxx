#include <sys/time.h>

#include <string>
#include <sstream>
#include <mutex>
#include <map>
#include <vector>

#include "Scintilla.h"

#include "GUI.h"
#include "Mutex.h"

#include "Platform.h"
#include "ILoader.h"
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

extern "C"
const GUI::gui_char appName[] = GUI_TEXT("SciTE");

class MyMutex : public Mutex{
public:
	virtual void Lock() { m_mutex.lock(); }
	virtual void Unlock() { m_mutex.unlock();}
	virtual ~MyMutex() {}

    std::mutex m_mutex;
};

Mutex * Mutex::Create() {
    return new MyMutex();
}

namespace GUI {

ElapsedTime::ElapsedTime() {
	struct timeval tv {0, 0};
    struct timezone tz {0, 0};
	gettimeofday(&tv, &tz);
	bigBit = tv.tv_sec;
	littleBit = tv.tv_usec;
}

double ElapsedTime::Duration(bool reset) {
	struct timeval tv {0, 0};
    struct timezone tz {0, 0};
	gettimeofday(&tv, &tz);

	long endBigBit = tv.tv_sec;
	long endLittleBit = tv.tv_usec;
	double result = 1000000.0 * (endBigBit - bigBit);
	result += endLittleBit - littleBit;
	result /= 1000000.0;
	if (reset) {
		bigBit = endBigBit;
		littleBit = endLittleBit;
	}
	return result;
}

sptr_t ScintillaPrimitive::Send(unsigned int msg, uptr_t wParam, sptr_t lParam) {
    Scintilla::ScintillaBase * base = reinterpret_cast<Scintilla::ScintillaBase *>(GetID());

	return base->WndProc(msg, wParam, lParam);
}

bool IsDBCSLeadByte(int codePage, char ch) {
	// Byte ranges found in Wikipedia articles with relevant search strings in each case
	unsigned char uch = static_cast<unsigned char>(ch);
	switch (codePage) {
    case 932:
        // Shift_jis
        return ((uch >= 0x81) && (uch <= 0x9F)) ||
				((uch >= 0xE0) && (uch <= 0xEF));
    case 936:
        // GBK
        return (uch >= 0x81) && (uch <= 0xFE);
    case 950:
        // Big5
        return (uch >= 0x81) && (uch <= 0xFE);
		// Korean EUC-KR may be code page 949.
	}
	return false;
}

gui_string StringFromUTF8(const char *s) {
	if (s)
		return gui_string(s);
	else
		return gui_string("");
}

gui_string StringFromUTF8(const std::string &s) {
	return s;
}

std::string UTF8FromString(const gui_string &s) {
	return s;
}

gui_string StringFromInteger(long i) {
	char number[32];
	sprintf(number, "%0ld", i);
	return gui_string(number);
}

gui_string StringFromLongLong(long long i) {
	try {
		std::ostringstream strstrm;
		strstrm << i;
		return StringFromUTF8(strstrm.str());
	} catch (std::exception &) {
		// Exceptions not enabled on stream but still causes diagnostic in Coverity.
		// Simply swallow the failure and return the default value.
	}
	return gui_string();
}

gui_string HexStringFromInteger(long i) {
	char number[32];
	sprintf(number, "%0lx", i);
	gui_char gnumber[32];
	size_t n = 0;
	while (number[n]) {
		gnumber[n] = static_cast<gui_char>(number[n]);
		n++;
	}
	gnumber[n] = 0;
	return gui_string(gnumber);
}

std::string LowerCaseUTF8(std::string_view sv) {
	std::string sLower(sv);

    std::transform(sLower.begin(), sLower.end(), sLower.begin(), ::tolower);

	return sLower;
}

void Window::Destroy() {
	wid = 0;
}

bool Window::HasFocus() {
	return true;
}

Rectangle Window::GetPosition() {
	// Before any size allocated pretend its 1000 wide so not scrolled
	Rectangle rc(0, 0, 1000, 1000);
	return rc;
}

void Window::SetPosition(Rectangle rc) {
}

Rectangle Window::GetClientPosition() {
	return GetPosition();
}

void Window::Show(bool show) {
}

void Window::InvalidateAll() {
}

void Window::SetTitle(const char *s) {
}

void Menu::CreatePopUp() {
	Destroy();
}

void Menu::Destroy() {
	mid = 0;
}

void Menu::Show(Point pt, Window &) {
}
};
