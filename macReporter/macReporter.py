#!/usr/local/bin/python


"""\nUsage: notManaged [OPTION ...] [EMAIL_ADDRESS1 EMAIL_ADDRESS2 ...]
Run reports to get the number of unmanaged machines, as well as the information about
those machines, including, but not limited to: Serial Number, Accountable User, Decal Number.

Options:
-h, --help                  Display this message
-e, --email-report          Email yourself a report of currently unmanaged machines (requires an email input)
-u, --unmanaged-notice      Send unmanaged machine notice email to all accountable customers
-o, --offline-notice        Send 90 day notice email to all accountable customers
-c, --csv                   Output in comma-separated format. If used with -e, CSV will be attached to email
-n, --no-interaction        Proceed without prompting for which report to run. Defaults to running both reports

Example usage:
Send someone the Unmanaged report:           notManaged.py -e user@email.com
Send multiple emails the report:             notmanaged.py -e user@email.com user2@email.com user3@email.com
Send Unmanaged report to accountable user:   notManaged.py -u
All options with mixed syntax:               notManaged.py --csv -u --offline-notice -e user@email.com
"""


import os
import cx_Oracle
import datetime
import xml.etree.ElementTree as ET
import urllib2
import smtplib
import csv
import sys
import getopt
import time
from string import Template
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

#########################################

# Build connection string
pswd = "" ## Password to authenticate to DB with
user = "" ## Username to authenticate to DB with
host = "" ## Hostname to server hosting DB
port = "" ## Port to connect to DB over
sn = "" ## Schema Name in the DB

heartbeatDays = 90
dt = datetime.datetime.now() - datetime.timedelta(days=heartbeatDays)
heartbeatThreshhold = datetime.date(dt.year, dt.month, dt.day)

dsn = cx_Oracle.makedsn(host, port, sn)
con = cx_Oracle.connect(user, pswd, dsn)
allApples = []
missingLANrev = []
over90Days = []
invalidSerialNumbers = []
validSerials = []
waivedMachines = []
finalOver90Days = []

ADMIN_EMAIL = '' ## Fill this in with an email that reports should default to being sent to

#########################################

nonMacModels = () ## can fill this list in with non-Mac models for filtering

def sendUnmanagedEmail(addresses,machineDict):
    
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
        max-width: 600px!important;
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
              <h1><b>SECOND NOTICE</b></h1>
              <p>Greetings:</p>
              <p>The computer listed below has not yet been enrolled in the COMPANY patch management system. <b><i>You are listed in the property database as the Accountable User.</i></b>
              <p>If the machine is not enrolled in LANrev, an IT ticket will automatically be created and a technician will come to assist with the enrollment.</p>
              <p>If you are not the current user of this Mac, contact the Property Team at <a href=mailto:property@domain.com>property@domain.com</a> to have the property record updated with the correct information.</p>
              <p>If you do not have access to this Mac (because you are offsite, or the computer is not accessible), please notify <a href=mailto:security@domain.com>security@domain.com</a> and we will work with you to locate it.
              <h2>Having trouble?</h2>
              <p>Contact the Help Desk at 123-GET-HELP for assistance with any issues or problems.</p>
              <p>&nbsp</p>
              <p>Best Regards,</p>
              <p><b>Property and Security Offices</b></p>
              <p></p>
            </td>
          </tr>
        </table>
        </div>
        <!-- /content -->
        <div class="ToadExtensionTableContainer">
        <table class="ToadExtensionTable">
        <tr>
        <th class="HeaderColumnEven">SERIAL_NUMBER</th>
        <th class="HeaderColumnOdd">MANUFACTURER</th>
        <th class="HeaderColumnEven">MODEL</th>
        <th class="HeaderColumnOdd">ASSET_IDENTIFIER</th>
        <th class="HeaderColumnEven">ACCOUNTABLE_USER</th>
        <th class="HeaderColumnOdd">PERSON_ORGANIZATION</th>
        <th class="HeaderColumnEven">PERSON_ORGANIZATION_CODE</th>
        <th class="HeaderColumnOdd">CURRENT_ORGANIZATION</th>
        <th class="HeaderColumnEven">ACQUISITION_DATE</th>
        <th class="HeaderColumnOdd">RESPONSIBILITY_BEGIN_DATE</th>
        <th class="HeaderColumnEven">ACTIVITY_STATUS</th>
        <th class="HeaderColumnOdd">CUSTODIAL_CODE</th>
        <th class="HeaderColumnEven">SYSTEM_NAME</th>
        <th class="HeaderColumnOdd">FREQUENT_USER</th>
        <th class="HeaderColumnEven">WINDOWS_DIRECTORY</th>
        <th class="HeaderColumnOdd">OS</th>
        <th class="HeaderColumnEven">SERVICE_PACK</th>
        <th class="HeaderColumnOdd">LAST_LOGIN_TIME</th>
        <th class="HeaderColumnEven">LAST_LOGIN_USER</th>
        </tr>
    '''

    values = '''      <tr>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          </tr>
        </td>
      </tr>
    </table>
    <!-- /body -->
    </body>
    </html>''' % (  machineDict["SERIAL_NUMBER"], \
                    machineDict["MANUFACTURER"], \
                    machineDict["MODEL"], \
                    machineDict["ASSET_IDENTIFIER"], \
                    machineDict["ACCOUNTABLE_USER"], \
                    machineDict["PERSON_ORGANIZATION"], \
                    machineDict["PERSON_ORGANIZATION_CODE"], \
                    machineDict["CURRENT_ORGANIZATION"], \
                    machineDict["ACQUISITION_DATE"], \
                    machineDict["RESPONSIBILITY_BEGIN_DATE"], \
                    machineDict["ACTIVITY_STATUS"], \
                    machineDict["CUSTODIAL_CODE"], \
                    machineDict["SYSTEM_NAME"], \
                    machineDict["FREQUENT_USER"], \
                    machineDict["WINDOWS_DIRECTORY"], \
                    machineDict["SERVICE_PACK"], \
                    machineDict["OS"], \
                    machineDict["LAST_LOGIN_TIME"], \
                    machineDict["LAST_LOGIN_USER"], )

    htmlEmail = htmlEmail + values
    customerEmail = [addresses]
    CCAddress = [''] ## need an email here
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Property: Missing from Computer Management'
    msg['From'] = '' ## need an email here
    msg['To'] = customerEmail[0]
    msg['Cc'] = CCAddress[0]

    text = "Property: Missing from Computer Management" % machineDict

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

    print customerEmail
    print CCAddress
    s = smtplib.SMTP('') ## Add a forwarding mail server
    s.sendmail(addresses, customerEmail+CCAddress, msg.as_string())
    s.quit()

def sendNinetyDayEmail(addresses, machineDict):

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
      max-width: 600px!important;
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
      <tr>
        <td class="container" bgcolor="#FFFFFF">

          <!-- content -->
          <div class="content">
          <table>
            <tr>
              <td>
                <h1>Mac Offline for 90+ Days</h1>
                <p>Greetings:</p>
                <p>The computer listed below has not come online in over 90 days. <b><i>You are listed in the property database as the Accountable User.</i></b> In the next 7 calendar days, please take the time to power on your Mac and connect it to the internet.  (You are not required to connect to VPN.)</p> 
                <p>If you do not, the equipment will be reported as missing/stolen.</p>
                <p>If you are not the current user of this Mac, contact the Property Team to have the property record updated with the correct information.</p>
                <p>If you do not have access to this Mac (because you are offsite, or the computer is not accessible), please notify us and we will work with you to locate it.
                <h2>Having trouble?</h2>
                <p>Contact the Help Desk at 123-GET-HELP for assistance with any issues or problems.</p>
                <p>&nbsp</p>
                <p>Thank you for your prompt attention to this matter!</p>
                <p><b>Property and Security Offices</b></p>
                <p></p>
              </td>
            </tr>
          </table>
          </div>
          <!-- /content -->
        <div class="ToadExtensionTableContainer">
          <table class="ToadExtensionTable">
          <tr>
          <th class="HeaderColumnEven">SERIAL_NUMBER</th>
          <th class="HeaderColumnOdd">MANUFACTURER</th>
          <th class="HeaderColumnEven">MODEL</th>
          <th class="HeaderColumnOdd">ASSET_IDENTIFIER</th>
          <th class="HeaderColumnEven">ACCOUNTABLE_USER</th>
          <th class="HeaderColumnOdd">PERSON_ORGANIZATION</th>
          <th class="HeaderColumnEven">PERSON_ORGANIZATION_CODE</th>
          <th class="HeaderColumnOdd">CURRENT_ORGANIZATION</th>
          <th class="HeaderColumnEven">ACQUISITION_DATE</th>
          <th class="HeaderColumnOdd">RESPONSIBILITY_BEGIN_DATE</th>
          <th class="HeaderColumnEven">ACTIVITY_STATUS</th>
          <th class="HeaderColumnOdd">CUSTODIAL_CODE</th>
          <th class="HeaderColumnEven">SYSTEM_NAME</th>
          <th class="HeaderColumnOdd">FREQUENT_USER</th>
          <th class="HeaderColumnEven">WINDOWS_DIRECTORY</th>
          <th class="HeaderColumnOdd">OS</th>
          <th class="HeaderColumnEven">SERVICE_PACK</th>
          <th class="HeaderColumnOdd">LAST_LOGIN_TIME</th>
          <th class="HeaderColumnEven">LAST_LOGIN_USER</th>
          </tr>
    '''

    values = '''      <tr>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          </tr>
        </td>
      </tr>
    </table>
    <!-- /body -->
    </body>
    </html>''' % (  machineDict["SERIAL_NUMBER"], \
                    machineDict["MANUFACTURER"], \
                    machineDict["MODEL"], \
                    machineDict["ASSET_IDENTIFIER"], \
                    machineDict["ACCOUNTABLE_USER"], \
                    machineDict["PERSON_ORGANIZATION"], \
                    machineDict["PERSON_ORGANIZATION_CODE"], \
                    machineDict["CURRENT_ORGANIZATION"], \
                    machineDict["ACQUISITION_DATE"], \
                    machineDict["RESPONSIBILITY_BEGIN_DATE"], \
                    machineDict["ACTIVITY_STATUS"], \
                    machineDict["CUSTODIAL_CODE"], \
                    machineDict["SYSTEM_NAME"], \
                    machineDict["FREQUENT_USER"], \
                    machineDict["WINDOWS_DIRECTORY"], \
                    machineDict["SERVICE_PACK"], \
                    machineDict["OS"], \
                    machineDict["LAST_LOGIN_TIME"], \
                    machineDict["LAST_LOGIN_USER"], )
    
    htmlEmail = htmlEmail + values
    customerEmail = [addresses]
    CCAddress = [''] ## need an email here
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Property: Not Seen in 90 days'
    msg['From'] = '' ## need an email here
    msg['To'] = customerEmail[0]
    msg['Cc'] = CCAddress[0]

    text = "Property: Not seen in 90 days" % machineDict

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

    print customerEmail
    print CCAddress
    s = smtplib.SMTP('') ## Add a forwarding mail server
    s.sendmail(addresses, customerEmail+CCAddress, msg.as_string())
    s.quit()

def sendUnmanagedEmailReport(addresses, machineList, csvStatus):
    numberOfMissing = len(machineList)
    htmlEmail = Template('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
              <h1>Unmanaged Computers</h1>
              <p>Greetings:</p>
              <p>There are <b>[${numberOfMissing}]</b> computers listed below that are not enrolled in LANrev.</p>
            </td>
          </tr>
        </table>
        </div>
        <!-- /content -->
        <div class="ToadExtensionTableContainer">
        <table class="ToadExtensionTable">
        <tr>
        <th class="HeaderColumnEven">SERIAL_NUMBER</th>
        <th class="HeaderColumnOdd">MANUFACTURER</th>
        <th class="HeaderColumnEven">MODEL</th>
        <th class="HeaderColumnOdd">ASSET_IDENTIFIER</th>
        <th class="HeaderColumnEven">ACCOUNTABLE_USER</th>
        <th class="HeaderColumnOdd">PERSON_ORGANIZATION</th>
        <th class="HeaderColumnEven">PERSON_ORGANIZATION_CODE</th>
        <th class="HeaderColumnOdd">CURRENT_ORGANIZATION</th>
        <th class="HeaderColumnEven">ACQUISITION_DATE</th>
        <th class="HeaderColumnOdd">RESPONSIBILITY_BEGIN_DATE</th>
        <th class="HeaderColumnEven">ACTIVITY_STATUS</th>
        <th class="HeaderColumnOdd">CUSTODIAL_CODE</th>
        <th class="HeaderColumnEven">SYSTEM_NAME</th>
        </tr>
    ''').substitute(numberOfMissing=numberOfMissing)
    index = 0
    values = ""
    for machine in machineList:
    	values += '''      <tr>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          </tr>
        </td>
      </tr>\n''' % ( machineList[index]["SERIAL_NUMBER"], \
                    machineList[index]["MANUFACTURER"], \
                    machineList[index]["MODEL"], \
                    machineList[index]["ASSET_IDENTIFIER"], \
                    machineList[index]["ACCOUNTABLE_USER"], \
                    machineList[index]["PERSON_ORGANIZATION"], \
                    machineList[index]["PERSON_ORGANIZATION_CODE"], \
                    machineList[index]["CURRENT_ORGANIZATION"], \
                    machineList[index]["ACQUISITION_DATE"], \
                    machineList[index]["RESPONSIBILITY_BEGIN_DATE"], \
                    machineList[index]["ACTIVITY_STATUS"], \
                    machineList[index]["CUSTODIAL_CODE"], \
                    machineList[index]["SYSTEM_NAME"] )
        index += 1 
    '''
    </table>
    <!-- /body -->
    </body>
    </html>'''

    htmlEmail = htmlEmail + values
    #htmlEmail = htmlEmail + str(machineList)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Property: Missing from Computer Management'
    msg['From'] = '' ## Need email address here
    msg['To'] = addresses[0]

    text = "Property: Missing from Computer Management"

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(htmlEmail, 'html')
    if csvStatus is True:
        part3 = MIMEApplication(open("missing.csv", "rb").read())
        part3.add_header('Content-Disposition', 'attachment', filename="missing.csv")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    if csvStatus is True:
        msg.attach(part3)

    s = smtplib.SMTP('') ## Need a forwarding mail server here
    s.sendmail(addresses[0], addresses, msg.as_string())
    s.quit()

def send90DayEmailReport(addresses, machineList, csvStatus):
    numberOf90Day = len(machineList)
    htmlEmail = Template('''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
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
              <h1>90 Day Computers</h1>
              <p>Greetings:</p>
              <p>There are <b>[${numberOf90Day}]</b> computers listed below that have a heartbeat greater than 90 days.</p>
            </td>
          </tr>
        </table>
        </div>
        <!-- /content -->
        <div class="ToadExtensionTableContainer">
        <table class="ToadExtensionTable">
        <tr>
        <th class="HeaderColumnEven">SERIAL_NUMBER</th>
        <th class="HeaderColumnOdd">MANUFACTURER</th>
        <th class="HeaderColumnEven">MODEL</th>
        <th class="HeaderColumnOdd">ASSET_IDENTIFIER</th>
        <th class="HeaderColumnEven">ACCOUNTABLE_USER</th>
        <th class="HeaderColumnOdd">PERSON_ORGANIZATION</th>
        <th class="HeaderColumnEven">PERSON_ORGANIZATION_CODE</th>
        <th class="HeaderColumnOdd">CURRENT_ORGANIZATION</th>
        <th class="HeaderColumnEven">ACQUISITION_DATE</th>
        <th class="HeaderColumnOdd">RESPONSIBILITY_BEGIN_DATE</th>
        <th class="HeaderColumnEven">ACTIVITY_STATUS</th>
        <th class="HeaderColumnOdd">CUSTODIAL_CODE</th>
        <th class="HeaderColumnEven">SYSTEM_NAME</th>
        </tr>
    ''').substitute(numberOf90Day=numberOf90Day)
    index = 0
    values = ""
    for machine in machineList:
        values += '''      <tr>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          <td class="R0C1">%s</td>
          <td class="R0C0">%s</td>
          </tr>
        </td>
      </tr>\n''' % ( machineList[index]["SERIAL_NUMBER"], \
                    machineList[index]["MANUFACTURER"], \
                    machineList[index]["MODEL"], \
                    machineList[index]["ASSET_IDENTIFIER"], \
                    machineList[index]["ACCOUNTABLE_USER"], \
                    machineList[index]["PERSON_ORGANIZATION"], \
                    machineList[index]["PERSON_ORGANIZATION_CODE"], \
                    machineList[index]["CURRENT_ORGANIZATION"], \
                    machineList[index]["ACQUISITION_DATE"], \
                    machineList[index]["RESPONSIBILITY_BEGIN_DATE"], \
                    machineList[index]["ACTIVITY_STATUS"], \
                    machineList[index]["CUSTODIAL_CODE"], \
                    machineList[index]["SYSTEM_NAME"] )
        index += 1
    
    '''
    </table>
    <!-- /body -->
    </body>
    </html>'''

    htmlEmail = htmlEmail + values
    #htmlEmail = htmlEmail + str(machineList)
    msg = MIMEMultipart('alternative')
    msg['Subject'] = 'Property: Macs Not Seen in Over 90 days'
    msg['From'] = '' ## Need an email address here
    msg['To'] = addresses[0]

    text = "Property: Macs Not Seen in Over 90 days"

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(htmlEmail, 'html')
    if csvStatus is True:
        part3 = MIMEApplication(open("90day.csv", "rb").read())
        part3.add_header('Content-Disposition', 'attachment', filename="90day.csv")

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    if csvStatus is True:
        msg.attach(part3)

    s = smtplib.SMTP('') ## Need a forwarding mail server here
    s.sendmail(addresses[0], addresses, msg.as_string())
    s.quit()

def usage():
    print __doc__
    sys.exit()

def makeDictFactory(cursor):
    columnNames = [d[0] for d in cursor.description]
    def createRow(*args):
        return dict(zip(columnNames, args))
    return createRow

def getLoanStatus():
    for machine in allApples[:]:
        if machine["ACTIVITY_STATUS"] == "ON LOAN":
            allApples.remove(machine)
    print "After ON LOAN check: %i" % len(allApples)

def getWaivedComputers():
    for machine in allApples[:]:
        if machine["WAIVER_STATUS"] == "Y":
            allApples.remove(machine)
            waivedMachines.append(machine)
    print "After WAIVER STATUS check: %i" % len(allApples)
    print "Total number of waived machines: %i" % len(waivedMachines)

def checkSerialValidity(serialNumber):
    global serialCheck
    serialCheck = None
    productIDNumber = None
    if len(serialNumber) > 11:
        productIDNumber = serialNumber[-4:]
    else:
        productIDNumber = serialNumber[-3:]

    response = urllib2.urlopen('http://support-sp.apple.com/sp/product?cc=%s' % productIDNumber)
    tree = ET.fromstring(response.read())
    try:
        configCode = None
        for e in tree.getchildren():
            if e.tag == "configCode":
                configCode = e.text
        if configCode == None:
            serialCheck = "Invalid"
	    invalidSerialNumbers.append(machine)
        elif "Mac" not in configCode:
            serialCheck = "Invalid"
    except:
        pass
 #   print "After SERIAL NUMBER check: %i" % len(usableList)

def getUnmanagedMachines():
    for machine in allApples[:]:
        try:
            if machine["SYSTEM_NAME"] is None:
                # print machine["ASSET_IDENTIFIER"]
                # print machine["SERIAL_NUMBER"]
                checkSerialValidity(str(machine["SERIAL_NUMBER"]))
                if serialCheck is not None:
                    pass
		 #   print "Invalid or non-Mac serial"
                else:
                    missingLANrev.append(machine)
                    allApples.remove(machine)
        except:
            pass
    print "Total number of remaining managed Apple machines: %i" % len(allApples)
    print "Found [%s] Apple Devices that need LANrev" % len(missingLANrev)

def writeDictToCSV(csv_file,csv_columns,applicableList):
    fname = "/scripts/All-Apples/missing.csv"
    ninetyfname = "/scripts/All-Apples/90day.csv"
    if csv_file == "missing.csv":
        if os.path.isfile(fname):
            os.remove(fname)
    elif csv_file == "90day.csv":
        if os.path.isfile(ninetyfname):
            os.remove(ninetyfname)

    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in applicableList:
                writer.writerow(data)
    except IOError as (errno, strerror):
        print("I/O error({0}): {1}".format(errno, strerror))
    return

def getNinetyDay():
    for machine in allApples[:]:
        try:
            if machine["LAST_LOGIN_TIME"] == None:
                allApples.remove(machine)
                continue
            hb = machine["LAST_LOGIN_TIME"].date()
            heartBeat = datetime.date(hb.year, hb.month, hb.day)
            if heartBeat <= heartbeatThreshhold:
                checkSerialValidity(str(machine["SERIAL_NUMBER"]))
                if checkSerialValidity == "Invalid":
                    pass
                else:
                    over90Days.append(machine)
                    continue
        except TypeError:
            pass

    for machine in over90Days:
        try:
            if machine["ASSET_STATUS"] == None:
                finalOver90Days.append(machine)
        except TypeError:
            pass

    if len(finalOver90Days) == 0:
        print "All Apple Devices have reported in."
    else:
        print "Found [%s] Apple Devices that have a heartbeat " \
              "greater than [%i]" % (len(finalOver90Days), heartbeatDays)


csv_columns = ['COMMUNICATION_TIME', 'FREQ_USER_FIRST_NAME', \
                       'PERSON_ORGANIZATION_CODE', 'CLIENT_STATUS', \
                       'ASSET_IDENTIFIER', 'LAST_LOGIN_USER', \
                       'FREQ_USER_LAN_ID', 'MODEL', 'LAST_LOGIN_TIME', \
                       'ASSET_STATUS', 'RESPONSIBILITY_BEGIN_DATE', \
                       'ACQUISITION_DATE', 'CURRENT_ORGANIZATION', \
                       'WINDOWS_DIRECTORY', 'HHS_ID', 'ACTIVITY_STATUS', \
                       'FREQUENT_USER', 'EMAIL_ADDRESS', 'MANUFACTURER', \
                       'SYSTEM_NAME', 'FREQ_USER_ADDR_TEXT', 'CUSTODIAL_CODE', \
                       'HEARTBEAT_TIME', 'SERVICE_PACK', 'FREQ_USER_LAST_NAME', \
                       'ACCOUNTABLE_USER', 'PERSON_ORGANIZATION', \
                       'SERIAL_NUMBER', 'OS', 'WAIVER_STATUS']
csv_file_missing = "missing.csv"

csv_file_ninety = "90day.csv"


def main():
    sendReport = False
    sendCustomerUnmanagedNotice = False
    generateCSV = False
    sendCustomerNinetyDayNotice = False
    attachCSV = False
    noInteraction = False
    reportOptions = (1, 2, 3)
    emailAddresses = []
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hnuoce:", ["help", \
                                                           "no-interaction", \
                                                           "unmanaged-notice", \
                                                           "offline-notice", \
                                                           "csv", \
                                                           "email"])
        if len(opts) == 0:
            usage()
    except getopt.GetoptError, err:
        print str(err)
        usage()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
        if opt in ("-n", "--no-interaction"):
            noInteraction = True
        if opt in ("-e", "--email"):
            if len(arg) == 0:
                print "This flag requires an email to added"
                usage()
            elif noInteraction is True:
                reportType = 3
            else:
                reportType = raw_input("\nPlease enter which the corresponding number " \
                                        "for the type of report you would like to generate. " \
                                        "Options are: 90-day [1], Unmanaged [2], or Both [3]: ")
                if len(reportType) == 0:
                    print "\nPlease enter an integer (1, 2, or 3) corresponding to the report type"
                    print "\nExiting"
                    sys.exit()
                reportType = int(reportType)
                if reportType not in reportOptions:
                    print "\nPlease enter an integer (1, 2, or 3) corresponding to the report type"
                    print "\nExiting"
                    sys.exit()
                print ""
                sendReport = True
                emailAddress = arg
        if opt in ("-u", "--unmanaged-notice"):
            sendCustomerUnmanagedNotice = True
        if opt in ("-o", "--offline-notice"):
            sendCustomerNinetyDayNotice = True
        if opt in ("-c", "--csv"):
            generateCSV = True
        if opt in ("-n", "--no-interaction"):
            noInteraction = True

    if sendReport is True:
        if generateCSV is True:
            print "Attaching CSV to emailed report"
            attachCSV = True
    # Whatever args remain, consider as emails
    emailAddresses = args

    if (con):
        cursor = con.cursor()
        cursor.execute("SELECT * FROM AMR.ASSET_VW WHERE MANUFACTURER='APPLE COMPUTER INC (DBA APPLE)'")
        cursor.rowfactory = makeDictFactory(cursor)
        global allApples
        allApples = cursor.fetchall()
        print "Starting number: %i" %  len(allApples)
    else:
        print "No Connection"

    ## This is a new bit to filter out Apple devices
    ## that are not Macs, but iOS devices
    for machine in allApples[:]:
        if machine["MODEL"] in nonMacModels:
            allApples.remove(machine)
    print "Number after MODEL check: [%i]" % len(allApples)

    getLoanStatus()
    getWaivedComputers()
    getUnmanagedMachines()
    getNinetyDay()


    waivedOrGoodMachines = ('') ## Can fill this in with machines that are waived from compliance

    print "Number of unmanaged machines AFTER property team pruning: %s" % len(missingLANrev)

    if sendCustomerUnmanagedNotice is True:
        index = 0
        for machine in missingLANrev:
        #    print missingLANrev[index]
            eMail = machine['EMAIL_ADDRESS']
            accountable_user = machine['ACCOUNTABLE_USER']
            #print machine['EMAIL_ADDRESS']
            print "Sending email to [%s]" % eMail 
            time.sleep(2)
            # print ""
            #if eMail not in sentAlready:
            if eMail == None:
                try:
                    sendUnmanagedEmail(ADMIN_EMAIL, missingLANrev[index])
                except:
                    print "The following email was not sent properly to user %s with serial: %s" % (eMail, machine['SERIAL_NUMBER'])
                    pass
            else:
                try:
                    sendUnmanagedEmail(eMail, missingLANrev[index])
                except:
                    print "The following email was not sent properly to user %s with serial: %s" % (eMail, machine['SERIAL_NUMBER'])
                    pass
            index += 1

    if sendCustomerNinetyDayNotice is True:
        index = 0
        for machine in finalOver90Days:
            #print finalOver90Days[index]
            eMail = machine['EMAIL_ADDRESS']
            print "Sending email to [%s]" % eMail
            time.sleep(2) 
            if eMail == None:
                try:
                    sendUnmanagedEmail(ADMIN_EMAIL, finalOver90Days[index])
                except:
                    print "The following email was not sent properly to user %s with serial: %s" % (eMail, machine['SERIAL_NUMBER'])
                    pass
            else:
                try:
                    sendUnmanagedEmail(eMail, finalOver90Days[index])
                except:
                    print "The following email was not sent properly to user %s with serial: %s" % (eMail, machine['SERIAL_NUMBER'])
                    pass

            index += 1

    ## Checks to see if the user passed in the -c flag
    if generateCSV is True:
        ## These are the unmanaged report options
        if reportType == 2 or reportType == 3:
            writeDictToCSV(csv_file_missing, csv_columns, missingLANrev)
        ## These are the 90-day report options
        if reportType == 1 or reportType == 3:
            writeDictToCSV(csv_file_ninety, csv_columns, finalOver90Days)

    ## Checks to see if we're sending an admin report (vs. customer notice), which type of report we want
    if sendReport is True:
        if reportType == 1:  ## This will send the 90-day report
            send90DayEmailReport([emailAddress], finalOver90Days, attachCSV)
            for email in emailAddresses:
                send90DayEmailReport([email], finalOver90Days, attachCSV)
        elif reportType == 2:  ## This will send the unmanaged report
            sendUnmanagedEmailReport([emailAddress], missingLANrev, attachCSV)
            for email in emailAddresses:
                sendUnmanagedEmailReport([email], missingLANrev, attachCSV)
        elif reportType == 3:  ## This will send _both_ the 90-day and unmanaged report
            send90DayEmailReport([emailAddress], finalOver90Days, attachCSV)
            sendUnmanagedEmailReport([emailAddress], missingLANrev, attachCSV)
            for email in emailAddresses:
                send90DayEmailReport([email], finalOver90Days, attachCSV)
                sendUnmanagedEmailReport([email], missingLANrev, attachCSV)
        else:
            print "\nSomething has gone wrong with the report type options. Please try again"
            print "\nExiting"

    print ""

if __name__ == "__main__":
    main()
