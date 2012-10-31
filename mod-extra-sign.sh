#! /bin/bash

# We need to sign modules we've moved from <path>/kernel/ to <path>/extra/
# during mod-extra processing by hand.  The 'modules_sign' Kbuild target can
# "handle" out-of-tree modules, but it does that by not signing them.  Plus,
# the modules we've moved aren't actually out-of-tree.  We've just shifted
# them to a different location behind Kbuild's back because we are mean.

# This essentially duplicates the 'modules_sign' Kbuild target and runs the
# same commands for those modules.

moddir=$1

modules=`find $moddir -name *.ko`

MODSECKEY="./signing_key.priv"
MODPUBKEY="./signing_key.x509"

for mod in $modules
do
    dir=`dirname $mod`
    file=`basename $mod`

    ./scripts/sign-file ${MODSECKEY} ${MODPUBKEY} ${dir}/${file} \
       ${dir}/${file}.signed
    mv ${dir}/${file}.signed ${dir}/${file}
    rm -f ${dir}/${file}.{sig,dig}
done
