#!/bin/sh
# Generate a commit for a rawhide RC release

source scripts/kernel-version.sh

klist -s
if [ ! $? -eq 0 ]; then
	echo "klist couldn't read the credential cache."
	echo "Do you need to fix your kerberos tokens?"
	exit 1
fi

make release
# fixup the release because rpmdev-bumpspec *sigh*
scripts/fixup-bumpspec.sh
fedpkg commit -c

# Figure out what is our RC
RC=`grep "%global rcrev" kernel.spec| cut -d ' ' -f 3`
RC=$(($RC+1))
BASE=`grep "%define base_sublevel" kernel.spec| cut -d ' ' -f 3`
OLDBASE=$BASE
# See comment in kernel.spec about the base numbering
BASE=$(($BASE+1))

# Kill all patches
awk '!/patch/ { print $0 }' < sources > sources.tmp
mv sources.tmp sources

# Grab the tarball
if [ ! -f patch-4.$BASE-rc$RC.xz ]; then
	wget -O patch-4.$BASE-rc$RC https://git.kernel.org/torvalds/p/v4.$BASE-rc$RC/v4.$OLDBASE
	if [ ! $? -eq 0 ]; then
		exit 1
	fi
	xz -9 patch-4.$BASE-rc$RC
	fedpkg upload patch-4.$BASE-rc$RC.xz
fi

# bump rcrev in the spec and set git snapshot to 0
RC=$RC perl -p -i -e 's|%global rcrev.*|%global rcrev $ENV{'RC'}|' kernel.spec

perl -p -i -e 's|%define gitrev.*|%define gitrev 0|' kernel.spec

perl -p -i -e 's|%global baserelease.*|%global baserelease 0|' kernel.spec

rpmdev-bumpspec -c "Linux v4.$BASE-rc$RC" kernel.spec
