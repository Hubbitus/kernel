#!/bin/bash

DIR=$(pwd)

# Only UP
LANG=C ionice -c3 nice -n19 rpmbuild --define "_sourcedir $DIR" --define "_specdir $DIR" --define "_builddir $DIR" --define "_srcrpmdir $DIR" --define "_rpmdir $DIR" --define 'dist .fc21' --define 'fedora 21' --eval '%undefine rhel' --define 'fc21 1' --define '_source_filedigest_algorithm md5' --define '_binary_filedigest_algorithm md5' \
	--without smp --without pae --without debug --without doc --without headers --without extra --without perf --without tools --without debuginfo --without bootwrapper --without vdso_install \
	--with baseonly \
	-ba ${DIR}/kernel.spec 2>&1 | tee .build-$(fedpkg --dist f21 verrel).log
