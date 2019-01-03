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

@interface AppDelegate ()
{
	SciTECocoa scite_cocoa;
  ScintillaView* mEditor;
  ScintillaView* mOutput;
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

  [mEditor setGeneralProperty: SCI_SETLEXER parameter: SCLEX_CPP value: 0];
	[mEditor setGeneralProperty: SCI_SETLEXERLANGUAGE parameter: 0 value: (sptr_t) "cpp"];
  [mEditor setStringProperty: SCI_STYLESETFONT parameter: STYLE_DEFAULT value: @"Helvetica"];
  [mEditor setGeneralProperty: SCI_STYLESETSIZE parameter: STYLE_DEFAULT value: 20];
  [mEditor setColorProperty: SCI_STYLESETFORE parameter: STYLE_DEFAULT value: [NSColor blackColor]];

	[self.window makeKeyWindow];
	delete argv;

	[self updateMenu];
}


- (void)applicationWillTerminate:(NSNotification *)aNotification {
	// Insert code here to tear down your application
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
	NSMenu *appMenu = [[mainMenu itemAtIndex:0] submenu];
	(void)appMenu;

	NSMenuItem *mainItem = [mainMenu addItemWithTitle:@"Main Item"
																						 action:@selector(foo:)
																			keyEquivalent:@""];

	NSMenu *submenu = [[NSMenu alloc] init];
	[submenu addItemWithTitle:@"Sub item" action:nil keyEquivalent:@""];

	[mainItem setSubmenu:submenu];

	[mainMenu addItem:mainItem];
	[[NSApplication sharedApplication] setMainMenu:submenu];
}

@end
