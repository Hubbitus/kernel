#!/bin/bash

utrace_base=2.6-current
utrace_base=2.6.34

url=http://people.redhat.com/roland/utrace/${1:-$utrace_base}

wget -q -O /dev/stdout $url/series | grep 'patch$' |
while read i
do
  rm -f linux-2.6-$i
  wget -nv -O linux-2.6-$i $url/$i
done
