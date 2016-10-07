#!/bin/sh
#
# Author: Laura Abbott <labbott@fedoraproject.org>
#
# Apply a stable patch update to the Fedora tree. This takes care of
# - Downloading the patch from kernel.org
# - Uploading the source file
# - Removing old patch files
# - Updating the spec file stable version
# - Adding a proper changelog entry
#
# Based on steps from https://fedoraproject.org/wiki/Kernel/DayToDay#Stable_kernel_update
#
# Args: Stable version to update (e.g. 4.7.7, 4.8.1)

if [ $# -lt 1 ]; then
	echo "Need a version"
	exit 1
fi

VERSION=`echo $1 | cut -d . -f 1`
if [ -z $VERSION ]; then
	echo "Malformed version $1"
	exit 1
fi
PATCHLEVEL=`echo $1 | cut -d . -f 2`
if [ -z $VERSION ]; then
	echo "Malformed version $1"
	exit 1
fi
SUBLEVEL=`echo $1 | cut -d . -f 3`
if [ -z $VERSION ]; then
	echo "Malformed version $1"
	exit 1
fi

if [ ! -f patch-$1.xz ]; then
	wget https://cdn.kernel.org/pub/linux/kernel/v4.x/patch-$1.xz
	if [ ! $? -eq 0 ]; then
		echo "Download fail"
		exit 1
	fi
fi

grep $1 sources &> /dev/null
if [ ! $? -eq 0 ]; then
	fedpkg upload patch-$1.xz

	# Cryptic awk: search for the previous patch level (if one exists) and
	# remove it from the source file
	awk -v VER=$VERSION.$PATCHLEVEL.$((SUBLEVEL-1)) '$0 !~ VER { print $0; }' < sources > sources.tmp
	mv sources.tmp sources
fi

# Update the stable level
awk -v STABLE=$SUBLEVEL '/%define stable_update/ \
			{ print "%define stable_update " STABLE } \
			!/%define stable_update/ { print $0 }' \
			< kernel.spec > kernel.spec.tmp
mv kernel.spec.tmp kernel.spec

# Add the changelog entry. Ideally we would get rpmdev-bumpspec to do so
# but that also bumps the release which we don't want so do this manually
# for now

BASERELEASE=`cat kernel.spec | grep "%global baserelease" | cut -d ' ' -f 3`
CURDATE=`date +"%a %b %d %Y"`
PACKAGER=`rpmdev-packager`
CHANGELOG="%changelog\n* $CURDATE $PACKAGER - $1\n- Linux v$1\n"

awk -v CHANGE="$CHANGELOG" '/%changelog/ {print CHANGE } \
			!/%changelog/ { print $0 }' \
			< kernel.spec > kernel.spec.tmp
mv kernel.spec.tmp kernel.spec
