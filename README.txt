
		Kernel package tips & tricks.
		~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The kernel is one of the more complicated packages in the distro, and
for the newcomer, some of the voodoo in the spec file can be somewhat scary.
This file attempts to document some of the magic.


Speeding up make prep
---------------------
The kernel is nearly 500MB of source code, and as such, 'make prep'
takes a while. The spec file employs some trickery so that repeated
invocations of make prep don't take as long.  Ordinarily the %prep
phase of a package will delete the tree it is about to untar/patch.
The kernel %prep keeps around an unpatched version of the tree,
and makes a symlink tree clone of that clean tree and than applies
the patches listed in the spec to the symlink tree.
This makes a huge difference if you're doing multiple make preps a day.
As an added bonus, doing a diff between the clean tree and the symlink
tree is slightly faster than it would be doing two proper copies of the tree.


build logs.
-----------
There's a convenience helper script in scripts/grab-logs.sh
that will grab the build logs from koji for the kernel version reported
by make verrel


config heirarchy.
-----------------
Instead of having to maintain a config file for every arch variant we build on,
the kernel spec uses a nested system of configs. Each option CONFIG_FOO is
represented by a single file named CONFIG_FOO which contains the state (=y, =m,
=n). These options are collected in the folder baseconfig. Architecture specifi
options are set in nested folders. An option set in a nested folder will
override the same option set in one of the higher levels.

The individual CONFIG_FOO files only exist in the pkg-git repository. The RPM
contains kernel-foo.config files which are the result of combining all the
CONFIG_FOO files. The files are combined by running build_configs.sh. This
script _must_ be run each time one of the options is changed.

Example flow:

# Enable the option CONFIG_ABC123 as a module for all arches
echo "CONFIG_ABC123=m" > baseconfig/CONFIG_ABC1234
# enable the option CONFIG_XYZ321 for only x86
echo "# CONFIG_XYZ321 is not set" > baseconfig/CONFIG_XYZ321
echo "CONFIG_XYZ321=m" > baseconfig/x86/CONFIG_XYZ321
# regenerate the combined config files
./build_configs.sh

The file config_generation gives a listing of what folders go into each
config file generated.

debug options.
--------------
This is a little complicated, as the purpose & meaning of this changes
depending on where we are in the release cycle.
If we are building for a current stable release, 'make release' has
typically been run already, which sets up the following..
- Two builds occur, a 'kernel' and a 'kernel-debug' flavor.
- kernel-debug will get various heavyweight debugging options like
  lockdep etc turned on.

If we are building for rawhide, 'make debug' has been run, which changes
the status quo to:
- We only build one kernel 'kernel'
- The debug options are always turned on.
This is done to increase coverage testing, as not many people actually
run kernel-debug.

The debug options are managed in a separate heierarchy under debugconfig. This
works in a similar manner to baseconfig. More deeply nested folders, again,
override options. The file config_generation gives a listing of what folders
go into each config file generated.
