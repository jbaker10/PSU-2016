#!/bin/sh

#echo "Installing LANrev Agent";

MYPATH="`dirname "${0}"`"

LinuxInstall() {
	if [ ! -e "${MYPATH}/LANrev Agent (Linux).lmp" ]; then
		echo "Missing Linux installer package file" >&2
		exit 1
    fi

	STATUS_FILE="/tmp/amlcd_status"

	if [ -f "${MYPATH}/LANrev Agent (Linux).lmp" ] && \
		 [ -d "${MYPATH}/Certificates" ] && \
		 [ -f "${MYPATH}/DefaultDefaults.plist" ]; then
		    tar -C "${MYPATH}" -zxvf "${MYPATH}/LANrev Agent (Linux).lmp" amlcd-installer.sh
			/bin/sh "${MYPATH}/amlcd-installer.sh" -- -c "${MYPATH}/Certificates" -d "${MYPATH}/DefaultDefaults.plist"
			rm -f "${MYPATH}/amlcd-installer.sh"
	fi

	if [ "`cat ${STATUS_FILE}`" != "installed"  ] ; then
			rm -f ${STATUS_FILE}
			exit 1
	fi

	rm -f ${STATUS_FILE}
}

MacOSXInstall() {
	if [ ! -e "${MYPATH}/LANrev Agent.pkg" ]; then
		echo "Missing Mac installer package file" >&2
		exit 1
	fi
	if [ -f "${MYPATH}/LANrev Agent.pkg" ]; then
		# flat installers will only work on Mac OS X 10.5 and up
		MINOR_OS_VERSION=`/usr/bin/sw_vers | /usr/bin/sed -n -e '/^ProductVersion:/s/ProductVersion:[[:space:]][0-9][0-9]*\.\([0-9][0-9]*\).*/\1/p'`
		if [ "${MINOR_OS_VERSION}" -lt 5 ]; then
			echo "Flat installers are not supported on this version of Mac OS X ($(/usr/bin/sw_vers | /usr/bin/sed -n -e '/^ProductVersion:/s/ProductVersion:[[:space:]]*\(.*\)/\1/p'))" >&2
			exit 1
		fi
	fi
	/usr/sbin/installer -pkg "${MYPATH}/LANrev Agent.pkg" -target /
}



PLATFORM=$("${MYPATH}/DetermineDeploymentPlatform.sh" -s)

echo "Determined platform to be ${PLATFORM}"
case ${PLATFORM} in
	"Mac OS X")
		MacOSXInstall
		;;
	Linux|Ubuntu*|Debian*)
		LinuxInstall
		;;
	*)
		echo "unsupported platform ${PLATFORM}" >&2
		exit 1;;
esac
