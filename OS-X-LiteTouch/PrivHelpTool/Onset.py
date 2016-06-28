#!/usr/bin/python
# Created by Jeremiah Baker
## OnSet v1.0

import sys, os, getopt, base64, zlib, subprocess, time, io, signal
import plistlib
import logging
import datetime
import urllib2
import smtplib
from subprocess import Popen, PIPE, STDOUT
from Foundation import NSPropertyListSerialization
from Foundation import NSPropertyListXMLFormat_v1_0
from Foundation import NSPropertyListBinaryFormat_v1_0
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

EMAIL_ADDRESS=""  ## Place your email here

def sendEmail(addresses, plistDict):
    htmlEmail = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
        <meta name="viewport" content="width=device-width" />
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <title>Really Simple HTML Email Template</title>
        <style>
        /* -------------------------------------
        GLOBAL
        ------------------------------------- */
        * {
        margin: 0;
        padding: 0;
        font-family: "Helvetica Neue", "Helvetica", Helvetica, Arial, sans-serif;
        font-size: 100%;
        line-height: 1.6;
        }
        img {
        max-width: 100%;
        }
        body {
        -webkit-font-smoothing: antialiased;
        -webkit-text-size-adjust: none;
        width: 100%!important;
        height: 100%;
        }
        /* -------------------------------------
        ELEMENTS
        ------------------------------------- */
        a {
        color: #348eda;
        }
        .btn-primary {
        text-decoration: none;
        color: #FFF;
        background-color: #348eda;
        border: solid #348eda;
        border-width: 10px 20px;
        line-height: 2;
        font-weight: bold;
        margin-right: 10px;
        text-align: center;
        cursor: pointer;
        display: inline-block;
        border-radius: 25px;
        }
        .btn-secondary {
        text-decoration: none;
        color: #FFF;
        background-color: #aaa;
        border: solid #aaa;
        border-width: 10px 20px;
        line-height: 2;
        font-weight: bold;
        margin-right: 10px;
        text-align: center;
        cursor: pointer;
        display: inline-block;
        border-radius: 25px;
        }
        .last {
        margin-bottom: 0;
        }
        .first {
        margin-top: 0;
        }
        .padding {
        padding: 10px 0;
        }
        /* -------------------------------------
        BODY
        ------------------------------------- */
        table.body-wrap {
        width: 100%;
        padding: 20px;
        }
        table.body-wrap .container {
        border: 1px solid #f0f0f0;
        }
        /* -------------------------------------
        FOOTER
        ------------------------------------- */
        table.footer-wrap {
        width: 100%;
        clear: both!important;
        }
        .footer-wrap .container p {
        font-size: 12px;
        color: #666;
        
        }
        table.footer-wrap a {
        color: #999;
        }
        /* -------------------------------------
        TYPOGRAPHY
        ------------------------------------- */
        h1, h2, h3 {
        font-family: "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif;
        color: #000;
        margin: 40px 0 10px;
        line-height: 1.2;
        font-weight: 200;
        }
        h1 {
        font-size: 36px;
        }
        h2 {
        font-size: 28px;
        }
        h3 {
        font-size: 22px;
        }
        p, ul, ol {
        margin-bottom: 10px;
        font-weight: normal;
        font-size: 14px;
        }
        ul li, ol li {
        margin-left: 5px;
        list-style-position: inside;
        }
        /* ---------------------------------------------------
        RESPONSIVENESS
        Nuke it from orbit. It's the only way to be sure.
        ------------------------------------------------------ */
        /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
        .container {
        display: block!important;
        max-width: 1000px!important;
        margin: 0 auto!important; /* makes it centered */
        clear: both!important;
        }
        /* Set the padding on the td rather than the div for Outlook compatibility */
        .body-wrap .container {
        padding: 20px;
        }
        /* This should also be a block element, so that it will fill 100% of the .container */
        .content {
        max-width: 600px;
        margin: 0 auto;
        display: block;
        }
        /* Let's make sure tables in the content area are 100% wide */
        .content table {
        width: 100%;
        }
        
        /* Database Styles */
        .ToadExtensionTableContainer {
        padding: 0px;
        border: 6px solid #348eda;
        -moz-border-radius: 8px;
        -webkit-border-radius: 8px;
        -khtml-border-radius: 8px;
        border-radius: 8px;
        overflow: auto;
        }
        
        .ToadExtensionTable {
        width: 100%;
        border: 0px;
        border-collapse: collapse;
        font-family: Arial, Tahoma, Verdana, "Times New Roman", Georgia, Serif;
        font-size: 12px;
        padding: 1px;
        border: 1px solid #fff;
        }
        
        th {
        padding: 2px 4px;
        border: 1px solid #fff;
        }
        
        td {
        padding: 2px 4px;
        border: 1px solid #fff;
        }
        
        .HeaderColumnEven {
        background: #75b2e6;
        color: #fff;
        }
        
        .HeaderColumnOdd {
        background: #348eda;
        color: #fff;
        }
        
        .R0C0 {
        background: #F3FAFC;
        }
        
        .R0C1 {
        background: #E1EEFA;
        }
        
        .R1C0 {
        background: #CFE9F2;
        }
        
        .R1C1 {
        background: #B3DCEB;
        }
        
        .lft {
        text-align: left;
        }
        
        .rght {
        text-align: right;
        }
        
        .cntr {
        text-align: center;
        }
        
        .jstf {
        text-align: justify;
        }
        
        .nowrap {
        white-space: nowrap;
        }
        
        </style>
        </head>
        
        <body bgcolor="#f6f6f6">
        
        <!-- body -->
        <table class="body-wrap" bgcolor="#f6f6f6">
        <td class="container" bgcolor="#FFFFFF">        
        <!-- content -->
        <div class="content">
        <table>
          <tr>
            <td>
              <h1>Computer Finished Imaging</h1>
              <p>Greetings:</p>
              <p>The following computer was just imaged:</p>
            </td>
          </tr>
        </table>
        </div>
        <!-- /content -->
        <div class="ToadExtensionTableContainer">
        <table class="ToadExtensionTable">
        <tr>
        <th class="HeaderColumnOdd">Time Imaged</th>
        <th class="HeaderColumnEven">Machine Name</th>
        <th class="HeaderColumnOdd">Location</th>
        <th class="HeaderColumnEven">Lab/Group</th>
        <th class="HeaderColumnOdd">FileVault Status</th>
        </tr>
    '''
      	  
    values = '''  <tr>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          </tr>
        </td>
      </tr> 
    </table>
    <!-- /body -->
    </body>
    </html>''' % (  datetime.datetime.today(), \
                    machineName, \
                    plistDict["Location"], \
                    plistDict["GroupName"], \
                    fdeStatus())

 
    htmlEmail = htmlEmail + values
    #htmlEmail = htmlEmail + str(machineDict)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Machine Finished Imaging'
    msg['From'] = 'LANrevImaging@gmail.com'
    msg['To'] = addresses[0]
        
    text = "Machine Finished Imaging"
        
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(htmlEmail, 'html')
    # part3 = MIMEApplication(open("missing.csv","rb").read())
    # part3.add_header('Content-Disposition', 'attachment', filename = "missing.csv")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # msg.attach(part3)

    s = smtplib.SMTP('smtp-relay.gmail.com')
    s.sendmail(addresses[0], addresses, msg.as_string())
    s.quit()


def create_user(username, realname, hash, pic):
    bashCommand('. /etc/rc.common')
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username])
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "RealName", realname])
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "picture", "%s" % pic])
    uid = findOpenUniqueID()
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "UniqueID", str(uid)])
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "PrimaryGroupID", "80"])
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "UserShell", "/bin/bash"])
    bashCommand(["/usr/bin/dscl", ".", "create", "/Users/%s" % username, "NFSHomeDirectory", "/Users/%s" % username])
    bashCommand(["/bin/cp", "-R", "/System/Library/User Template/English.lproj", "/Users/%s" % username])
    bashCommand(["/usr/sbin/chown", "-R", "%s:staff" % username, "/Users/%s" % username])
    writeHash(username, hash)


def writeHash(username, userHash):

    bashCommand(['dscacheutil', '-flushcache'])
    time.sleep(2)

    ## Open User's Plist Data
    data = open('/var/db/dslocal/nodes/Default/users/%s.plist' % username, 'r')

    ## Read and buffer the user's Plist Data
    plistData = buffer(data.read())
    data.close

    ## Convert the Plist Data into a Dictionary
    (userPlist, _, _) = (
    NSPropertyListSerialization.propertyListWithData_options_format_error_(plistData, NSPropertyListXMLFormat_v1_0,
                                                                           None, None))

    ## Read and buffer the new ShadowHashData
    userShadowHashData = buffer(userHash.decode('hex'))

    ## Convert the ShadowHashData into a Dictionary
    (userShadowHashPlist, _, _) = (
    NSPropertyListSerialization.propertyListWithData_options_format_error_(userShadowHashData,
                                                                           NSPropertyListXMLFormat_v1_0, None, None))

    ## Remove unsecured hash types
    del userShadowHashPlist['CRAM-MD5']
    del userShadowHashPlist['NT']

    ## Convert the ShadowHashData back to data
    (userShadowHashData, _) = (
    NSPropertyListSerialization.dataWithPropertyList_format_options_error_(userShadowHashPlist,
                                                                           NSPropertyListBinaryFormat_v1_0, 0, None))

    ## Insert the new ShadowHashData into the User's Plist Dictionary
    userPlist['ShadowHashData'][0] = userShadowHashData

    ## Convert the UserPlist back to data
    (plistData, _) = (
    NSPropertyListSerialization.dataWithPropertyList_format_options_error_(userPlist, NSPropertyListBinaryFormat_v1_0,
                                                                           0, None))

    ## Write user's updated plist to disk
    stream = io.open('/var/db/dslocal/nodes/Default/users/%s.plist' % username, 'bw')
    stream.write(plistData)
    stream.close

    bashCommand(['dscacheutil', '-flushcache'])
    time.sleep(2)


def nameMachine(computerNamePrefix, assetTag):
    global machineName
    machineName = computerNamePrefix + assetTag + 'MAC' + lapOrDesk()
    for e in ('ComputerName', 'LocalHostName', 'HostName'):
        bashCommand(["/usr/sbin/scutil", "--set", e, machineName])
    logging.debug("[+] Complete. Machine is now named [%s]" % machineName)


def lapOrDesk():
    command = '/usr/sbin/system_profiler SPHardwareDataType | grep "Model Identifier" | grep -i "Book"'
    event = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    output = event.communicate()
    if 'Book' in output[0]:
        return 'LT'
    else:
        return 'DT'


def shareSettings(admins):
    kickstart = "/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart"
    for e in admins:
        bashCommand([kickstart, "-activate", "-configure", "-access", "-on", "-users", e['ShortName'], "-privs", "-all",
                     "-restart", "-agent", "-menu"])
        bashCommand([kickstart, "-configure", "-allowAccessFor", "-specifiedUsers"])
    bashCommand(["/usr/sbin/systemsetup", "-setremotelogin", "on"])
    bashCommand(["/usr/sbin/dseditgroup", "-o", "create", "-q", "com.apple.access_ssh"])
    bashCommand(["/usr/sbin/dseditgroup", "-o", "edit", "-a", "admin", "-t", "group", "com.apple.access_ssh"])
    bashCommand(["/usr/sbin/dseditgroup", "-o", "edit", "-a", "powerusers", "-t", "group", "com.apple.access_ssh"])


def findOpenUniqueID():
    uids = []
    users = bashCommand(["/usr/bin/dscl", ".", "-list", "/Users"]).split("\n")
    for e in users:
        if '_' in e or 'netboot' in e or e == '':
            del users[users.index(e)]
    for e in users:
        uid_temp = bashCommand(["/usr/bin/dscl", ".", "-read", "/Users/%s" % e, "UniqueID"])
        uid_temp = uid_temp.replace("UniqueID: ", "").replace("\n", "")
        try:
            uid_temp = int(uid_temp)
        except:
            uid_temp = 0
        uids.append(uid_temp)
    uids = sorted(uids)
    open_UID = 501
    while True:
        if open_UID in uids:
            open_UID = open_UID + 1
        else:
            break
    return open_UID


def abMan(resource, location, groupName):
    plist = plistlib.readPlist(resource + '/DefaultDefaults.plist')
    plist['UserInfo1'] = location
    plist['UserInfo3'] = groupName
    plistlib.writePlist(plist, resource + '/DefaultDefaults.plist')
    bashCommand([resource + "/InstallAgent.sh"])

def fdeStatus():
    return bashCommand(['/usr/bin/fdesetup', 'status'])

def cleanUp():
    logging.debug("[+] Remove Config and Install Files")
    ## Remove Config and Install Files
    bashCommand(['/bin/rm', '-r', '-f', '/var/tmp/OnSet/'])

    logging.debug("[+] Remove LoginLog App")
    ## Remove LoginLog App
    bashCommand(['/bin/rm', '-r', '-f', '/Library/PrivilegedHelperTools/LoginLog.app'])

    ## Unload Launch Agent
    bashCommand(['/bin/launchctl', 'unload', '-S', 'loginwindow', '/Library/LaunchAgents/com.github.jbaker10.LoginLog.plist'])

    ## Remove Launch Agents and Daemons
    bashCommand(['/bin/rm', '-r', '-f', '/Library/LaunchAgents/com.github.jbaker10.LoginLog.plist'])
    bashCommand(['/bin/rm', '-r', '-f', '/Library/LaunchDaemons/com.github.jbaker10.OnSet.plist'])

    # logging.debug("*** Reload the LoginWindow ***")
    # ## Reload the LoginWindow
    # bashCommand(['/bin/launchctl', 'unload', '/System/Library/LaunchDaemons/com.apple.loginwindow.plist'])
    # bashCommand(['/bin/launchctl', 'load', '/System/Library/LaunchDaemons/com.apple.loginwindow.plist'])
    
    ## With the introduction of SIP, the unload and reload of the loginwindow stopped working. Therefore we are manually killing it"
    logging.debug("*** Reload the LoginWindow FORCEFULLY***")
    
    p = subprocess.Popen(['ps', '-a', '-x'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    for line in out.splitlines():
        if 'loginwindow console' in line:
            pid = int(line.split(None, 1)[0])
            os.kill(pid, signal.SIGKILL)

    bashCommand(['/bin/rm', '-r', '-f', '/Library/PrivilegedHelperTools/OnSet.py'])


def bashCommand(script):
    try:
        return subprocess.check_output(script)
    except (subprocess.CalledProcessError, OSError), err:
        return "[* Error] **%s** [%s]" % (err, str(script))


def main():
    logging.basicConfig(filename='/var/log/com.github.jbaker10.onset.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', encoding="UTF-8")
    logging.debug("=" * 10 + "[+] Starting OnSet v2.0.7 [+]" + "=" * 10)
    logging.debug("[+] Importing configuration plist")
    try:
        plistPath = "/private/var/tmp/OnSet/com.onset.plist"
        plist = plistlib.readPlist(plistPath)
        assetTag = plist["AssetTag"]
        location = plist["Location"]
        resource = "/private/var/tmp/OnSet/LANrev Agent Installer"
        groupName = plist["GroupName"]
        admins = plist["Admins"]
        language = plist["Language"]
        timeZone = plist["TimeZone"]
        computerNamePrefix = plist["ComputerNamePrefix"]
        logging.debug("[+] Plist Parsed")
    except (KeyError, IOError):
        logging.debug("[*] Error with parsing plist. Please re-run the LiteTouch or Contact IT")
        logging.debug("=" * 10 + "[-] Exiting OnSet [-]" + "=" * 10)
        sys.exit(1)

    logging.debug("[+] Setting Language to: %s" % language)
    bashCommand(['/usr/sbin/languagesetup', '-langspec', language])

    logging.debug("[+] Setting TimeZone to: %s" % timeZone)
    bashCommand(['/usr/sbin/systemsetup', '-settimezone', timeZone])

    logging.debug("[+] Setting Machine Name")
    nameMachine(computerNamePrefix, assetTag)
    plist["NameIsDone"] = "true"
    plistlib.writePlist(plist, plistPath)

    logging.debug("[+] Creating Defined Users")
    for e in admins:
        create_user(e["ShortName"], e["RealName"], e["Hash"], e["Picture"])
        logging.debug("[+] Created user [%s]" % e["RealName"])
    plist["UserIsDone"] = "true"
    plistlib.writePlist(plist, plistPath)

    logging.debug("[+] Setting SSH and ARD access")
    shareSettings(admins)
    plist["RemoteIsDone"] = "true"
    plistlib.writePlist(plist, plistPath)

    logging.debug("[+] Enrolling Machine into Absolute Manage")
    abMan(resource, location, groupName)
    bashCommand(['/Library/Scripts/amkickstart.sh'])
    plist["AbmanIsDone"] = "true"
    plistlib.writePlist(plist, plistPath)

    sendEmail([EMAIL_ADDRESS], plist)
    logging.debug("[+] Done. Cleaning Up")
    cleanUp()

if __name__ == "__main__":
    main()