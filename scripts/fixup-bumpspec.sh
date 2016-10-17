#!/bin/sh
# rpmdev-bumpspec 'helpfully' bumps the release which we don't always want.
# This script fixes it up.

RELEASE=`grep "%global baserelease" kernel.spec | cut -d ' ' -f 3`
export RELEASE=$(($RELEASE-1))
perl -p -i -e 's|%global baserelease.*|%global baserelease $ENV{'RELEASE'}|' kernel.spec
TODAY=`date +"%a %b %d %Y"`
awk -v DATE="$TODAY" 'START { marked = 0; } $0 ~ DATE { if (marked == 1) { print $0 } else {out=$1; for(i = 2; i <= NF - 2; i++) { out=out" "$i } print out; marked = 1;  } } $0 !~ DATE { print $0; }' < kernel.spec > kernel.spec.tmp
mv kernel.spec.tmp kernel.spec
