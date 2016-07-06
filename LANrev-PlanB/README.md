Overview
========

Plan B is a remediation program for managed Macs. It is meant to be run to re-install other management software.

Features
------

  - Secure download of disk images from an Internet-facing server.
  - Installation of package files contained on the disk images.
  - Validation of server certificate against explicitly trusted certificate authorities only.
  - Support for client certificate authentication to ensure only trusted clients can access the server.
  - URL construction to download packages based on a client's configuration in a plist.
  - Extensive logging of presented certificate details for auditing and MITM detection.
  - No external dependencies; the compiled program is tiny and can be easily deployed.

AbMan Health Check Script
------

The `abman_health_check` script is a python script that is meant to keep your Absolute Manage agents in tip-top shape. It will perform the following functions:

  - Check to make sure that the core parts of the AbMan agent are installed. This includes:
    - The LANrev folder under `/Library/Application Support/LANrev Agent/`
    - The LANrev binary under `/Library/Application Support/LANrev Agent/LANrev Agent.app/Contents/MacOS/LANrev Agent`
    - The LANrev On-Demand .netloc under `/Applications/Absolute On-demand Software.inetloc`
  - Parse the previous day's logs looking for errors. The current function searches for the following errors:
    - "WARNING: Absolute Manage Agent code signature not valid: /Library/Application Support/LANrev Agent/LANrev Agent.app"
  - Checks to make sure the Apple Software Update check run via AbMan is working properly
  - Checks the installed Agent version to ensure it is up to date. This variable is defined within the script under the variable name `LANrev_agent_vers` and can be updated as needed
  - Pulls a known-good `DefaultDefaults.plist` from a web server, and compares defined values on the agent with the known-good prefs, to ensure it is as intended

If any of the above conditions (with the exclusion of the `DefaultDefaults.plist` check, which I will discuss below) are true, the script will send en email to the defined recipient within the script including the following information:

  - The Hostname of the machine `planb` was triggered on
  - The time that `planb` was triggered
  - The error which caused `planb` to be triggered

It will appear as so:

![planb email](https://github.nimh.nih.gov/github-enterprise-assets/0000/0008/0000/0039/617a1694-a411-11e5-940b-4dd82bcf5350.png)

Deployment
----------

We have packaged the planb binary, a Absolute Manage health check script, and a LaunchDaemon that will run the health check script ever 24 hours, for easy deployment. Both the planb binary and the helath check script, abman_health_check are placed in /usr/local/sbin/ The LaunchDaemon that runs the script is placed in /Library/LaunchDaemons/ with the name gov.nih.nimh.planb.plist
