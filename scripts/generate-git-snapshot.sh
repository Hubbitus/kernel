#!/bin/sh
#
# Set LINUX_GIT to point to an upstream Linux git tree in your .bashrc or wherever.
#
# TODO: Generate the gitN number.
#

VER=$(grep patch sources | head -n1 | awk '{ print $2 }' | sed s/patch-// | sed s/.xz//)

pushd $LINUX_GIT

git diff v$VER.. > /tmp/patch-$VER-git
xz -9 /tmp/patch-$VER-git
DESC=$(git describe)
popd

mv /tmp/patch-$VER-git.xz .

rpmdev-bumpspec -c "Linux $DESC" kernel.spec
