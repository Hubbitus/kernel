#!/bin/sh
# Small script to generate the perf-man tarball. The script relies on having
# LINUX_GIT set in your local .bashrc. By default the script will use the
# the kernel version of the upstream tree set in LINUX_GIT. Use --version=x.y
# to set a specific version.

# [Default] eg. ./scritps/generate-perf-man
# eg. ./scripts/generate-perf-man --version=4.8
function usage(){
    echo
    echo "Helps generate the perf-man tarball                              "
    echo "-h, --help                                                       "
    echo
    echo "./generate-perf-man.sh   #Generates using upstream kernel version"
    echo
    echo "./generate-perf-man.sh --version=x.y  #Generate using x.y version"
}

if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

if [ ! -d "$LINUX_GIT" ]; then
    echo "Error: \$LINUX_GIT is not set to the upstream git tree."
    exit 1
fi

BASEDIR=$(dirname "$(cd $(dirname $BASH_SOURCE[0]) && pwd)")
pushd "$LINUX_GIT" > /dev/null
KERNEL_VERSION=$( awk '/^VERSION =/ {print $3}' Makefile )
KERNEL_PATCHLEVEL=$( awk '/^PATCHLEVEL =/ {print $3}' Makefile )

if [ ! -z "$@" ]; then
    for opt in "$@"; do
	case $opt in
	    --version=*.*)
		version="${opt#*=}"
		KERNEL_VERSION=$( awk -F. '{print $1}' <<< $version )
		KERNEL_PATCHLEVEL=$( awk -F. '{print $2}' <<< $version )
		;;
	    -h | --help)
		usage
		exit 0
		;;
	    *)
		;;
	esac
    done
fi
cd tools/perf/Documentation/
make
tar -czvf $BASEDIR/perf-man-${KERNEL_VERSION}.${KERNEL_PATCHLEVEL}.tar.gz *.1
make clean
popd
