#!/bin/sh

hdiutil attach http://IP_ADDRESS_GOES_HERE/Apps/LiteTouch.dmg;
/Volumes/LiteTouch/Onset.app/Contents/MacOS/Onset;
hdiutil eject /Volumes/LiteTouch;

exit 0;