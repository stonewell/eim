#include <string_view>
#include <vector>

#import "Platform.h"
#import "ScintillaView.h"
#import "ScintillaCocoa.h"

#import "scintilla_cocoa.h"

using namespace Scintilla;

// Add backend property to ScintillaView as a private category.
// Specified here as backend accessed by SCIMarginView and SCIContentView.
@interface ScintillaView()
@property(nonatomic, readonly) Scintilla::ScintillaCocoa *backend;
@end

extern "C"
ScintillaBase * get_backend(ScintillaView * view) {
	return view.backend;
}
