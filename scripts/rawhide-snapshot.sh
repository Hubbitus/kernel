#!/bin/sh
# A coffeeproof rawhide script. You should be able to run this before the
# coffee has kicked in and generate a good rawhide commit.
#
# - Updates the local Fedora tree to master and verifies that you are working
#   off of the correct master
# - Updates the upstream tree to the latest master.
# - Generates a git snapshot via generate-git-snapshot.sh
# - Clears out old git snapshots from the sources
# - Uploads the new snapshot

source scripts/kernel-version.sh

klist -s
if [ ! $? -eq 0 ]; then
	echo "klist couldn't read the credential cache."
	echo "Do you need to fix your kerberos tokens?"
	exit 1
fi

git fetch origin
if [ "$(git rev-parse origin/master)" != "$(git rev-parse HEAD)" ]; then
	echo "I just did a git fetch and this branch does not match master"
	echo "Re-check out this branch to work off of the latest master"
	exit 1
fi

if [ ! -d "$LINUX_GIT" ]; then
	echo "error: set \$LINUX_GIT to point at an upstream git tree"
	exit 1
fi

git -C $LINUX_GIT pull
if [ ! $? -eq 0 ]; then
	echo "Git pull failed. Is your tree clean/correct?"
	exit 1
fi

git -C $LINUX_GIT describe --tags HEAD | grep -q "\-g"
if [ ! $? -eq 0 ]; then
	echo "Trying to snapshot off of a tagged git."
	echo "I don't think this is what you want"
	exit 1
fi

if [ "$(git -C $LINUX_GIT rev-parse origin/master)" == `cat gitrev` ]; then
	echo "Last snapshot commit matches current master. Nothing to do"
	echo "\o/"
	exit 0
fi

GIT=`grep "%define gitrev" kernel.spec | cut -d ' ' -f 3`
if [ "$GIT" -eq 0 ]; then
	make debug
	./scripts/fixup-bumpspec.sh
	fedpkg commit -c
fi

./scripts/generate-git-snapshot.sh

#Nuke the old patch from the source
awk '!/git/ { print $0 }' < sources > sources.tmp
mv sources.tmp sources

GIT=`grep "%define gitrev" kernel.spec | cut -d ' ' -f 3`
fedpkg upload patch-$VER-git$GIT.xz
