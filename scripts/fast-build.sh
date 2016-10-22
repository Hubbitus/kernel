#! /bin/sh
# Description:
#     rpmbuild combo to build the given architecture without
#     debugging information, perf or tools.
#
# Sample usage:
#     ./fast-build.sh x86_64 kernel-4.7.0-0.rc1.git1.2.fc25.src.rpm

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "usage: $0 [ arch ] [ kernel-x.x.x.fcxx.src.rpm ] "
fi

rpmbuild --target $1 --without debug --without debuginfo --without perf --without tools --rebuild $2
