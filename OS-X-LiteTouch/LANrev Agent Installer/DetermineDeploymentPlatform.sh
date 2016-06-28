#!/bin/bash

PLATFORM="<<unknown>>"
UNAME=$(uname)

case "${UNAME}" in
	Linux)
		PLATFORM=Linux
#		if [ -x /bin/sed ]; then SED=/bin/sed; else SED=/usr/bin/sed; fi
#		if [ -f /etc/lsb-release ]; then
#			PLATFORM=$(${SED} -n -e '/^DISTRIB_ID=/{s/DISTRIB_ID=\(.*\)/\1/;p;}' /etc/lsb-release) &&
#			ARCH=$(uname -m) &&
#			case "${ARCH}" in
#				i386|i686) ARCH=32bit;;
#				x86_64) ARCH=64bit;;
#				*) echo "unsupported hardware platform">&2; exit 1;;
#			esac &&
#			PLATFORM="${PLATFORM} [${ARCH}]"
#		else
#			echo "unsupported Linux platform" >&2
#			exit 1
#		fi
		;;
	Darwin)
		PLATFORM=$(/usr/bin/sw_vers -productName | /usr/bin/sed 's/^Mac OS X.*/Mac OS X/')
		;;
esac

if [ $? -ne 0 ]; then
	echo "could not determine OS platform" >&2
	exit 1
fi

if [ "${1}" == "-s" ]; then
	echo -n "${PLATFORM}"
else
	echo "PPS_PLATFORM=${PLATFORM}"
fi
