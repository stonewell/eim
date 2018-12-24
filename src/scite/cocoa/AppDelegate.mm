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
@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
	NSArray *args = [[NSProcessInfo processInfo] arguments];

	int argc = [args count];
	char ** argv = [self getArray:args];

	NSBundle *main = [NSBundle mainBundle];

  NSRect newFrame = [[self window] frame];
  newFrame.size.width -= 2 * newFrame.origin.x;
  newFrame.size.height -= 3 * newFrame.origin.y;

  mEditor = [[ScintillaView alloc] initWithFrame: newFrame];
  [mEditor setAutoresizesSubviews: YES];
  [mEditor setAutoresizingMask: NSViewWidthSizable | NSViewHeightSizable];

  mOutput = [[ScintillaView alloc] initWithFrame: newFrame];
  [mOutput setAutoresizesSubviews: YES];
  [mOutput setAutoresizingMask: NSViewWidthSizable | NSViewHeightSizable];

	[self.window.contentView addSubview:mEditor];

	scite_cocoa.Run([[main executablePath] UTF8String],
									get_backend(mEditor),
									get_backend(mOutput),
									argc, argv);
}


- (void)applicationWillTerminate:(NSNotification *)aNotification {
	// Insert code here to tear down your application
}

- (char**)getArray:(NSArray *)a_array {
	int count = [a_array count];
	char** array = new char *[count];

	for(int i = 0; i < count; i++)
	{
	array[i] = (char *)[[a_array objectAtIndex:i] UTF8String];
	}
	return array;
}


@end
