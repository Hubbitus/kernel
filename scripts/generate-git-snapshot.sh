#!/bin/sh
#
# Set LINUX_GIT to point to an upstream Linux git tree in your .bashrc or wherever.

[ ! -d "$LINUX_GIT" ] && echo "error: set \$LINUX_GIT to point at upstream git tree" && exit 1

VER=$(grep patch sources | head -n1 | awk '{ print $2 }' | sed s/patch-// | sed s/-git.*// | sed s/.xz//)

OLDGIT=$(grep gitrev kernel.spec | head -n1 | sed s/%define\ gitrev\ //)
export NEWGIT=$(($OLDGIT+1))

pushd $LINUX_GIT

git diff v$VER.. > /tmp/patch-$VER-git$NEWGIT
xz -9 /tmp/patch-$VER-git$NEWGIT
DESC=$(git describe)
popd

mv /tmp/patch-$VER-git$NEWGIT.xz .

perl -p -i -e 's|%global baserelease.*|%global baserelease 0|' kernel.spec

perl -p -i -e 's|%define gitrev.*|%define gitrev $ENV{'NEWGIT'}|' kernel.spec

rpmdev-bumpspec -c "Linux $DESC" kernel.spec
