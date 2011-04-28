#!/bin/bash

KORG26="http://ftp.kernel.org/pub/linux/kernel/v2.6"
KORG26SNAPS="${KORG26}/snapshots"
KORG26TESTING="${KORG26}/testing"

if [ ! -f /usr/bin/curl ]; then
  echo yum install curl
  exit 0
fi

# Current kernel bits
if [ `grep -c patch-2.6 sources` -ge 1 ]; then
  export OLD=`grep patch-2.6 sources | awk '{print $2}' | tail -n1 | sed s/patch-// | sed s/\.bz2//`
else
  export OLD=`grep linux-2.6 sources | awk '{print $2}' | tail -n1 | sed s/linux-// | sed s/\.tar\.bz2//`
fi
export OLDBASE=`echo $OLD | sed s/-/\ /g | sed s/2\.6\.// | awk '{ print $1 }'`
if [ `echo $OLD | grep -c rc` -ge 1 ]; then
  export OLDRC=`echo $OLD | sed s/-/\ /g | sed s/rc// | awk '{ print $2 }'`
  if [ `echo $OLD | grep -c git` -ge 1 ]; then
    export OLDGIT=`echo $OLD | sed s/-/\ /g | sed s/git// | awk '{ print $3 }'`
  else
    export OLDGIT=0
  fi
else
  export OLDRC=0
  if [ `echo $OLD | grep -c git` -ge 1 ]; then
    export OLDGIT=`echo $OLD | sed s/-/\ /g | sed s/git// | awk '{ print $2 }'`
  else
    export OLDGIT=0
  fi
fi

# Is there a new snapshot or prepatch ?
NEW=`curl -s http://www.kernel.org/kdist/finger_banner | grep "latest snapshot 2.6 version"`
if [ -z "$NEW" ] ; then
  NEW=`curl -s http://www.kernel.org/kdist/finger_banner | grep "latest mainline 2.6 version"`
  if [ -z "$NEW" ] ; then
    if [ "$OLDRC" -ne 0 ] ; then
      NEW=`curl -s http://www.kernel.org/kdist/finger_banner | grep "latest stable 2.6." | head -n1`
    else
      echo "No new rc or git snapshot of stable branch".
      exit 0
    fi
  fi
fi
export N=`echo $NEW | awk '{ print $11 }'`
if [ -z "$N" ]; then
  # "Stable version"
  export NEW=`echo $NEW | awk '{ print $10 }'`
else
  export NEW=`echo $NEW | awk '{ print $11 }'`
fi

export NEWBASE=`echo $NEW | sed s/-/\ /g | sed s/2\.6\.// | awk '{ print $1 }'`
if [ `echo $NEW | grep -c rc` -ge 1 ]; then
  export NEWRC=`echo $NEW | sed s/-/\ /g | sed s/rc// | awk '{ print $2 }'`
  if [ `echo $NEW | grep -c git` -ge 1 ]; then
    export NEWGIT=`echo $NEW | sed s/-/\ /g | sed s/git// | awk '{ print $3 }'`
  else
    export NEWGIT=0
  fi
else
  export NEWRC=0
  if [ `echo $NEW | grep -c git` -ge 1 ]; then
    export NEWGIT=`echo $NEW | sed s/-/\ /g | sed s/git// | awk '{ print $2 }'`
  else
    export NEWGIT=0
  fi
fi

echo "OLD kernel was $OLD  BASE=$OLDBASE RC=$OLDRC GIT=$OLDGIT"
echo "NEW kernel is  $NEW  BASE=$NEWBASE RC=$NEWRC GIT=$NEWGIT"

if [ "$OLDRC" -eq 0 -a "$OLDGIT" -eq 0 -a "$OLDGIT" -ne "$NEWGIT" ]; then
  echo "Rebasing from a stable release to a new git snapshot"
  perl -p -i -e 's/^%define\ released_kernel\ 1/\%define\ released_kernel\ 0/' kernel.spec
  perl -p -i -e 's/^%define\ rawhide_skip_docs\ 1/\%define\ rawhide_skip_docs\ 0/' kernel.spec
  # force these to zero in this case, they may not have been when we rebased to stable
  perl -p -i -e 's/^%define\ rcrev.*/\%define\ rcrev\ 0/' kernel.spec
  perl -p -i -e 's/^%define\ gitrev.*/\%define\ gitrev\ 0/' kernel.spec
fi

# make sure we build docs at least once per -rc kernel, shut it off otherwise
if [ "$OLDRC" -ne 0 -a "$NEWRC" -gt "$OLDRC" ]; then
  perl -p -i -e 's/^%define\ rawhide_skip_docs\ 1/\%define\ rawhide_skip_docs\ 0/' kernel.spec
else
  if [ "$NEWRC" -eq "$OLDRC" -a "$NEWGIT" -gt "$OLDGIT" ]; then
    # common case, same -rc, new -git, make sure docs are off.
    perl -p -i -e 's/^%define\ rawhide_skip_docs\ 0/\%define\ rawhide_skip_docs\ 1/' kernel.spec
  fi
fi

if [ "$NEWRC" -eq 0 -a "$NEWGIT" -eq 0 ]; then
  echo "Rebasing from -rc to final release."
  perl -p -i -e 's/^%define\ released_kernel\ 0/\%define\ released_kernel\ 1/' kernel.spec
  perl -p -i -e 's/^%define\ rawhide_skip_docs\ 1/\%define\ rawhide_skip_docs\ 0/' kernel.spec
  export OLD_TARBALL_BASE=$(($OLDBASE-1))
  perl -p -i -e 's/^%define\ base_sublevel\ $ENV{OLD_TARBALL_BASE}/%define\ base_sublevel\ $ENV{NEWBASE}/' kernel.spec
  perl -p -i -e 's/^%define\ rcrev.*/\%define\ rcrev\ 0/' kernel.spec
  perl -p -i -e 's/^%define\ gitrev.*/\%define\ gitrev\ 0/' kernel.spec

  grep -v kernel-2.6.$OLD_TARBALL_BASE .gitignore >.gitignore.tmp ; mv .gitignore.tmp .gitignore
  echo kernel-2.6.$NEWBASE >> .gitignore

  for i in sources .gitignore
  do
   grep -v linux-2.6.$OLD_TARBALL_BASE.tar.bz2 $i > .$i.tmp; mv .$i.tmp $i
   grep -v patch-2.6.$OLDBASE-rc$OLDRC.bz2 $i > .$i.tmp; mv .$i.tmp $i
   grep -v patch-2.6.$OLDBASE-rc$OLDRC-git$OLDGIT.bz2 $i > .$i.tmp; mv .$i.tmp $i
  done

  rm -f linux-2.6.$OLD_TARBALL_BASE.tar.bz2
  rm -f patch-2.6.$OLDBASE-rc$OLDRC.bz2
  rm -f patch-2.6.$OLDBASE-rc$OLDRC-git$OLDGIT.bz2

  curl -O $KORG26/linux-$NEW.tar.bz2
  fedpkg upload linux-$NEW.tar.bz2

  exit 1
fi

if [ "$OLDRC" != "$NEWRC" ]; then
  echo "Different rc. Rebasing from $OLDRC to $NEWRC"
  perl -p -i -e 's/^%define\ rcrev.*/\%define\ rcrev\ $ENV{"NEWRC"}/' kernel.spec
  grep -v patch-2.6.$OLDBASE-rc$OLDRC.bz2 sources > .sources.tmp; mv .sources.tmp sources
  rm -f patch-2.6.$OLDBASE-rc$OLDRC.bz2

  curl -O $KORG26TESTING/patch-2.6.$NEWBASE-rc$NEWRC.bz2
  fedpkg upload patch-2.6.$NEWBASE-rc$NEWRC.bz2

  # Another awkward (albeit unlikely) corner case.
  # Moving from say 26-rc3-git1 to 26-rc4-git1
  # The above will grab the new -rc, but the below will
  # think that the -git hasn't changed.
  # Fudge around this, by pretending the old git was something crazy.
  OLDGIT=99
fi

if [ "$OLDGIT" != "$NEWGIT" ]; then
  if [ "$OLDRC" -eq 0 -a "$OLDGIT" -eq 0 ]; then
    echo "Rebasing to pre-rc git$NEWGIT"
  else
    echo "Different git. Rebasing from git$OLDGIT to git$NEWGIT"
  fi
  perl -p -i -e 's/^%define\ gitrev.*/\%define\ gitrev\ $ENV{"NEWGIT"}/' kernel.spec
  if [ "$OLDGIT" -ne 0 ]; then
    grep -v patch-$OLD.bz2 sources > .sources.tmp; mv .sources.tmp sources
  fi

  if [ "$NEWGIT" -ne 0 ]; then
  	curl -O $KORG26SNAPS/patch-$NEW.bz2
  fi
  fedpkg upload patch-$NEW.bz2

  if [ "$OLDGIT" -ne 0 ]; then
    rm -f patch-$OLD.bz2
  fi
fi

if [ "$OLDRC" != "$NEWRC" -o "$OLDGIT" != "$NEWGIT" ]; then
  perl -p -i -e 's|^ApplyPatch\ git-linus.diff|#ApplyPatch\ git-linus.diff|' kernel.spec
  > git-linus.diff
  fedpkg clog
  exit 1
else
  exit 0
fi
