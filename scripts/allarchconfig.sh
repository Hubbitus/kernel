#!/bin/sh
# Run from within a source tree.

for i in configs/kernel-*.config
do
  cp -f $i .config
  Arch=`head -1 .config | cut -b 3-`
  echo $Arch \($i\)
  make ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true;
  if [ -s .newoptions ]; then
    cat .newoptions;
    exit 1;
  fi;
  rm -f .newoptions;
done

