#!/bin/sh
# This script allows for the generation of a git snapshot between the upstream
# git tree and the current tree.
#
# Prerequisites:
#     Set LINUX_GIT to point to an upstream Linux git tree in your .bashrc
#     or wherever.

# Look to see if LINUX_GIT is set in local .bashrc
if [ -f ~/.bashrc  ]; then
    source ~/.bashrc
fi

if [ ! -d "$LINUX_GIT" ]; then
    echo "error: set \$LINUX_GIT to point at upstream git tree"
    exit 1
fi

VER=$(grep patch sources | head -n1 | awk '{ print $2 }' | sed s/patch-// | sed s/-git.*// | sed s/.xz// | sed s/[\(\)]//g)

if [ -z "$VER" ] ;
then
    VER=$(grep linux sources | head -1 | awk '{ print $2 }' | sed s/linux-// | sed s/.tar.xz// | sed s/[\(\)]//g)
fi

OLDGIT=$(grep gitrev kernel.spec | head -n1 | sed s/%define\ gitrev\ //)
export NEWGIT=$(($OLDGIT+1))

pushd $LINUX_GIT

git diff v$VER.. > /tmp/patch-$VER-git$NEWGIT
xz -9 /tmp/patch-$VER-git$NEWGIT
DESC=$(git describe)
git rev-list --max-count=1 HEAD > /tmp/gitrev
popd

mv /tmp/patch-$VER-git$NEWGIT.xz .
mv /tmp/gitrev .

perl -p -i -e 's|%global baserelease.*|%global baserelease 0|' kernel.spec

perl -p -i -e 's|%define gitrev.*|%define gitrev $ENV{'NEWGIT'}|' kernel.spec

rpmdev-bumpspec -c "Linux $DESC" kernel.spec
