//
//  AppDelegate.m
//  SciTECocoa
//
//  Created by Jingnan Si on 12/23/18.
//  Copyright © 2018 Angelsto-Tech. All rights reserved.
//

#import "AppDelegate.h"
#import "scite_cocoa.h"
#import "ScintillaView.h"
#import "scintilla_cocoa.h"

static int TranslateModifierFlags(NSUInteger modifiers) {
	// Signal Control as SCI_META
	return
		(((modifiers & NSEventModifierFlagShift) != 0) ? SCI_SHIFT : 0) |
		(((modifiers & NSEventModifierFlagCommand) != 0) ? SCI_CTRL : 0) |
		(((modifiers & NSEventModifierFlagOption) != 0) ? SCI_ALT : 0) |
		(((modifiers & NSEventModifierFlagControl) != 0) ? SCI_META : 0);
}

static inline UniChar KeyTranslate(UniChar unicodeChar, NSEventModifierFlags modifierFlags) {
	switch (unicodeChar) {
	case NSDownArrowFunctionKey:
		return SCK_DOWN;
	case NSUpArrowFunctionKey:
		return SCK_UP;
	case NSLeftArrowFunctionKey:
		return SCK_LEFT;
	case NSRightArrowFunctionKey:
		return SCK_RIGHT;
	case NSHomeFunctionKey:
		return SCK_HOME;
	case NSEndFunctionKey:
		return SCK_END;
	case NSPageUpFunctionKey:
		return SCK_PRIOR;
	case NSPageDownFunctionKey:
		return SCK_NEXT;
	case NSDeleteFunctionKey:
		return SCK_DELETE;
	case NSInsertFunctionKey:
		return SCK_INSERT;
	case '\n':
	case 3:
		return SCK_RETURN;
	case 27:
		return SCK_ESCAPE;
	case '+':
		if (modifierFlags & NSEventModifierFlagNumericPad)
			return SCK_ADD;
		else
			return unicodeChar;
	case '-':
		if (modifierFlags & NSEventModifierFlagNumericPad)
			return SCK_SUBTRACT;
		else
			return unicodeChar;
	case '/':
		if (modifierFlags & NSEventModifierFlagNumericPad)
			return SCK_DIVIDE;
		else
			return unicodeChar;
	case 127:
		return SCK_BACK;
	case '\t':
	case 25: // Shift tab, return to unmodified tab and handle that via modifiers.
		return SCK_TAB;
	default:
		return unicodeChar;
	}
}

@interface AppDelegate ()
{
	SciTECocoa scite_cocoa;
  ScintillaView* mEditor;
  ScintillaView* mOutput;
	id _eventMonitor;
}
@property (weak) IBOutlet NSWindow *window;
- (char **)getArray:(NSArray *) args;
- (void)updateMenu;
@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
	NSArray *args = [[NSProcessInfo processInfo] arguments];

	int argc = [args count];
	char ** argv = [self getArray:args];

	NSBundle *main = [NSBundle mainBundle];

  NSRect newFrame = [self.window.contentView bounds];
	newFrame.origin.x = 0;

  [self.window.contentView setAutoresizesSubviews: YES];
  [self.window.contentView setAutoresizingMask: NSViewWidthSizable | NSViewHeightSizable];

  mEditor = [[ScintillaView alloc] initWithFrame: newFrame];
  [mEditor setAutoresizesSubviews: YES];
  [mEditor setAutoresizingMask: NSViewWidthSizable | NSViewHeightSizable];

	mOutput = [[ScintillaView alloc] initWithFrame: NSMakeRect(0,0,0,0)];
  [mOutput setAutoresizesSubviews: YES];
  [mOutput setAutoresizingMask: NSViewWidthSizable | NSViewHeightSizable];

	[self.window.contentView addSubview:mEditor];

	scite_cocoa.Run([[main executablePath] UTF8String],
									get_backend(mEditor),
									get_backend(mOutput),
									argc, argv);

 	[self.window makeKeyWindow];
	delete argv;

	[self updateMenu];

	_eventMonitor = [NSEvent addLocalMonitorForEventsMatchingMask:NSKeyDownMask
																												handler:^(NSEvent *incomingEvent) {
			NSEvent *result = incomingEvent;
			NSWindow *targetWindowForEvent = [incomingEvent window];

			if (targetWindowForEvent != _window) {
			return result;
			}

			// For now filter out function keys.
			NSString *input = incomingEvent.charactersIgnoringModifiers;

			bool handled = false;
			// Handle each entry individually. Usually we only have one entry anyway.
			for (size_t i = 0; i < input.length; i++) {
			const UniChar originalKey = [input characterAtIndex: i];
			NSEventModifierFlags modifierFlags = incomingEvent.modifierFlags;

			UniChar key = KeyTranslate(originalKey, modifierFlags);

			if (scite_cocoa.Key(key, TranslateModifierFlags(modifierFlags)))
				handled = true;
			}

			if (handled) {
			result = nil;
			}

			return result;
    }];
}


- (void)applicationWillTerminate:(NSNotification *)aNotification {
	// Insert code here to tear down your application
	[NSEvent removeMonitor:_eventMonitor];
}

- (char**)getArray:(NSArray *)a_array {
	int count = [a_array count];
	char** array = new char *[count];

	for(int i = 0; i < count; i++) {
	array[i] = (char *)[[a_array objectAtIndex:i] UTF8String];
	}
	return array;
}

- (void)updateMenu {
	NSMenu * mainMenu = [NSApp mainMenu];
	NSMenuItem * item = [mainMenu itemAtIndex:0];
	NSMenu *appMenu = [item submenu];
	(void)appMenu;

	// NSMenuItem *mainItem = [mainMenu addItemWithTitle:@"Main Item"
	// 																					 action:@selector(foo:)
	// 																		keyEquivalent:@""];

	NSMenu *submenu = [[NSMenu alloc] init];
	[submenu addItemWithTitle:@"Sub item" action:nil keyEquivalent:@""];

	//[mainItem setSubmenu:submenu];

	//[[mainMenu itemAtIndex:1] setSubmenu:submenu];
	//[mainMenu addItem:item];
}

@end
