#!/bin/bash

base_sublevel=$(grep "^%define base_sublevel" kernel.spec | head -n1 | awk '{ print $3 }')

#if [ `grep -c "^%define released_kernel 1" kernel.spec` -ge 1 ]; then
  V=$base_sublevel
#else
#  let V=$base_sublevel+1
#fi

cd kernel-2.6.$base_sublevel/linux-2.6.$base_sublevel.noarch/
rm -f kernel-*.config
cp ../../kernel-2.6.$V-*.config .

for i in kernel-*.config
do
	echo $i
	rm -f .config
	cp $i .config
	Arch=`head -1 .config | cut -b 3-`
	make ARCH=$Arch nonint_oldconfig > /dev/null || exit 1
	echo "# $Arch" > configs/$i
	cat .config >> configs/$i
	echo
done

