#!/bin/sh
# Emulate the changelog part of rpmdev-bumpspec without the bumping of the
# rev. Because Laura keeps typoing her name and the date.

CURDATE=`date +"%a %b %d %Y"`
PACKAGER=`rpmdev-packager`
CHANGELOG="%changelog\n* $CURDATE $PACKAGER\n- $1\n"

awk -v CHANGE="$CHANGELOG" '/%changelog/ {print CHANGE} \
			!/%changelog/ { print $0 }' \
			< kernel.spec > kernel.spec.tmp
mv kernel.spec.tmp kernel.spec
