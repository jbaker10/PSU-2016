OSXLiteTouch
============

Initial modular setup for enterprise Macs

At NIMH we use 2 methods for imaging a Mac: either a NetBoot image, or a NetInstaller, depending on if the machine is brand new or not. If the machine is brand new, then we want to leave the original OS intact and use the NetBoot to add stuff to the current OS. If it is a computer that has been used before, needs to be wiped and then have the OS reinstalled, we want to use the NetInstaller.

## NetBoot Process
As mentioned above, the NetBoot is used with a fresh machine, or any Mac with a fresh OS installed. The NetBoot is built using the DeployStudio Assistant.app to create the NetBoot image. We then replace the Runtime that is within the .nbi created from DS. To do this, open the NetInstall.dmg within the .nbi created. Once the volume is mounted, change into the following directory: `/Volumes/DeployStudioRuntime/Applications/Utilities/DeployStudio\ Admin/Contents/Applications/` and within there you will see two applications, DeployStudio Assistant and DeployStudio Runtime. We wanted to replace the DeployStudio Runtime with the app under `Onset App/build` in the Github repo. This is our custom app which is built using Xcode.

## NetInstaller Process
The NetInstaller process is a bit simpler than the NetBoot process above. It uses Apple's System Image Utility to create the NetInstaller. You will need an OS X Installer.app of your OS version choice, and then the Onset pkg found in the `Onset/build/Onset-distro.pkg` directory. The Onset.pkg runs after the OS has been installed on the machine but before the reboot, and all it does is run a postinstall script that mounts a DMG stored on a server. That DMG contains our custom Onset Runtime, like the one used in the NetBoot process.

## Custom Onset Runtime
The custom Runtime allows us to enter information such as decal number (which will be used to name the machine i.e. MH02001234LT) and choose what Local Admins we want on the machine.

## Interaction between Onset and LiteTouch
In both processes (NetBoot and NetInstall), the Onset application (Deploystudio Runtime.app) is called in order to show the GUI interface. After the information is entered (i.e. decal number and lab), it mounts the LiteTouch image and uses that to then perform certain functions. See the Wiki on LiteTouch for more information about that.
