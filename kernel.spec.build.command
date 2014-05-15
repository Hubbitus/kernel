# Only UP
LANG=C ionice -c3 nice -n19 rpmbuild --define '_sourcedir /home/pasha/SOFT/git_OTHERS/kernel/f20' --define '_specdir /home/pasha/SOFT/git_OTHERS/kernel/f20' --define '_builddir /home/pasha/SOFT/git_OTHERS/kernel/f20' --define '_srcrpmdir /home/pasha/SOFT/git_OTHERS/kernel/f20' --define '_rpmdir /home/pasha/SOFT/git_OTHERS/kernel/f20' --define 'dist .fc20' --define 'fedora 20' --eval '%undefine rhel' --define 'fc20 1' --define '_source_filedigest_algorithm md5' --define '_binary_filedigest_algorithm md5' \
	--without smp --without pae --without debug --without doc --without headers --without extra --without perf --without tools --without debuginfo --without bootwrapper --without vdso_install \
	--with baseonly \
	-ba /home/pasha/SOFT/git_OTHERS/kernel/f20/kernel.spec | tee .build-3.14.2-200.hu.1.fc20.log
