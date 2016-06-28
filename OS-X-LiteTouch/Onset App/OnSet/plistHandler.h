//
//  plistHandler.h
//  DeployStudio Runtime
//
//  Created by Burgin, Thomas on 4/6/14.
//  Copyright (c) 2014 Burgin, Thomas. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface plistHandler : NSObject

+ (NSMutableDictionary *) readPlist: (NSString *) plistPath;
+ (void) writePlist:(NSMutableDictionary *)writePlist plistPath:(NSString *)plistPath;

@end
