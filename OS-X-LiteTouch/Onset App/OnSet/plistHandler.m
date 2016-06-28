//
//  plistHandler.m
//  DeployStudio Runtime
//
//  Created by Burgin, Thomas on 4/6/14.
//  Copyright (c) 2014 Burgin, Thomas. All rights reserved.
//

#import "plistHandler.h"

@implementation plistHandler

+ (NSMutableDictionary *) readPlist:(NSString *)plistPath {
    NSMutableDictionary* plistDict = [[NSMutableDictionary alloc] initWithContentsOfFile:plistPath];
    return plistDict;
}

+ (void) writePlist: (NSMutableDictionary *) plist plistPath: (NSString *) plistPath {
    [plist writeToFile:plistPath atomically:YES];
}

@end
