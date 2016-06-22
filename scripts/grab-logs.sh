#!/bin/sh
# Script helps download the build logs for the current tree.
# The downloaded logs will be saved in a logs/ within the
# tree.

BASEDIR="$(dirname "$(cd $(dirname $BASH_SOURCE[0]) && pwd)")"
pushd $BASEDIR > /dev/null

VER=$(fedpkg verrel)
ver=$(echo $VER | sed -e 's/-/ /g' | awk '{print $2}')
rev=$(echo $VER | sed -e 's/-/ /g' | awk '{print $3}')

# keep logs in one place. If logs directory does not exist, make it.
if [ -d "$BASEDIR/logs" ]; then
  DIR="$BASEDIR/logs"
else
  mkdir "$BASEDIR/logs"
  DIR="$BASEDIR/logs"
fi

# Common architectures that have build logs.
ARCHS[0]=i686
ARCHS[1]=x86_64
ARCHS[2]=noarch
ARCHS[3]=armv7hl

for arch in ${ARCHS[@]}; do
    URL=http://kojipkgs.fedoraproject.org/packages/kernel/$ver/$rev/data/logs/$arch/build.log
    # Only download logs if exist
    wget --spider -q $URL
    if [ $? -eq 0 ]; then
	wget -O $DIR/build-$VER-$arch.log $URL
    fi
done
popd > /dev/null
