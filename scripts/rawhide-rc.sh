#!/bin/sh
# Generate a commit for a rawhide RC release

source scripts/kernel-version.sh

make release
# fixup the release because rpmdev-bumpspec *sigh*
scripts/fixup-bumpspec.sh
fedpkg commit -c

# Figure out what is our RC
RC=`grep "%define rcrev" kernel.spec| cut -d ' ' -f 3`
RC=$(($RC+1))
BASE=`grep "%define base_sublevel" kernel.spec| cut -d ' ' -f 3`

# Kill all patches
awk '!/patch/ { print $0 }' < sources > sources.tmp
mv sources.tmp sources

# Grab the tarball
if [ ! -f patch-4.$BASE-rc$RC.xz ]; then
	wget https://cdn.kernel.org/pub/linux/kernel/v4.x/testing/patch-4.$BASE-rc$RC.xz
	if [ ! $? -eq 0 ]; then
		exit 1
	fi
	fedpkg upload patch-4.$BASE-rc$RC.xz
fi

# bump rcrev in the spec and set git snapshot to 0
RC=$RC perl -p -i -e 's|%define rcrev.*|%global rcrev $ENV{'RC'}|' kernel.spec

perl -p -i -e 's|%define gitrev.*|%define gitrev 0|' kernel.spec

perl -p -i -e 's|%global baserelease.*|%global baserelease 0|' kernel.spec

rpmdev-bumpspec -c "Linux v4.$BASE-rc$RC" kernel.spec
