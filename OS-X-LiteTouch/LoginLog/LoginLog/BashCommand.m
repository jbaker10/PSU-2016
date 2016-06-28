//
//  BashCommand.m
//  Setup Assistant
//
//  Created by Burgin, Thomas on 6/25/13.
//  Copyright (c) 2013. All rights reserved.
//

#import "BashCommand.h"

@implementation BashCommand

+ (NSString*) shell:(NSString*)shell args:(NSArray*)args
{
    NSTask *task;
    task = [[NSTask alloc] init];
    [task setLaunchPath:shell];
    [task setArguments:args];
    
    NSPipe *pipe;
    pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
    NSFileHandle *file;
    file = [pipe fileHandleForReading];
    
    [task launch];
    
    NSData *data;
    data = [file readDataToEndOfFile];
    
    NSString *string;
    string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
    return string;
}

@end
