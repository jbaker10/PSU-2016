//
//  AppDelegate.h
//  OnSet
//
//  Created by Burgin, Thomas on 4/23/13.
//  Copyright (c) 2013 Burgin, Thomas. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface AppDelegate : NSObject <NSApplicationDelegate>{
    AuthorizationRef        _authRef;
}

@property (assign) IBOutlet NSWindow *window;
@property (weak) IBOutlet NSImageView *firstTast;
@property (weak) IBOutlet NSImageView *seccondTask;
@property (weak) IBOutlet NSImageView *thirdTask;
@property (weak) IBOutlet NSImageView *fourthTask;
@property (weak) IBOutlet NSComboBox *chooseOS;
@property (weak) IBOutlet NSComboBox *chooseLocation;
@property (weak) IBOutlet NSComboBox *chooseAsset;
@property (weak) IBOutlet NSProgressIndicator *firstTaskProg;
@property (weak) IBOutlet NSProgressIndicator *seccondTaskProg;
@property (weak) IBOutlet NSProgressIndicator *thirdTaskProg;
@property (weak) IBOutlet NSProgressIndicator *fourthTaskProg;
@property (weak) IBOutlet NSButton *startButtonView;
@property (weak) IBOutlet NSButton *rebootButtonView;
@property (weak) IBOutlet NSComboBox *chooseLabOrGroup;


- (IBAction)startProvisioning:(id)sender;
- (IBAction)rebootMachine:(id)sender;
- (IBAction)openTerminal:(id)sender;
- (IBAction)openDiskUtility:(id)sender;


@end
