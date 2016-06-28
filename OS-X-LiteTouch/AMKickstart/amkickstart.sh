#!/bin/bash
#
# Force LANrev to install software at the login window.

declare -r AMSERVER="" ## Enter the IP address or hostname of your LANrev server
declare -r AMDIR="/Library/Application Support/LANrev Agent"
declare -r AMAGENT="$AMDIR/LANrev Agent.app/Contents/MacOS/LANrev Agent"
declare -r LOGFILE="/var/log/com.somelog.onset.log"


# Redirect stdout and stderr to a log file with date stamps.
exec > >(perl -MPOSIX -pe \
            '$| = 1; print POSIX::strftime("%m/%d/%Y %r", localtime), " [+] ";' \
            >> "$LOGFILE") 2>&1

## This initial check is so that we can determine whether we need to worry about adding adapters to the machine or not.
## If the ping is successful, it will continue with the script without manually adding netowrk adapters.
function pingCheck() {  
    echo ""
    echo "**********************"
    echo "Attempting to ping $AMSERVER"
    echo "**********************"
    echo ""

    while ! ping -q -c 1 "$AMSERVER" &>/dev/null; do
        echo ""
        echo "**********************"
        echo "Unable to reach $AMSERVER. Please ensure a network adapter has been plugged into the machine."
        echo "Will attempt to manually setup a network adapter"
        echo "**********************"
        echo ""
        sleep 1;
        checkAvailableAdapters;
    done
}

## We had some issues with new network adapters not being detected upon first boot, and therefore the imaging process never could finish
function checkAvailableAdapters() {
    ## First we want to try the detect command to see if Apple can add the adapters for us
    local availableNetworks=$( /usr/sbin/networksetup -detectnewhardware )
    local availableNetworks=$( /usr/sbin/networksetup -listallnetworkservices )
    if [[ $availableNetworks != *USB\ Ethernet* ]]; then
        echo "Did not detect a USB Ethernet interface. Will check for Thunderbolt Ethernet"
        if [[ $availableNetworks != *Thunderbolt\ Ethernet* ]]; then
            echo ""
            echo "**********************"
            echo "Unable to detect a network adapter automatically. Will try to manually set one up."
            echo "**********************"
            echo ""
            createThunderboltEth;
        else
            echo ""
            echo "The Thunderbolt Ethernet adapter has been detected. Will proceed with rest of script."
            echo ""
        fi
    else
        echo ""
        echo "The USB Ethernet interface adapter has been detected. Will proceed with rest of script."
        echo ""
    fi
}

## This function will try to create the Thunderbolt Ethernet adapter. We are going to try this first since it is
## more commonly used and much faster
function createThunderboltEth(){
    local server="$1"

    echo ""
    echo "**********************"
    echo "Attempting to create a Thunderbolt Ethernet connection."
    echo "**********************"
    echo ""

    /usr/sbin/networksetup -createnetworkservice "Thunderbolt Ethernet" en3 &>/dev/null
    sleep 2

    local availableNetworks=$( /usr/sbin/networksetup -listallnetworkservices )
    if [[ $availableNetworks == *Thunderbolt\ Ethernet* ]]; then
        echo ""
        echo "The Thunderbolt Ethernet adapter has been successfully added"
        echo ""
        echo ""
        echo "Sleeping 10 seconds to allow interface to get IP"
        echo ""
        sleep 10
        echo ""
        echo "Attempting to ping $AMSERVER with new network interface"
        echo ""
        local i=0
        while ! ping -q -c 1 "$AMSERVER" &>/dev/null; do
            sleep 3
            local i=$((i+1))
            if [ $i -eq 3 ]; then
                echo ""
                echo "Still unable to reach the internal server, will try to add the USB Ethernet and connect with that"
                echo ""
                createUSBEth;
                break
            fi
        done
    else
        echo ""
        echo "The Thunderbolt Ethernet adapter was not added, will attempt to create USB Ethernet"
        echo ""
        createUSBEth;
    fi
}

## This function will try to create the USB Ethernet adapter. If the Thunderbolt Ethernet fails to be added
## or is added but can't talk to the server, we will try to do the same with the USB Ethernet
function createUSBEth() {
    local server="$1"

    echo ""
    echo "**********************"
    echo "Attempting to create a USB Ethernet connection."
    echo "**********************"
    echo ""

    /usr/sbin/networksetup -createnetworkservice "USB Ethernet" en5 &>/dev/null
    sleep 2

    local availableNetworks=$( /usr/sbin/networksetup -listallnetworkservices )
    if [[ $availableNetworks == *USB\ Ethernet* ]]; then
        echo ""
        echo "The USB Ethernet adapter has been successfully added"
        echo ""
        echo ""
        echo "Sleeping 10 seconds to allow interface to get IP"
        echo ""
        sleep 10
        echo ""
        echo "Attempting to ping $AMSERVER with new network interface"
        echo ""
        local i=0
        while ! ping -q -c 1 "$AMSERVER" &>/dev/null; do
            sleep 1
            local i=$((i+1))
            if [ $i -eq 3 ]; then
                echo ""
                echo "**********************"
                echo "Unable to connect to the internal server."
                echo "Please make sure a network adapter is connected."
                echo "The script will cycle through every 10 seconds and try to add network adapters."
                echo ""
                echo "If a network adapter is plugged in, try removing it and pluggin it back in and wait 10 seconds."
                echo ""
                echo "If the script is STILL not working, quit the app (Cmd+Q) and login to the machine"
                echo "**********************"
                echo ""
                sleep 10;
                pingCheck;
            fi
        done
    else
        echo ""
        echo "**********************"
        echo "The attempt to add the USB Ethernet adapter failed. Please make sure a network adapter is connected."
        echo "The script will cycle through every 10 seconds and retry to add network adapters."
        echo ""
        echo "If a network adapter is plugged in, try removing it and pluggin it back in and wait 10 seconds."
        echo ""
        echo "If the script is STILL not working, quit the app (Cmd+Q) and login to the machine"
        echo ""
        sleep 10;
        pingCheck;
    fi
}

# Wait until a path exists.
function wait_for_path() {
    local path="$1"
    
    while [[ ! -e "$path" ]]; do
        echo "..."
        sleep 5
    done
}

# Wait for ping reply from server.
function wait_for_ping() {
    local server="$1"
    
    echo "Waiting for $server to respond"
    while ! ping -q -c 1 "$server" &>/dev/null; do
        sleep 1
    done
    echo "The Absolute Manage server $AMSERVER has responded"
    echo ""
    echo "***************************************"
    echo "***************************************" 
    echo ""
    echo "If you would like to SSH in and monitor the status, the IP is shown below:"
    ifconfig | grep "inet" | grep -v 127.0.0.1 | cut -d\  -f2 | grep -v :
    echo ""
    echo "***************************************"
    echo "***************************************"
    echo ""
    sleep 20;
}

# Wait until the AM agent's status is idle.
function wait_amagent_idle() {
    local status
    local sdstate=""
    local newstate
    
    while true; do
        amstatus=$( "$AMAGENT" --GetSDState 2>/dev/null )
        returncode=$?
        echo $ret
        if [[ "$returncode" -eq 0 ]]; then
            if [[ "$amstatus" -eq 0 ]]; then
                break
            else
                newstate=$( "$AMAGENT" --GetSDStateString 2>/dev/null )
                if [[ "$newstate" != "$sdstate" ]]; then
                    sdstate="$newstate"
                    echo "$sdstate"
                fi
            fi
        fi
        sleep 5
        let count=count+5
    done
}

# Send inventory.
function am_send_inventory() {
    wait_amagent_idle
    echo ""
    echo "**********************"
    echo "Sending inventory"
    echo "**********************"    
    echo ""
    "$AMAGENT" --SendInventory 2>/dev/null
    sleep 5
    echo ""
    echo "**********************"
    echo "Inventory was successfully sent"
    echo "**********************"    
    echo ""
}

# Perform software distribution check.
function am_sdcheck() {
    wait_amagent_idle
    echo ""
    echo "**********************"
    echo "Checking software distribution"
    echo "**********************"    
    echo ""
    "$AMAGENT" --SDCheck 2>/dev/null
    sleep 5
    echo ""
    echo "**********************"
    echo "The software installation will now begin"
    echo "**********************"
    echo ""
}

function enable_am_logging() {
    
    echo ""
    echo "**********************"
    echo "Enable AM Debug Logs"
    echo "**********************"
    echo ""

    /usr/bin/defaults write /Library/Preferences/com.poleposition-sw.lanrev_agent DefaultLogLevel 6 2>/dev/null
    /bin/launchctl unload "/Library/LaunchDaemons/com.poleposition-sw.LANrevAgent.plist" 2>/dev/null
    /bin/launchctl load "/Library/LaunchDaemons/com.poleposition-sw.LANrevAgent.plist" 2>/dev/null
    ## Adding a function below to kill the subprocess of `tail` before running it again.
    childPID=$( pgrep -P $$ )
    kill -9 $childPID 2>/dev/null
    sleep 60
    ## This is to resolve the issue after the first reboot that was preventing the LoginLog.app to see the output again
    /usr/bin/tail -f "/Library/Logs/LANrev Agent.log" > "/var/log/com.github.jbaker10.onset.log" &
}

function disable_am_logging() {
    
    echo ""
    echo "**********************"
    echo "Disable AM Debug Logs"
    echo "**********************"
    echo ""

    /usr/bin/defaults write /Library/Preferences/com.poleposition-sw.lanrev_agent DefaultLogLevel 5 2>/dev/null
    /bin/launchctl unload "/Library/LaunchDaemons/com.poleposition-sw.LANrevAgent.plist" 2>/dev/null
    /bin/launchctl load "/Library/LaunchDaemons/com.poleposition-sw.LANrevAgent.plist" 2>/dev/null
    childPID=$( pgrep -P $$ )
    kill -9 $childPID 2>/dev/null
}

## This script requires being run by root, so before doing anything, we need to make sure this is true
checkIfRoot() {
    ## Make sure only root can run the script
    if [[ $EUID -ne 0 ]]; then
       echo "This script must be run as root. Exiting..." 1>&2
       exit 1;
    else
        echo "The script is running as root."
    fi
}

function main() {

    checkIfRoot;
    pingCheck;
    local name
    local datestamp
    local i
    
    name=$( scutil --get ComputerName 2>/dev/null || echo '<no name>' )
    datestamp=$( date +'%m/%d/%Y %r' )
    
    echo ""
    echo "**********************"
    echo "Absolute Manage kickstart for $name ($datestamp)"
    echo "**********************"
    echo ""

    sleep 5
    
    wait_for_path "$AMAGENT"
    wait_for_ping "$AMSERVER"

    enable_am_logging

    for i in 1 2; do
        am_send_inventory
        am_sdcheck
        echo "running"
    done
    
    disable_am_logging
    datestamp=$( date +'%m/%d/%Y %r' )
    
    echo ""
    echo "**********************"
    echo "Kickstart done ($datestamp)"
    echo "**********************"
    echo ""
}

main "$@"