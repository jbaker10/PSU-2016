//
//  AppDelegate.m
//  OnSet
//
//  Created by Burgin, Thomas on 4/23/13.
//  Copyright (c) 2013 Burgin, Thomas. All rights reserved.
//

#import "AppDelegate.h"
#import <ServiceManagement/ServiceManagement.h>
#import <Security/Authorization.h>
#import <DiskArbitration/DiskArbitration.h>
#import "plistHandler.h"

NSString *const K_OnSetPlistPath = @"/private/var/tmp/OnSet/com.onset.plist";
NSString *const K_ResourcePath = @"/private/var/tmp/OnSet/Resources";
NSString *const K_PythonPath = @"/private/var/tmp/OnSet/Resources/onset.py";
NSString *const K_SystemVersionPath = @"/System/Library/CoreServices/SystemVersion.plist";


#pragma mark Init
@implementation AppDelegate
@synthesize firstTast,seccondTask,thirdTask,fourthTask,chooseAsset,chooseLocation,chooseOS,chooseLabOrGroup,firstTaskProg,seccondTaskProg,thirdTaskProg,fourthTaskProg,startButtonView,rebootButtonView;

- (void) awakeFromNib {
    [NSApp activateIgnoringOtherApps:YES];
}

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    [self mountServer];
    //Define Array Types
    NSMutableArray *primaryAdmins = [[NSMutableArray alloc] init];
    NSMutableArray *secondaryAdmins = [[NSMutableArray alloc] init];
    
    NSDictionary * adminUsersDict = [plistHandler readPlist:@"/Volumes/LiteTouch/AdminUsers.plist"];
    
    for (NSString *e in [[adminUsersDict objectForKey:@"Admin Accounts"] allKeys]){
        if ([[[[adminUsersDict objectForKey:@"Admin Accounts"] objectForKey:e] objectForKey:@"isSuperAdmin"]  isEqual: @"TRUE"]) {
            [primaryAdmins addObject:e];
        }
        else {
            [secondaryAdmins addObject:e];
        }
        
    }

    [chooseLocation addItemsWithObjectValues:primaryAdmins];
    [chooseLabOrGroup addItemsWithObjectValues:secondaryAdmins];
}

- (void)applicationDidBecomeActive:(NSNotification *)notification {
    [self listVolumes];
}

#pragma mark Buttons
- (IBAction)startProvisioning:(id)sender
{
    if ([self testInput] == TRUE){
        dispatch_queue_t backgroundQueue = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
        dispatch_async(backgroundQueue, ^{
        
        //First
        dispatch_async(dispatch_get_main_queue(), ^{[firstTaskProg setHidden:FALSE];[firstTaskProg startAnimation:firstTaskProg];});
        [self writeToPlist];
        NSImage *check = [[NSImage alloc] initByReferencingFile:[[NSBundle mainBundle] pathForResource:@"check" ofType:@"png"]];
        dispatch_async(dispatch_get_main_queue(), ^{[firstTast setImage:check];[firstTaskProg stopAnimation:firstTaskProg]; [firstTaskProg setHidden:TRUE];});
        
        //Seccond
        dispatch_async(dispatch_get_main_queue(), ^{[seccondTaskProg setHidden:FALSE];[seccondTaskProg startAnimation:seccondTaskProg];});
        //[self copyPlist];
        dispatch_async(dispatch_get_main_queue(), ^{[seccondTask setImage:check];[seccondTaskProg stopAnimation:seccondTaskProg];[seccondTaskProg setHidden:TRUE];});
        
        //Third
        dispatch_async(dispatch_get_main_queue(), ^{[thirdTaskProg setHidden:FALSE];[thirdTaskProg startAnimation:thirdTaskProg];});
        [self installStartupItems];
        dispatch_async(dispatch_get_main_queue(), ^{[thirdTask setImage:check];[thirdTaskProg stopAnimation:thirdTaskProg];[thirdTaskProg setHidden:TRUE];});
        
        //Fourth
        dispatch_async(dispatch_get_main_queue(), ^{[fourthTaskProg setHidden:FALSE];[fourthTaskProg startAnimation:fourthTaskProg];});
        dispatch_async(dispatch_get_main_queue(), ^{[fourthTask setImage:check];[fourthTaskProg stopAnimation:fourthTaskProg];[fourthTaskProg setHidden:TRUE];});

        //Swtich Buttons
        dispatch_async(dispatch_get_main_queue(), ^{[startButtonView setHidden:TRUE];});
        dispatch_async(dispatch_get_main_queue(), ^{[rebootButtonView setHidden:FALSE];});
        });
    }
}

- (IBAction)rebootMachine:(id)sender
{
    [[NSApplication sharedApplication] terminate:nil];
}

- (IBAction)openTerminal:(id)sender {
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:@"/Applications/Utilities/Terminal.app/Contents/MacOS/Terminal"];
    [task launch];
}

- (IBAction)openDiskUtility:(id)sender {
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:@"/Applications/Utilities/Disk Utility.app/Contents/MacOS/Disk Utility"];
    [task launch];
}


#pragma mark Check Inputs
- (BOOL)testInput
{

    NSUInteger lengthAsset = [[chooseAsset stringValue] length];
    NSUInteger lengthLoc = [[chooseLocation stringValue] length];
    NSUInteger lengthGroup = [[chooseLabOrGroup stringValue] length];
    NSUInteger lengthOS = [[chooseOS stringValue] length];

    NSString *sf = [[NSString alloc] initWithFormat:@""];
    
    if (lengthAsset == 8)
    {
        if (lengthLoc > 0)
        {
            sf = @"TRUE";
        }
        else
        {
            sf = @"FALSE";
            NSAlert *alert = [[NSAlert alloc] init];
            [alert addButtonWithTitle:@"OK"];
            [alert setMessageText:@"Please Choose a Location"];
            [alert setInformativeText:@"Please choose the location the computer will be deployed."];
            [alert setAlertStyle:NSWarningAlertStyle];
            [alert beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil contextInfo:nil];
        
        }
        
        if (lengthGroup > 0) {
            sf = @"TRUE";
        }
        else
        {
            sf = @"FALSE";
            NSAlert *alert = [[NSAlert alloc] init];
            [alert addButtonWithTitle:@"OK"];
            [alert setMessageText:@"Please Choose a Group or Lab"];
            [alert setInformativeText:@"Please choose the Group or Lab the computer will be deployed."];
            [alert setAlertStyle:NSWarningAlertStyle];
            [alert beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil contextInfo:nil];
        }
        
        if (lengthOS > 0) {
            sf = @"TRUE";
        }
        else
        {
            sf = @"FALSE";
            NSAlert *alert = [[NSAlert alloc] init];
            [alert addButtonWithTitle:@"OK"];
            [alert setMessageText:@"Please Choose an OS to Lite Touch"];
            [alert setInformativeText:@"Please choose the OS."];
            [alert setAlertStyle:NSWarningAlertStyle];
            [alert beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil contextInfo:nil];
        }
        }
    else
    {
        sf = @"FALSE";
        NSAlert *eightOnly = [[NSAlert alloc] init];
        [eightOnly addButtonWithTitle:@"OK"];
        [eightOnly setMessageText:@"NIH Asset Tags are 8 numbers"];
        [eightOnly setInformativeText:@"Please enter the NIH Asset Tag as displayed on the sticker attached to the machine."];
        [eightOnly setAlertStyle:NSWarningAlertStyle];
        [eightOnly beginSheetModalForWindow:[self window] modalDelegate:self didEndSelector:nil contextInfo:nil];
    }

    if ([sf isEqualToString:@"FALSE"])
    {
        return FALSE;
    }

    else
    {
        return TRUE;
    }
    
}

- (void)listVolumes
{
    // Clear out any previous items before checking
    [chooseOS removeAllItems];
    
    // Grab a liskt of media attached to the system
    NSArray *listOfMedia = [[NSArray alloc] initWithArray:[NSArray arrayWithObject:@""]];
    NSMutableArray* usableListOfMedia = [[NSMutableArray alloc] init];
    listOfMedia = [[NSWorkspace sharedWorkspace] mountedLocalVolumePaths];
    
    // Check out each volume
    for (NSString *volume in listOfMedia) {
        
        //Check to make sure the volume has OS X installed
        NSMutableDictionary * dict = [plistHandler readPlist:[NSString stringWithFormat:@"%@%@", volume, K_SystemVersionPath]];
        
        if (dict != NULL && ![volume  isEqual: @"/"]) {
            [usableListOfMedia addObject:volume];
        }
    }
    
    [chooseOS addItemsWithObjectValues:usableListOfMedia];
    if ([usableListOfMedia count] != 0) {
        [chooseOS selectItemAtIndex:0];
    }
    
    NSLog(@"%@", usableListOfMedia);
}

- (void)writeToPlist
{
    NSFileManager * fileManager = [NSFileManager defaultManager];
    [fileManager createDirectoryAtPath:[NSString stringWithFormat:@"%@/private/var/tmp/OnSet/", [chooseOS stringValue]] withIntermediateDirectories:TRUE attributes:nil error:nil];
    
    NSDictionary * adminUsersDict = [plistHandler readPlist:@"/Volumes/LiteTouch/AdminUsers.plist"];
    NSMutableDictionary * plistDict = [plistHandler readPlist:@"/Volumes/LiteTouch/LiteTouch.plist"];
    
    [plistDict setValue:[chooseAsset stringValue] forKey:@"AssetTag"];
    [plistDict setValue:[chooseLocation stringValue] forKey:@"Location"];
    [plistDict setValue:[chooseOS stringValue] forKey:@"InstallPath"];
    [plistDict setValue:K_ResourcePath forKey:@"ResourcePath"];
    [plistDict setValue:K_PythonPath forKey:@"PythonPath"];
    [plistDict setValue:[chooseLabOrGroup stringValue] forKey:@"GroupName"];
    
    // Set Master Admin Account
    [[plistDict objectForKey:@"Admins"] addObject:[[adminUsersDict objectForKey:@"Admin Accounts"] objectForKey:[chooseLocation stringValue]]];
    
    // Set Secondary Admin Accounts
    if ([[[[adminUsersDict objectForKey:@"Admin Accounts"] objectForKey:[chooseLabOrGroup stringValue]] objectForKey:@"RealName"] isEqualToString:@"null"]) {
        ;
    }
    else {
        [[plistDict objectForKey:@"Admins"] addObject:[[adminUsersDict objectForKey:@"Admin Accounts"] objectForKey:[chooseLabOrGroup stringValue]]];
    }

    // Write Plist to the OS
    [plistHandler writePlist:plistDict plistPath:[NSString stringWithFormat:@"%@%@", [chooseOS stringValue], K_OnSetPlistPath]];
    
}

#pragma mark Run while NetBooted
- (void)installStartupItems
{
    NSString *item;
    item = [chooseOS stringValue];
    
    
    NSTask *task;
    task = [[NSTask alloc] init];
    [task setLaunchPath:@"/usr/sbin/installer"];
    [task setArguments:[NSArray arrayWithObjects:@"-allowUntrusted", @"-pkg", @"/Volumes/LiteTouch/LiteTouch.pkg", @"-target", item, nil]];
    
    NSPipe *pipe;
    pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
    
    NSFileHandle *file;
    file = [pipe fileHandleForReading];
    
    [task waitUntilExit];
    [task launch];
    
    NSData *data;
    data = [file readDataToEndOfFile];
    
    NSString *string;
    string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
    NSLog(@"%@", string);
    
}

#pragma mark NSString Cleaner
- (NSString*)cleanOSString
{
    NSString *OSString = [[NSString alloc] initWithFormat:@"%@",[chooseOS stringValue]];
    OSString = [OSString stringByReplacingOccurrencesOfString:@" " withString:@"\\ "];
    //NSLog(@"%@",OSString);
    return OSString;
}

- (void)mountServer {
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *path = @"/usr/bin/hdiutil";
    NSArray *args = [NSArray arrayWithObjects:@"attach", @"http://172.16.163.130/Apps/LiteTouch.dmg", nil];
    if ([fileManager fileExistsAtPath:path]) {
        [[NSTask launchedTaskWithLaunchPath:path arguments:args] waitUntilExit];
    } else {
        NSLog(@"[+] Executable does not exist [%@]", path);
    }
}

- (void)applicationWillTerminate:(NSNotification *)notification {
    
    NSFileManager *fileManager = [NSFileManager defaultManager];
    NSString *path = @"/usr/bin/hdiutil";
    NSArray *args = [NSArray arrayWithObjects:@"detach", @"/Volumes/LiteTouch", nil];
    if ([fileManager fileExistsAtPath:path]) {
        [[NSTask launchedTaskWithLaunchPath:path arguments:args] waitUntilExit];
    } else {
        NSLog(@"[+] Executable does not exist [%@]", path);
    }
    
}

@end
