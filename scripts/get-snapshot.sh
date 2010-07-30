#!/bin/bash

VER=$(tail -n1 upstream | sed s/bz2/id/)
rm -f $VER
wget -c http://www.kernel.org/pub/linux/kernel/v2.6/snapshots/$VER
SHA1=$(cat $VER)
rm -f patch-2.6.*-git*.id

cd ~/src/git-trees/kernel/linux-2.6
git pull

DIF=$(git diff $SHA1.. | wc -l)
if [ "$DIF" = "0" ]; then
  echo Nothing changed.
  exit
fi
TOT=$(git log | head -n1)

git diff $SHA1.. > ~/src/fedora/kernel/devel/git-linus-new.diff
cd ~/src/fedora/kernel/devel/
DIF=$(cmp git-linus.diff git-linus-new.diff)
if [ "$?" = "0" ]; then
  echo Nothing new in git
  rm -f git-linus-new.diff
  exit
fi
mv git-linus-new.diff git-linus.diff

perl -p -i -e 's|^#ApplyPatch\ git-linus.diff|ApplyPatch\ git-linus.diff|' kernel.spec

echo "- Merge Linux-2.6 up to" $TOT > ~/src/fedora/kernel/devel/clog.tmp
cd ~/src/fedora/kernel/devel/
bumpspecfile.py kernel.spec "$(cat clog.tmp)"
rm -f clog.tmp
make clog
