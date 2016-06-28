//
//  BashCommand.h
//  Setup Assistant
//
//  Created by Burgin, Thomas on 6/25/13.
//  Copyright (c) 2013. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface BashCommand : NSObject

+ (NSString*) shell: (NSString*)shell args: (NSArray*)args;

@end
