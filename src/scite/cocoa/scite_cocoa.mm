#import <Cocoa/Cocoa.h>

extern "C"
void quit_progam() {
	[NSApp terminal:nil];
}
