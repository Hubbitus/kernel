#!/bin/sh
# Generate a commit for a rawhide RC release

source scripts/kernel-version.sh

make release
# fixup the release because rpmdev-bumpspec *sigh*
scripts/fixup-bumpspec.sh
fedpkg commit -c

# Figure out what is our RC
RC=`grep kernel.spec "%define rcrev" | cut -d ' ' -f 3`
RC=$(($RC+1))

# Kill all patches
awk '!/patch/ { print $0 }' < sources > sources.tmp
mv sources.tmp sources

# Grab the tarball
# FILL this in laura

# bump rcrev in the spec and set git snapshot to 0

perl -p -i -e 's|%define rcrev.*|%global rcrev $ENV{'RC'}|' kernel.spec

perl -p -i -e 's|%define gitrev.*|%define gitrev 0|' kernel.spec
