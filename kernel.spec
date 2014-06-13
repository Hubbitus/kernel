# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 0

# Sign modules on x86.  Make sure the config files match this setting if more
# architectures are added.
%ifarch %{ix86} x86_64
%global signmodules 1
%global zipmodules 1
%else
%global signmodules 0
%global zipmodules 0
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
%endif

# % define buildid .local

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# We used to have some extra magic weirdness to bump this automatically,
# but now we don't.  Just use: rpmdev-bumpspec -c 'comment for changelog'
# When changing base_sublevel below or going from rc to a final kernel,
# reset this by hand to 1 (or to 0 and then use rpmdev-bumpspec).
# scripts/rebase.sh should be made to do that for you, actually.
#
# NOTE: baserelease must be > 0 or bad things will happen if you switch
#       to a released kernel (released version will be < rc version)
#
# For non-released -rc kernels, this will be appended after the rcX and
# gitX tags, so a 3 here would become part of release "0.rcX.gitX.3"
#
%global baserelease 1
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 15

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 3.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 0
# The git snapshot level
%define gitrev 7
# Set rpm version accordingly
%define rpmversion 3.%{upstream_sublevel}.0
%endif
# Nb: The above rcrev and gitrev values automagically define Patch00 and Patch01 below.

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# standard kernel
%define with_up        %{?_without_up:        0} %{?!_without_up:        1}
# kernel-smp (only valid for ppc 32-bit)
%define with_smp       %{?_without_smp:       0} %{?!_without_smp:       1}
# kernel PAE (only valid for i686 (PAE) and ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-modules-extra
%define with_extra     %{?_without_extra:     0} %{?!_without_extra:     1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}
#
# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the pae kernel (--with paeonly):
%define with_paeonly   %{?_with_paeonly:      1} %{?!_with_paeonly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}
#
# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}
#
# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}
#
# build a release kernel on rawhide
%define with_release   %{?_with_release:      1} %{?!_with_release:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 0

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%define pkg_release %{fedora_build}%{?buildid}%{?dist}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define pkg_release 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 3.%{base_sublevel}

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if 0%{!?nopatches:1}
%define nopatches 0
%endif

%if %{with_vanilla}
%define nopatches 1
%endif

%if %{nopatches}
%define with_bootwrapper 0
%define variant -vanilla
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# kernel PAE is only built on i686 and ARMv7.
%ifnarch i686 armv7hl
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_smp 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%define with_pae 0
%endif
%define with_smp 0
%define with_pae 0
%define with_tools 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64 ppc64p7 s390 s390x aarch64 ppc64le
%endif

# Overrides for generic default options

# only ppc needs a separate smp kernel
%ifnarch ppc 
%define with_smp 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64 ppc64p7 ppc64le
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64 and sparc64
%ifarch ppc64 ppc ppc64p7 ppc64le
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define pae PAE
%define all_arch_configs kernel-%{version}-i?86*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc64 ppc64p7
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch ppc64le
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64le.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_tools 0
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_tools 0
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc{-,.}*config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define asmarch arm
%define hdrarch arm
%define pae lpae
%define make_target bzImage
%define kernel_image arch/arm/boot/zImage
# http://lists.infradead.org/pipermail/linux-arm-kernel/2012-March/091404.html
%define kernel_mflags KALLSYMS_EXTRA_PASS=1
# we only build headers/perf/tools on the base arm arches
# just like we used to only build them on i386 for x86
%ifnarch armv7hl
%define with_headers 0
%define with_perf 0
%define with_tools 0
%endif
%endif

%ifarch aarch64
%define all_arch_configs kernel-%{version}-aarch64*.config
%define asmarch arm64
%define hdrarch arm64
%define make_target Image.gz
%define kernel_image arch/arm64/boot/Image.gz
%define image_install_path boot
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}
%define listnewconfig_fail 0
%else
%define listnewconfig_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 s390

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_debuginfo 0
%define with_perf 0
%define with_tools 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs %{ix86} x86_64 ppc ppc64 ppc64p7 %{arm} aarch64 ppc64le

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, systemd >= 203-2
%define initrd_prereq  dracut >= 027


Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: %{all_x86} x86_64 ppc ppc64 ppc64p7 s390 s390x %{arm} aarch64 ppc64le
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-%{?variant:%{variant}-}core-uname-r = %{KVERREL}%{?variant}
Requires: kernel-%{?variant:%{variant}-}modules-uname-r = %{KVERREL}%{?variant}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, sh-utils, tar
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, perl-Carp, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc
BuildRequires: net-tools, hostname, bc
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed) bison flex
BuildRequires: audit-libs-devel
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
%define debuginfo_args --strict-build-id -r
%endif

%if %{signmodules}
BuildRequires: openssl
BuildRequires: pesign >= 0.10-4
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v3.0/linux-%{kversion}.tar.xz

Source10: perf-man-%{kversion}.tar.gz
Source11: x509.genkey

Source15: merge.pl
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-sign.sh
Source90: filter-x86_64.sh
Source91: filter-armv7hl.sh
Source92: filter-i686.sh
Source93: filter-aarch64.sh
Source94: filter-ppc.sh
Source95: filter-ppc64.sh
Source96: filter-ppc64le.sh
Source97: filter-s390x.sh
Source98: filter-ppc64p7.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source19: Makefile.release
Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic
Source24: config-no-extra

Source30: config-x86-generic
Source31: config-i686-PAE
Source32: config-x86-32-generic

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source51: config-powerpc32-generic
Source52: config-powerpc32-smp
Source53: config-powerpc64
Source54: config-powerpc64p7
Source55: config-powerpc64le

Source70: config-s390x

Source100: config-arm-generic

# Unified ARM kernels
Source101: config-armv7-generic
Source102: config-armv7
Source103: config-armv7-lpae

Source110: config-arm64

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: config-local

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-3.%{base_sublevel}.%{stable_base}.xz
Patch00: %{stable_patch_00}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Patch00: patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
Patch01: patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Patch00: patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif
%endif

# we also need compile fixes for -vanilla
Patch04: compile-fixes.patch

# build tweak for build ID magic, even for -vanilla
Patch05: makefile-after_link.patch

%if !%{nopatches}


# revert upstream patches we get via other methods
Patch09: upstream-reverts.patch
# Git trees.

# Standalone patches

Patch450: input-kill-stupid-messages.patch
Patch452: no-pcspkr-modalias.patch

Patch460: serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: silence-noise.patch
Patch530: silence-fbcon-logo.patch

Patch600: 0001-lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

#rhbz 917708
Patch700: Revert-userns-Allow-unprivileged-users-to-create-use.patch

Patch800: crash-driver.patch

# crypto/

# secure boot
Patch1000: secure-modules.patch
Patch1001: modsign-uefi.patch
Patch1002: sb-hibernate.patch
Patch1003: sysrq-secure-boot.patch

# virt + ksm patches

# DRM

# nouveau + drm fixes
# intel drm is all merged upstream
Patch1826: drm-i915-hush-check-crtc-state.patch

# Quiet boot fixes

# fs fixes

# NFSv4

# patches headed upstream
Patch12016: disable-i8042-check-on-apple-mac.patch

Patch14000: hibernate-freeze-filesystems.patch

Patch14010: lis3-improve-handling-of-null-rate.patch

Patch15000: nowatchdog-on-virt.patch

# ARM64

# ARM

# lpae

# ARM omap

# ARM tegra
Patch21020: arm-tegra-usb-no-reset-linux33.patch

# ARM i.MX6

# ARM sunxi (AllWinner)

#rhbz 754518
Patch21235: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

# https://fedoraproject.org/wiki/Features/Checkpoint_Restore
Patch21242: criu-no-expert.patch

#rhbz 892811
Patch21247: ath9k_rx_dma_stop_check.patch

Patch22000: weird-root-dentry-name-debug.patch

Patch25047: drm-radeon-Disable-writeback-by-default-on-ppc.patch

#rhbz 1025603
Patch25063: disable-libdw-unwind-on-non-x86.patch

#rhbz 983342 1093120
Patch25069: 0001-acpi-video-Add-4-new-models-to-the-use_native_backli.patch

Patch26000: perf-lib64.patch

# Patch series from Hans for various backlight and platform driver fixes
Patch26002: samsung-laptop-Add-broken-acpi-video-quirk-for-NC210.patch
Patch26004: asus-wmi-Add-a-no-backlight-quirk.patch
Patch26005: eeepc-wmi-Add-no-backlight-quirk-for-Asus-H87I-PLUS-.patch
Patch26013: acpi-video-Add-use-native-backlight-quirk-for-the-Th.patch
Patch26014: acpi-video-Add-use_native_backlight-quirk-for-HP-Pro.patch

Patch26016: x86-vdso-Fix-vdso_install.patch

# END OF PATCH DEFINITIONS

%endif

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel meta package

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:+%{1}}\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20130724-29.git31f6b30\
Requires(preun): systemd >= 200\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip binutils
%description bootwrapper
Kernel-bootwrapper contains the wrapper code which makes bootable "zImage"
files combining both kernel and initial ramdisk.

%package debuginfo-common-%{_target_cpu}
Summary: Kernel source files used by %{name}-debuginfo packages
Group: Development/Debug
%description debuginfo-common-%{_target_cpu}
This package is required by %{name}-debuginfo subpackages.
It provides the kernel source files common to all builds.

%if %{with_perf}
%package -n perf
Summary: Performance monitoring for the Linux kernel
Group: Development/System
License: GPLv2
%description -n perf
This package contains the perf tool, which enables performance monitoring
of the Linux kernel.

%package -n perf-debuginfo
Summary: Debug information for package perf
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n perf-debuginfo
This package provides debug information for the perf package.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|.*%%{_libdir}/traceevent/plugins/.*|XXX' -o perf-debuginfo.list}

%package -n python-perf
Summary: Python bindings for apps which will manipulate perf events
Group: Development/Libraries
%description -n python-perf
The python-perf package contains a module that permits applications
written in the Python programming language to use the interface
to manipulate perf events.

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%package -n python-perf-debuginfo
Summary: Debug information for package perf python bindings
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n python-perf-debuginfo
This package provides debug information for the perf python bindings.

# the python_sitearch macro should already be defined from above
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{python_sitearch}/perf.so(\.debug)?|XXX' -o python-perf-debuginfo.list}


%endif # with_perf

%if %{with_tools}
%package -n kernel-tools
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Provides:  cpupowerutils = 1:009-0.6.p1
Obsoletes: cpupowerutils < 1:009-0.6.p1
Provides:  cpufreq-utils = 1:009-0.6.p1
Provides:  cpufrequtils = 1:009-0.6.p1
Obsoletes: cpufreq-utils < 1:009-0.6.p1
Obsoletes: cpufrequtils < 1:009-0.6.p1
Obsoletes: cpuspeed < 1:1.5-16
Requires: kernel-tools-libs = %{version}-%{release}
%description -n kernel-tools
This package contains the tools/ directory from the kernel source
and the supporting documentation.

%package -n kernel-tools-libs
Summary: Libraries for the kernels-tools
Group: Development/System
License: GPLv2
%description -n kernel-tools-libs
This package contains the libraries built from the tools/ directory
from the kernel source.

%package -n kernel-tools-libs-devel
Summary: Assortment of tools for the Linux kernel
Group: Development/System
License: GPLv2
Requires: kernel-tools = %{version}-%{release}
Provides:  cpupowerutils-devel = 1:009-0.6.p1
Obsoletes: cpupowerutils-devel < 1:009-0.6.p1
Requires: kernel-tools-libs = %{version}-%{release}
Provides: kernel-tools-devel
%description -n kernel-tools-libs-devel
This package contains the development files for the tools/ directory from
the kernel source.

%package -n kernel-tools-debuginfo
Summary: Debug information for package kernel-tools
Group: Development/Debug
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}
AutoReqProv: no
%description -n kernel-tools-debuginfo
This package provides debug information for package kernel-tools.

# Note that this pattern only works right to match the .build-id
# symlinks because of the trailing nonmatching alternation and
# the leading .*, because of find-debuginfo.sh's buggy handling
# of matching the pattern against the symlinks file.
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools


#
# This macro creates a kernel-<subpackage>-debuginfo package.
#	%%kernel_debuginfo_package <subpackage>
#
%define kernel_debuginfo_package() \
%package %{?1:%{1}-}debuginfo\
Summary: Debug information for package %{name}%{?1:-%{1}}\
Group: Development/Debug\
Requires: %{name}-debuginfo-common-%{_target_cpu} = %{version}-%{release}\
Provides: %{name}%{?1:-%{1}}-debuginfo-%{_target_cpu} = %{version}-%{release}\
AutoReqProv: no\
%description -n %{name}%{?1:-%{1}}-debuginfo\
This package provides debug information for package %{name}%{?1:-%{1}}.\
This is required to use SystemTap with %{name}%{?1:-%{1}}-%{KVERREL}.\
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:[+]%{1}}/.*|/.*%%{KVERREL}%{?1:\+%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
%{nil}

#
# This macro creates a kernel-<subpackage>-devel package.
#	%%kernel_devel_package <subpackage> <pretty-name>
#
%define kernel_devel_package() \
%package %{?1:%{1}-}devel\
Summary: Development package for building kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-devel-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules-extra package.
#	%%kernel_modules_extra_package <subpackage> <pretty-name>
#
%define kernel_modules_extra_package() \
%package %{?1:%{1}-}modules-extra\
Summary: Extra kernel modules to match the %{?2:%{2} }kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}\
Provides: kernel%{?1:-%{1}}-modules-extra-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel%{?1:-%{1}}-modules-extra = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description -n kernel%{?variant}%{?1:-%{1}}-modules-extra\
This package provides less commonly used kernel modules for the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage>-modules package.
#	%%kernel_modules_package <subpackage> <pretty-name>
#
%define kernel_modules_package() \
%package %{?1:%{1}-}modules\
Summary: kernel modules to match the %{?2:%{2}-}core kernel\
Group: System Environment/Kernel\
Provides: kernel%{?1:-%{1}}-modules-%{_target_cpu} = %{version}-%{release}\
Provides: kernel-modules-%{_target_cpu} = %{version}-%{release}%{?1:+%{1}}\
Provides: kernel-modules = %{version}-%{release}%{?1:+%{1}}\
Provides: installonlypkg(kernel-module)\
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description -n kernel%{?variant}%{?1:-%{1}}-modules\
This package provides commonly used kernel modules for the %{?2:%{2}-}core kernel package.\
%{nil}

#
# this macro creates a kernel-<subpackage> meta package.
#	%%kernel_meta_package <subpackage>
#
%define kernel_meta_package() \
%package %{1}\
summary: kernel meta-package for the %{1} kernel\
group: system environment/kernel\
Requires: kernel-%{1}-%{?variant:%{variant}-}core-uname-r = %{KVERREL}%{?variant}+%{1}\
Requires: kernel-%{1}-%{?variant:%{variant}-}modules-uname-r = %{KVERREL}%{?variant}+%{1}\
%description %{1}\
The meta-package for the %{1} kernel\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %{?1:%{1}-}core\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?1:+%{1}}\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%if %{with_extra}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%endif\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

%define variant_summary The Linux kernel compiled for SMP machines
%kernel_variant_package -n SMP smp
%description smp-core
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.

%ifnarch armv7hl
%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.
%else
%define variant_summary The Linux kernel compiled for Cortex-A15
%kernel_variant_package %{pae}
%description %{pae}-core
This package includes a version of the Linux kernel with support for
Cortex-A15 devices with LPAE and HW virtualisation support
%endif


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package %{pae}debug
Obsoletes: kernel-PAE-debug
%description %{pae}debug-core
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug-core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.

# And finally the main -core package

%define variant_summary The Linux kernel
%kernel_variant_package 
%description core
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_up}%{with_pae}
echo "Cannot build --with baseonly, up build is disabled"
exit 1
%endif
%endif

%if %{with_smponly}
%if !%{with_smp}
echo "Cannot build --with smponly, smp build is disabled"
exit 1
%endif
%endif

%if "%{baserelease}" == "0"
echo "baserelease must be greater than zero"
exit 1
%endif

# more sanity checking; do it quietly
if [ "%{patches}" != "%%{patches}" ] ; then
  for patch in %{patches} ; do
    if [ ! -f $patch ] ; then
      echo "ERROR: Patch  ${patch##/*/}  listed in specfile but is missing"
      exit 1
    fi
  done
fi 2>/dev/null

patch_command='patch -p1 -F1 -s'
ApplyPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz)  gunzip  < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.xz)  unxz    < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *) $patch_command ${1+"$@"} < "$RPM_SOURCE_DIR/$patch" ;;
  esac
}

# don't apply patch if it's empty
ApplyOptionalPatch()
{
  local patch=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  local C=$(wc -l $RPM_SOURCE_DIR/$patch | awk '{print $1}')
  if [ "$C" -gt 9 ]; then
    ApplyPatch $patch ${1+"$@"}
  fi
}

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 3.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 3.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 3.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-3.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

# Delete all old stale trees.
if [ -d kernel-%{kversion}%{?dist} ]; then
  cd kernel-%{kversion}%{?dist}
  for i in linux-*
  do
     if [ -d $i ]; then
       # Just in case we ctrl-c'd a prep already
       rm -rf deleteme.%{_target_cpu}
       # Move away the stale away, and delete in background.
       mv $i deleteme-$i
       rm -rf deleteme* &
     fi
  done
  cd ..
fi

# Generate new tree
if [ ! -d kernel-%{kversion}%{?dist}/vanilla-%{vanillaversion} ]; then

  if [ -d kernel-%{kversion}%{?dist}/vanilla-%{kversion} ]; then

    # The base vanilla version already exists.
    cd kernel-%{kversion}%{?dist}

    # Any vanilla-* directories other than the base one are stale.
    for dir in vanilla-*; do
      [ "$dir" = vanilla-%{kversion} ] || rm -rf $dir &
    done

  else

    rm -f pax_global_header
    # Look for an identical base vanilla dir that can be hardlinked.
    for sharedir in $sharedirs ; do
      if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
        break
      fi
    done
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{kversion} ]] ; then
%setup -q -n kernel-%{kversion}%{?dist} -c -T
      cp -al $sharedir/vanilla-%{kversion} .
    else
%setup -q -n kernel-%{kversion}%{?dist} -c
      mv linux-%{kversion} vanilla-%{kversion}
    fi

  fi

%if "%{kversion}" != "%{vanillaversion}"

  for sharedir in $sharedirs ; do
    if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then
      break
    fi
  done
  if [[ ! -z $sharedir  &&  -d $sharedir/vanilla-%{vanillaversion} ]] ; then

    cp -al $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -al vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
    ApplyPatch patch-3.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-3.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif

    cd ..

  fi

%endif

else

  # We already have all vanilla dirs, just change to the top-level directory.
  cd kernel-%{kversion}%{?dist}

fi

# Now build the fedora kernel tree.
cp -al vanilla-%{vanillaversion} linux-%{KVERREL}

cd linux-%{KVERREL}

# released_kernel with possible stable updates
%if 0%{?stable_base}
ApplyPatch %{stable_patch_00}
%endif

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .

%if !%{debugbuildsenabled}
%if %{with_release}
# The normal build is a really debug build and the user has explicitly requested
# a release kernel. Change the config files into non-debug versions.
make -f %{SOURCE19} config-release
%endif
%endif

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done
%endif

ApplyPatch makefile-after_link.patch

#
# misc small stuff to make things compile
#
ApplyOptionalPatch compile-fixes.patch

%if !%{nopatches}

# revert patches from upstream that conflict or that we get via other means
ApplyOptionalPatch upstream-reverts.patch -R

# Architecture patches
# x86(-64)
ApplyPatch 0001-lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

# ARM64

#
# ARM
#
ApplyPatch arm-tegra-usb-no-reset-linux33.patch

#
# bugfixes to drivers and filesystems
#

# ext4

# xfs

# btrfs

# eCryptfs

# NFSv4

# USB

# WMI

# ACPI

#
# PCI
#

#
# SCSI Bits.
#

# ACPI

# ALSA

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

ApplyPatch no-pcspkr-modalias.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch silence-noise.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch silence-fbcon-logo.patch

# Changes to upstream defaults.

#rhbz 917708
ApplyPatch Revert-userns-Allow-unprivileged-users-to-create-use.patch

# /dev/crash driver.
ApplyPatch crash-driver.patch

# crypto/

# secure boot
ApplyPatch secure-modules.patch
ApplyPatch modsign-uefi.patch
ApplyPatch sb-hibernate.patch
ApplyPatch sysrq-secure-boot.patch

# Assorted Virt Fixes

# DRM core

# Nouveau DRM

# Intel DRM
ApplyPatch drm-i915-hush-check-crtc-state.patch

# Radeon DRM

# Patches headed upstream
ApplyPatch disable-i8042-check-on-apple-mac.patch

# FIXME: REBASE
#ApplyPatch hibernate-freeze-filesystems.patch

ApplyPatch lis3-improve-handling-of-null-rate.patch

# Disable watchdog on virtual machines.
ApplyPatch nowatchdog-on-virt.patch

#rhbz 754518
ApplyPatch scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

#pplyPatch weird-root-dentry-name-debug.patch

# https://fedoraproject.org/wiki/Features/Checkpoint_Restore
ApplyPatch criu-no-expert.patch

#rhbz 892811
ApplyPatch ath9k_rx_dma_stop_check.patch

ApplyPatch drm-radeon-Disable-writeback-by-default-on-ppc.patch

#rhbz 1025603
ApplyPatch disable-libdw-unwind-on-non-x86.patch

#rhbz 983342 1093120
ApplyPatch 0001-acpi-video-Add-4-new-models-to-the-use_native_backli.patch

ApplyPatch perf-lib64.patch

# Patch series from Hans for various backlight and platform driver fixes
ApplyPatch samsung-laptop-Add-broken-acpi-video-quirk-for-NC210.patch
ApplyPatch asus-wmi-Add-a-no-backlight-quirk.patch
ApplyPatch eeepc-wmi-Add-no-backlight-quirk-for-Asus-H87I-PLUS-.patch
ApplyPatch acpi-video-Add-use-native-backlight-quirk-for-the-Th.patch
ApplyPatch acpi-video-Add-use_native_backlight-quirk-for-HP-Pro.patch

ApplyPatch x86-vdso-Fix-vdso_install.patch

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

%define make make %{?cross_opts}

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make ARCH=$Arch oldnoconfig
  echo "# $Arch" > configs/$i
  cat .config >> configs/$i
done
# end of kernel config
%endif

# get rid of unwanted files resulting from patch fuzz
find . \( -name "*.orig" -o -name "*~" \) -exec rm -f {} \; >/dev/null

# remove unnecessary SCM files
find . -name .gitignore -exec rm -f {} \; >/dev/null

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{with_debuginfo}
# This override tweaks the kernel makefiles so that we run debugedit on an
# object before embedding it.  When we later run find-debuginfo.sh, it will
# run debugedit again.  The edits it does change the build ID bits embedded
# in the stripped object, but repeating debugedit is a no-op.  We do it
# beforehand to get the proper final build ID bits into the embedded image.
# This affects the vDSO images in vmlinux, and the vmlinux image in bzImage.
export AFTER_LINK=\
'sh -xc "/usr/lib/rpm/debugedit -b $$RPM_BUILD_DIR -d /usr/src/debug \
    				-i $@ > $@.id"'
%endif

cp_vmlinux()
{
  eu-strip --remove-comment -o "$2" "$1"
}

BuildKernel() {
    MakeTarget=$1
    KernelImage=$2
    Flavour=$3
    Flav=${Flavour:++${Flavour}}
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flav}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flav}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    %if 0%{?stable_update}
    # make sure SUBLEVEL is incremented on a stable release.  Sigh 3.x.
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{?stablerev}/" Makefile
    %endif

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flav}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    %if %{signmodules}
    cp %{SOURCE11} .
    %endif

    chmod +x scripts/sign-file

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

%ifarch %{arm} aarch64
    %{make} -s ARCH=$Arch V=1 dtbs
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    install -m 644 arch/$Arch/boot/dts/*.dtb $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer/
    rm -f arch/$Arch/boot/dts/*.dtb
%endif

    # Start installing the results
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/boot
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif
    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
    fi
    %if %{signmodules}
    # Sign the image if we're using EFI
    %pesign -s -i $KernelImage -o vmlinuz.signed
    if [ ! -s vmlinuz.signed ]; then
        echo "pesigning failed"
        exit 1
    fi
    mv vmlinuz.signed $KernelImage
    %endif
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # we'll get it from the linux-firmware package and we don't want conflicts
    %{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=

%ifarch %{vdso_arches}
    %{make} -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
    if [ ! -s ldconfig-kernel.conf ]; then
      echo > ldconfig-kernel.conf "\
# Placeholder file, no vDSO hwcap entries used in this kernel."
    fi
    %{__install} -D -m 444 ldconfig-kernel.conf \
        $RPM_BUILD_ROOT/etc/ld.so.conf.d/kernel-$KernelVer.conf
%endif

    # And save the headers/makefiles etc for building modules against
    #
    # This all looks scary, but the end result is supposed to be:
    # * all arch relevant include/ files
    # * all Makefile/Kconfig files
    # * all script/ files

    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/source
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    (cd $RPM_BUILD_ROOT/lib/modules/$KernelVer ; ln -s build source)
    # dirs for additional modules per module-init-tools, kbuild/modules.txt
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/extra
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/updates
    # first copy everything
    cp --parents `find  -type f -name "Makefile*" -o -name "Kconfig*"` $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp Module.symvers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -s Module.markers ]; then
      cp Module.markers $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    fi
    # then drop all but the needed Makefiles/Kconfig files
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Documentation
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
    cp .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    cp -a scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch ppc ppc64 ppc64p7
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Flavour}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Flavour}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h

    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{with_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    grep -F /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
        LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      if [ ! -z "$3" ]; then
        sed -r -e "/^($3)\$/d" -i $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
      fi
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt(l_|2x00)(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    ( find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name '*.ko' | xargs /sbin/modinfo -l | \
        grep -E -v 'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' ) && exit 1

    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

%if %{with_extra}
    # Call the modules-extra script to move things around
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}
%endif

    #
    # Generate the kernel-core and kernel-modules files lists
    #

    # Copy the System.map file for depmod to use, and create a backup of the
    # full module tree so we can restore it after we're done filtering
    cp System.map $RPM_BUILD_ROOT/.
    pushd $RPM_BUILD_ROOT
    mkdir restore
    cp -r lib/modules/$KernelVer/* restore/.

    # don't include anything going into k-m-e in the file lists
    rm -rf lib/modules/$KernelVer/extra

    # Find all the module files and filter them out into the core and modules
    # lists.  This actually removes anything going into -modules from the dir.
    find lib/modules/$KernelVer/kernel -name *.ko | sort -n > modules.list
	cp $RPM_SOURCE_DIR/filter-*.sh .
    %{SOURCE99} modules.list %{_target_cpu}
	rm filter-*.sh

    # Run depmod on the resulting module tree and make sure it isn't broken
    depmod -b . -aeF ./System.map $KernelVer &> depmod.out
    if [ -s depmod.out ]; then
        echo "Depmod failure"
        cat depmod.out
        exit 1
    else
        rm depmod.out
    fi
    # remove files that will be auto generated by depmod at rpm -i time
    pushd $RPM_BUILD_ROOT/lib/modules/$KernelVer/
        rm -f modules.{alias*,builtin.bin,dep*,*map,symbols*,devname,softdep}
    popd

    # Go back and find all of the various directories in the tree.  We use this
    # for the dir lists in kernel-core
    find lib/modules/$KernelVer/kernel -type d | sort -n > module-dirs.list

    # Cleanup
    rm System.map
    cp -r restore/* lib/modules/$KernelVer/.
    rm -rf restore
    popd

    # Make sure the files lists start with absolute paths or rpmbuild fails.
    # Also add in the dir entries
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/k-d.list > ../kernel${Flavour:+-${Flavour}}-modules.list
    sed -e 's/^lib*/%dir \/lib/' %{?zipsed} $RPM_BUILD_ROOT/module-dirs.list > ../kernel${Flavour:+-${Flavour}}-core.list
    sed -e 's/^lib*/\/lib/' %{?zipsed} $RPM_BUILD_ROOT/modules.list >> ../kernel${Flavour:+-${Flavour}}-core.list

    # Cleanup
    rm -f $RPM_BUILD_ROOT/k-d.list
    rm -f $RPM_BUILD_ROOT/modules.list
    rm -f $RPM_BUILD_ROOT/module-dirs.list

%if %{signmodules}
    # Save the signing keys so we can sign the modules in __modsign_install_post
    cp signing_key.priv signing_key.priv.sign${Flav}
    cp signing_key.x509 signing_key.x509.sign${Flav}
%endif

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir

    # This is going to create a broken link during the build, but we don't use
    # it after this point.  We need the link to actually point to something
    # when kernel-devel is installed, and a relative link doesn't work across
    # the F17 UsrMove feature.
    ln -sf $DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build

    # prune junk from kernel-devel
    find $RPM_BUILD_ROOT/usr/src/kernels -name ".*.cmd" -exec rm -f {} \;
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{KVERREL}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image %{pae}debug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image %{pae}
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%global perf_make \
  make -s %{?cross_opts} %{?_smp_mflags} -C tools/perf V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix}
%if %{with_perf}
# perf
%{perf_make} DESTDIR=$RPM_BUILD_ROOT all
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
%{make} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    %{make} %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch %{ix86} x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   %{make}
   popd
   pushd tools/power/x86/turbostat
   %{make}
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
pushd tools/thermal/tmon/
%{make}
popd
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke mod-sign.sh command to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.

%define __modsign_install_post \
  if [ "%{signmodules}" -eq "1" ]; then \
    if [ "%{with_pae}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+%{pae} signing_key.x509.sign+%{pae} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+debug signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_pae_debug}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign+%{pae}debug signing_key.x509.sign+%{pae}debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} signing_key.priv.sign signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
    fi \
  fi \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find $RPM_BUILD_ROOT/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi \
%{nil}

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{with_debuginfo}

%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}

%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif

%endif

#
# Disgusting hack alert! We need to ensure we sign modules *after* all
# invocations of strip occur, which is in __debug_install_post if
# find-debuginfo.sh runs, and __os_install_post if not.
#
%define __spec_install_post \
  %{?__debug_package:%{__debug_install_post}}\
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__modsign_install_post}

###
### install
###

%install

cd linux-%{KVERREL}

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT MULTILIBDIR=%{_lib} install-bin install-traceevent-plugins
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace

# python-perf extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
mkdir -p %{buildroot}/%{_mandir}/man1
pushd %{buildroot}/%{_mandir}/man1
tar -xf %{SOURCE10}
popd
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
%{make} -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
%ifarch %{ix86}
    pushd tools/power/cpupower/debug/i386
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    install -m755 centrino-decode %{buildroot}%{_bindir}/centrino-decode
    install -m755 powernow-k8-decode %{buildroot}%{_bindir}/powernow-k8-decode
    popd
%endif
chmod 0755 %{buildroot}%{_libdir}/libcpupower.so*
mkdir -p %{buildroot}%{_unitdir} %{buildroot}%{_sysconfdir}/sysconfig
install -m644 %{SOURCE2000} %{buildroot}%{_unitdir}/cpupower.service
install -m644 %{SOURCE2001} %{buildroot}%{_sysconfdir}/sysconfig/cpupower
%endif
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
pushd tools/thermal/tmon
make INSTALL_ROOT=%{buildroot} install
popd
%endif

%if %{with_bootwrapper}
make DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
%endif


###
### clean
###

%clean
rm -rf $RPM_BUILD_ROOT

###
### scripts
###

%if %{with_tools}
%post -n kernel-tools
/sbin/ldconfig

%postun -n kernel-tools
/sbin/ldconfig
%endif

#
# This macro defines a %%post script for a kernel*-devel package.
#	%%kernel_devel_post [<subpackage>]
#
%define kernel_devel_post() \
%{expand:%%post %{?1:%{1}-}devel}\
if [ -f /etc/sysconfig/kernel ]\
then\
    . /etc/sysconfig/kernel || exit $?\
fi\
if [ "$HARDLINK" != "no" -a -x /usr/sbin/hardlink ]\
then\
    (cd /usr/src/kernels/%{KVERREL}%{?1:+%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules-extra package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_extra_post [<subpackage>]
#
%define kernel_modules_extra_post() \
%{expand:%%post %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules-extra}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

#
# This macro defines a %%post script for a kernel*-modules package.
# It also defines a %%postun script that does the same thing.
#	%%kernel_modules_post [<subpackage>]
#
%define kernel_modules_post() \
%{expand:%%post %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}\
%{expand:%%postun %{?1:%{1}-}modules}\
/sbin/depmod -a %{KVERREL}%{?1:+%{1}}\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1:%{1}-}core}\
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /%{image_install_path}/vmlinuz-%{KVERREL}%{?1:+%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%if %{with_extra}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
%endif\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*:%{-v*}-}core}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1:%{1}-}core}\
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /%{image_install_path}/vmlinuz-%{KVERREL}%{?1:+%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun %{pae}
%kernel_variant_post -v %{pae} -r (kernel|kernel-smp)

%kernel_variant_post -v %{pae}debug -r (kernel|kernel-smp)
%kernel_variant_preun %{pae}debug

%kernel_variant_preun debug
%kernel_variant_post -v debug

if [ -x /sbin/ldconfig ]
then
    /sbin/ldconfig -X || exit $?
fi

###
### file lists
###

%if %{with_headers}
%files headers
%defattr(-,root,root)
/usr/include/*
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libdir}/traceevent/plugins
%{_libdir}/traceevent/plugins/*
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf
%doc linux-%{KVERREL}/tools/perf/Documentation/examples.txt

%files -n python-perf
%defattr(-,root,root)
%{python_sitearch}

%if %{with_debuginfo}
%files -f perf-debuginfo.list -n perf-debuginfo
%defattr(-,root,root)

%files -f python-perf-debuginfo.list -n python-perf-debuginfo
%defattr(-,root,root)
%endif
%endif # with_perf

%if %{with_tools}
%files -n kernel-tools -f cpupower.lang
%defattr(-,root,root)
%ifarch %{cpupowerarchs}
%{_bindir}/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/centrino-decode
%{_bindir}/powernow-k8-decode
%endif
%{_unitdir}/cpupower.service
%{_mandir}/man[1-8]/cpupower*
%config(noreplace) %{_sysconfdir}/sysconfig/cpupower
%ifarch %{ix86} x86_64
%{_bindir}/x86_energy_perf_policy
%{_mandir}/man8/x86_energy_perf_policy*
%{_bindir}/turbostat
%{_mandir}/man8/turbostat*
%endif
%{_bindir}/tmon
%endif

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.0

%files -n kernel-tools-libs-devel
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif
%endif # with_perf

# empty meta-package
%files
%defattr(-,root,root)

# This is %%{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files -f kernel-%{?2:%{2}-}core.list %{?2:%{2}-}core}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:+%{2}}\
/%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:+%{2}}.hmac \
%ifarch %{arm} aarch64\
/%{image_install_path}/dtb-%{KVERREL}%{?2:+%{2}} \
%endif\
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:+%{2}}\
/boot/config-%{KVERREL}%{?2:+%{2}}\
%ghost /boot/initramfs-%{KVERREL}%{?2:+%{2}}.img\
%dir /lib/modules\
%dir /lib/modules/%{KVERREL}%{?2:+%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:+%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:+%{2}}/build\
/lib/modules/%{KVERREL}%{?2:+%{2}}/source\
/lib/modules/%{KVERREL}%{?2:+%{2}}/updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:+%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:+%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:+%{2}}/modules.*\
%{expand:%%files -f kernel-%{?2:%{2}-}modules.list %{?2:%{2}-}modules}\
%defattr(-,root,root)\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVERREL}%{?2:+%{2}}\
%if %{with_extra}\
%{expand:%%files %{?2:%{2}-}modules-extra}\
%endif\
%defattr(-,root,root)\
/lib/modules/%{KVERREL}%{?2:+%{2}}/extra\
%if %{with_debuginfo}\
%ifnarch noarch\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%if %{?2:1} %{!?2:0}\
%{expand:%%files %{2}}\
%defattr(-,root,root)\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} %{pae}
%kernel_variant_files %{with_pae_debug} %{pae}debug

# plz don't put in a version string unless you're going to tag
# and build.
#
# 
#                        ___________________________________________________________
#                       / This branch is for Fedora 21. You probably want to commit \
#  _____ ____  _        \ to the F-20 branch instead, or in addition to this one.   /
# |  ___|___ \/ |        -----------------------------------------------------------
# | |_    __) | |             \   ^__^
# |  _|  / __/| |              \  (@@)\_______
# |_|   |_____|_|                 (__)\       )\/\
#                                    ||----w |
#                                    ||     ||
%changelog
* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git7.1
- Linux v3.15-8556-gdfb945473ae8

* Fri Jun 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git6.1
- Linux v3.15-8351-g9ee4d7a65383

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git5.1
- Linux v3.15-8163-g5b174fd6472b

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git4.1
- Linux v3.15-7926-gd53b47c08d8f

* Thu Jun 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git3.1
- Linux v3.15-7378-g14208b0ec569

* Wed Jun 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git2.1
- Linux v3.15-7283-gda85d191f58a

* Tue Jun 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.16.0-0.rc0.git1.1
- Linux v3.15-7218-g3f17ea6dea8b
- Reenable debugging options.

* Mon Jun 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-1
- Linux v3.15
- Disable debugging options.

* Mon Jun  9 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable USB_EHCI_HCD_ORION to fix USB on Marvell (fix boot for some devices)

* Fri Jun 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git4.1
- CVE-2014-3940 missing check during hugepage migration (rhbz 1104097 1105042)
- Linux v3.15-rc8-81-g951e273060d1

* Thu Jun 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git3.1
- Linux v3.15-rc8-72-g54539cd217d6

* Wed Jun 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git2.1
- Linux v3.15-rc8-58-gd2cfd3105094

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add filter-ppc64p7.sh because ppc64p7 is an entirely separate RPM arch

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git1.2
- Fixes from Hans de Goede for backlight and platform drivers on various
  machines.  (rhbz 1025690 1012674 1093171 1097436 861573)

* Tue Jun 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git1.1
- Add patch to install libtraceevent plugins from Kyle McMartin
- Linux v3.15-rc8-53-gcae61ba37b4c
- Reenable debugging options.

* Mon Jun  2 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM MMC config updates

* Mon Jun 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc8.git0.1
- Linux v3.15-rc8
- Disable debugging options.

* Sat May 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git4.2
- Add patch to fix dentry lockdep splat

* Sat May 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git4.1
- Linux v3.15-rc7-102-g1487385edb55

* Fri May 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git3.1
- Linux v3.15-rc7-79-gfe45736f4134
- Disable CARL9170 on ppc64le

* Thu May 29 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-3917 DoS with syscall auditing (rhbz 1102571 1102715)

* Wed May 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git2.1
- Linux v3.15-rc7-53-g4efdedca9326

* Wed May 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git1.1
- Linux v3.15-rc7-40-gcd79bde29f00
- Reenable debugging options.

* Mon May 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc7.git0.1
- Linux v3.15-rc7
- Disable debugging options.

* Sun May 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc6.git1.1
- Linux v3.15-rc6-213-gdb1003f23189
- Reenable debugging options.

* Thu May 22 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CONFIG_R8723AU (rhbz 1100162)

* Thu May 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc6.git0.1
- Linux v3.15-rc6
- Disable debugging options.

* Wed May 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git4.1
- Linux v3.15-rc5-270-gfba69f042ad9

* Tue May 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git3.1
- Linux v3.15-rc5-157-g60b5f90d0fac

* Mon May 19 2014 Dan Horák <dan@danny.cz>
- kernel metapackage shouldn't depend on subpackages we don't build

* Thu May 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.9
- Fix build fail on s390x

* Wed May 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.8
- Enable autoprov for kernel module Provides (rhbz 1058331)
- Enable xz compressed modules (from Kyle McMartin)

* Tue May 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Don't try and merge local config changes on arches we aren't building

* Tue May 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git2.1
- Linux v3.15-rc5-77-g14186fea0cb0

* Mon May 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git1.1
- Linux v3.15-rc5-9-g7e338c9991ec
- Reenable debugging options.

* Sat May 10 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Marvell Dove support
- Minor ARM cleanups
- Disable some unneed drivers on ARM

* Sat May 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc5.git0.1
- Linux v3.15-rc5
- Disable debugging options.

* Fri May 09 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Move isofs to kernel-core

* Fri May 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git4.1
- Linux v3.15-rc4-320-gafcf0a2d9289

* Thu May 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git3.1
- Linux v3.15-rc4-298-g9f1eb57dc706

* Wed May 07 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git2.1
- Linux v3.15-rc4-260-g38583f095c5a

* Tue May 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git1.1
- Linux v3.15-rc4-202-g30321c7b658a
- Reenable debugging options.

* Mon May  5 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix some USB on ARM LPAE kernels

* Mon May 05 2014 Kyle McMartin <kyle@fedoraproject.org>
- Install arch/arm/include/asm/xen headers on aarch64, since the headers in
  arch/arm64/include/asm/xen reference them.

* Mon May 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc4.git0.1
- Linux v3.15-rc4
- Disable debugging options.

* Mon May  5 2014 Hans de Goede <hdegoede@redhat.com>
- Add use_native_brightness quirk for the ThinkPad T530 (rhbz 1089545)

* Sun May  4 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- General minor ARM cleanups

* Sun May 04 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix k-m-e requires on k-m-uname-r provides
- ONE MORE TIME WITH FEELING

* Sat May  3 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable OMAP-3 boards (use DT) and some minor omap3 config updates

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git5.1
- Linux v3.15-rc3-159-g6c6ca9c2a5b9

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix HID rmi driver from Benjamin Tissoires (rhbz 1090161)

* Sat May 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix up Provides on kernel-module variant packages
- Enable CONFIG_USB_UAS unconditionally per Hans

* Fri May 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git4.1
- Linux v3.15-rc3-121-gb7270cce7db7

* Thu May 01 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Rename kernel-drivers to kernel-modules
- Add kernel metapackages for all flavors, not just debug

* Thu May  1 2014 Hans de Goede <hdegoede@redhat.com>
- Add use_native_backlight quirk for 4 laptops (rhbz 983342 1093120)

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git3.1
- Linux v3.15-rc3-82-g8aa9e85adac6

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add kernel-debug metapackage when debugbuildsenabled is set

* Wed Apr 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git2.1
- Linux v3.15-rc3-62-ged8c37e158cb
- Drop noarch from ExclusiveArch.  Nothing is built as noarch

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git1.10
- Make depmod call fatal if it errors or warns

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Introduce kernel-core/kernel-drivers split for F21 Feature work

* Tue Apr 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git1.1
- Linux v3.15-rc3-41-g2aafe1a4d451
- Reenable debugging options.

* Mon Apr 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc3.git0.1
- Linux v3.15-rc3
- Disable debugging options.

* Fri Apr 25 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop obsolete ARM LPAE patches

* Fri Apr 25 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Will Woods to fix fanotify EOVERFLOW issue (rhbz 696821)
- Fix ACPI issue preventing boot on AMI firmware (rhbz 1090746)

* Fri Apr 25 2014 Hans de Goede <hdegoede@redhat.com>
- Add synaptics min-max quirk for ThinkPad Edge E431 (rhbz#1089689)

* Fri Apr 25 2014 Hans de Goede <hdegoede@redhat.com>
- Add a patch to add support for the mmc controller on sunxi ARM SoCs

* Thu Apr 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git3.1
- Linux v3.15-rc2-107-g76429f1dedbc

* Wed Apr 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git2.1
- Linux v3.15-rc2-69-g1aae31c8306e

* Tue Apr 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git1.1
- Linux v3.15-rc2-42-g4d0fa8a0f012
- Reenable debugging options.

* Tue Apr 22 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix Synaptics touchscreens and HID rmi driver (rhbz 1089583)

* Mon Apr 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc2.git0.1
- Linux v3.15-rc2
- Disable debugging options.

* Fri Apr 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git4.1
- Linux v3.15-rc1-137-g81cef0fe19e0

* Thu Apr 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git3.1
- Linux v3.15-rc1-113-g6ca2a88ad820
- Build perf with unwind support via libdw (rhbz 1025603)

* Thu Apr 17 2014 Hans de Goede <hdegoede@redhat.com>
- Update min/max quirk patch to add a quirk for the ThinkPad L540 (rhbz1088588)

* Thu Apr 17 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop OMAP DRM hack to load encoder module now it fully supports DT (YAY!)

* Wed Apr 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git2.1
- Linux v3.15-rc1-49-g10ec34fcb100

* Tue Apr 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git1.1
- Linux v3.15-rc1-12-g55101e2d6ce1
- Reenable debugging options.

* Mon Apr 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc1.git0.1
- Linux v3.15-rc1
- Disable debugging options.
- Turn SLUB_DEBUG off

* Mon Apr 14 2014 Hans de Goede <hdegoede@redhat.com>
- Add min/max quirks for various new Thinkpad touchpads (rhbz 1085582 1085697)

* Mon Apr 14 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config changes and cleanups for 3.15 merge window

* Mon Apr 14 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-2851 net ipv4 ping refcount issue in ping_init_sock (rhbz 1086730 1087420)

* Sun Apr 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git13.1
- Linux v3.14-12812-g321d03c86732

* Fri Apr 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git12.1
- Linux v3.14-12380-g9e897e13bd46
- Add queued urgent efi fixes (rhbz 1085349)

* Thu Apr 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git11.1
- Linux v3.14-12376-g4ba85265790b

* Thu Apr 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Backported HID RMI driver for Haswell Dell XPS machines from Benjamin Tissoires (rhbz 1048314)

* Wed Apr 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git10.1
- Linux v3.14-12042-g69cd9eba3886

* Wed Apr 09 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-0155 KVM: BUG caused by invalid guest ioapic redirect table (rhbz 1081589 1085016)

* Thu Apr 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git9.1
- Linux v3.14-7333-g59ecc26004e7

* Thu Apr 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git8.1
- Linux v3.14-7247-gcd6362befe4c

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git7.1
- Linux v3.14-5146-g0f1b1e6d73cb

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git6.1
- Linux v3.14-4600-g467cbd207abd

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git5.1
- Linux v3.14-4555-gb33ce4429938

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git4.1
- Linux v3.14-4227-g3e75c6de1ac3

* Wed Apr 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git3.1
- Linux v3.14-3893-gc12e69c6aaf7

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git2.1
- CVE-2014-2678 net: rds: deref of NULL dev in rds_iw_laddr_check (rhbz 1083274 1083280)

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> 
- Linux v3.14-751-g683b6c6f82a6

* Tue Apr 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.15.0-0.rc0.git1.1
- Linux v3.14-313-g918d80a13643
- Reenable debugging options.
- Turn on SLUB_DEBUG

* Mon Mar 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-1
- Linux v3.14
- Disable debugging options.

* Mon Mar 31 2014 Hans de Goede <hdegoede@redhat.com>
- Fix clicks getting lost with cypress_ps2 touchpads with recent
  xorg-x11-drv-synaptics versions (bfdo#76341)

* Fri Mar 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc8.git1.1
- CVE-2014-2580 xen: netback crash trying to disable due to malformed packet (rhbz 1080084 1080086)
- CVE-2014-0077 vhost-net: insufficent big packet handling in handle_rx (rhbz 1064440 1081504)
- CVE-2014-0055 vhost-net: insufficent error handling in get_rx_bufs (rhbz 1062577 1081503)
- CVE-2014-2568 net: potential info leak when ubuf backed skbs are zero copied (rhbz 1079012 1079013)

* Fri Mar 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.14-rc8-12-g75c5a52
- Reenable debugging options.

* Fri Mar 28 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Tegra 114/124 SoCs
- Re-enable OMAP cpufreq
- Re-enable CPSW PTP option

* Thu Mar 27 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Switch to CONFIG_TRANSPARENT_HUGEPAGE_MADVISE instead of always on

* Tue Mar 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc8.git0.1
- Linux v3.14-rc8
- Disable debugging options.

* Mon Mar 24 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Update some generic ARM config options
- Build in TPS65217 for ARM non lpae kernels (fixes BBW booting)

* Fri Mar 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git2.1
- Linux v3.14-rc7-59-g08edb33

* Wed Mar 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git1.1
- Linux v3.14-rc7-26-g4907cdc
- Reenable debugging options.

* Tue Mar 18 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable TEGRA_FBDEV (rhbz 1073960)

* Mon Mar 17 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add bootwrapper for ppc64le

* Mon Mar 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc7.git0.1
- Linux v3.14-rc7
- Disable debugging options.

* Mon Mar 17 2014 Peter Robinson <pbrobinson@fedoraproject.org> 
- Build in Palmas regulator on ARM to fix ext MMC boot on OMAP5

* Fri Mar 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git4.1
- Linux v3.14-rc6-133-gc60f7d5

* Thu Mar 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git3.1
- Linux v3.14-rc6-41-gac9dc67

* Wed Mar 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git2.1
- Fix locking issue in iwldvm (rhbz 1046495)
- Linux v3.14-rc6-26-g33807f4

* Wed Mar 12 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Add some general missing ARM drivers (mostly sound)
- ARM config tweaks and cleanups
- Update i.MX6 dtb

* Tue Mar 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git1.1
- CVE-2014-2309 ipv6: crash due to router advertisment flooding (rhbz 1074471 1075064)
- Linux v3.14-rc6-17-g8712a00
- Reenable debugging options.

* Mon Mar 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc6.git0.1
- Linux v3.14-rc6
- Disable debugging options.

* Fri Mar 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Revert two xhci fixes that break USB mass storage (rhbz 1073180)

* Thu Mar 06 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix stale EC events on Samsung systems (rhbz 1003602)
- Add ppc64le support from Brent Baude (rhbz 1073102)
- Fix depmod error message from hci_vhci module (rhbz 1051748)
- Fix bogus WARN in iwlwifi (rhbz 1071998)

* Wed Mar 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git2.1
- Linux v3.14-rc5-185-gc3bebc7

* Tue Mar 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git1.1
- Linux v3.14-rc5-43-g0c0bd34
- Reenable debugging options.

* Mon Mar 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc5.git0.1
- Linux v3.14-rc5
- Disable debugging options.

* Fri Feb 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git3.1
- Linux v3.14-rc4-78-gd8efcf3

* Fri Feb 28 2014 Kyle McMartin <kyle@fedoraproject.org>
- Enable appropriate CONFIG_XZ_DEC_$arch options to ensure we can mount
  squashfs images on supported architectures.

* Fri Feb 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-0102 keyctl_link can be used to cause an oops (rhbz 1071396)

* Thu Feb 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git2.1
- Linux v3.14-rc4-45-gd2a0476

* Wed Feb 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git1.1
- Linux v3.14-rc4-34-g6dba6ec
- Reenable debugging options.

* Wed Feb 26 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Re-enable KVM on aarch64 now it builds again

* Tue Feb 25 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix mounting issues on cifs (rhbz 1068862)

* Mon Feb 24 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix lockdep issue in EHCI when using threaded IRQs (rhbz 1056170)

* Mon Feb 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc4.git0.1
- Linux v3.14-rc4
- Disable debugging options.

* Thu Feb 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git5.1
- Linux v3.14-rc3-219-gd158fc7

* Thu Feb 20 2014 Kyle McMartin <kyle@fedoraproject.org>
- armv7: disable CONFIG_DEBUG_SET_MODULE_RONX until debugged (rhbz#1067113)

* Thu Feb 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git4.1
- Linux v3.14-rc3-184-ge95003c

* Wed Feb 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git3.1
- Linux v3.14-rc3-168-g960dfc4

* Tue Feb 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git2.1
- Linux v3.14-rc3-43-g805937c

* Tue Feb 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git1.1
- Linux v3.14-rc3-20-g60f76ea
- Reenable debugging options.
- Fix r8169 ethernet after suspend (rhbz 1054408)
- Enable INTEL_MIC drivers (rhbz 1064086)

* Mon Feb 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc3.git0.1
- Linux v3.14-rc3
- Disable debugging options.
- Enable CONFIG_PPC_DENORMALIZATION (from Tony Breeds)

* Fri Feb 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git4.1
- Linux v3.14-rc2-342-g5e57dc8
- CVE-2014-0069 cifs: incorrect handling of bogus user pointers (rhbz 1064253 1062578)

* Thu Feb 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git3.1
- Linux v3.14-rc2-271-g4675348

* Wed Feb 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git2.1
- Linux v3.14-rc2-267-g9398a10

* Wed Feb 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix cgroup destroy oops (rhbz 1045755)
- Fix backtrace in amd_e400_idle (rhbz 1031296)

* Tue Feb 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git1.1
- Linux v3.14-rc2-26-g6792dfe
- Reenable debugging options.

* Mon Feb 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc2.git0.1
- Linux v3.14-rc2
- Disable debugging options.

* Sun Feb  9 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable CMA on aarch64
- Disable KVM temporarily on aarch64
- Minor ARM config updates and cleanups

* Sun Feb 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git5.1.1
- Linux v3.14-rc1-182-g4944790

* Sat Feb 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git4.1
- Linux v3.14-rc1-150-g34a9bff

* Fri Feb 07 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git3.1
- Linux v3.14-rc1-86-g9343224

* Thu Feb 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git2.1
- Linux v3.14-rc1-54-gef42c58

* Wed Feb 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git1.1
- Linux v3.14-rc1-13-g878a876

* Tue Feb 04 2014 Kyle McMartin <kyle@fedoraproject.org>
- Fix %all_arch_configs on aarch64.

* Tue Feb 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git0.2
- Add NUMA oops patches
- Reenable debugging options.

* Mon Feb 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc1.git0.1
- Linux v3.14-rc1
- Disable debugging options.
- Disable Xen on ARM temporarily as it doesn't build

* Mon Feb  3 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Re-enable modular Tegra DRM driver
- Add SD driver for ZYNQ SoCs

* Fri Jan 31 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git19.1
- Linux v3.13-10637-ge7651b8
- Enable ZRAM/ZSMALLOC (rhbz 1058072)
- Turn EXYNOS_HDMI back on now that it should build

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git18.1
- Linux v3.13-10231-g53d8ab2

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git17.1
- Linux v3.13-10094-g9b0cd30
- Add patches to fix imx-hdmi build, and fix kernfs lockdep oops (rhbz 1055105)

* Thu Jan 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git16.1
- Linux v3.13-9240-g1329311

* Wed Jan 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git15.1
- Linux v3.13-9218-g0e47c96

* Tue Jan 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git14.1
- Linux v3.13-8905-g627f4b3

* Tue Jan 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git13.1
- Linux v3.13-8789-g54c0a4b
- Enable CONFIG_CC_STACKPROTECTOR_STRONG on x86

* Mon Jan 27 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Build AllWinner (sunxi) on LPAE too (Cortex-A7 supports LPAE/KVM)

* Mon Jan 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git12.1
- Linux v3.13-8631-gba635f8

* Mon Jan 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git11.1
- Linux v3.13-8598-g77d143d

* Sat Jan 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git10.1
- Linux v3.13-8330-g4ba9920

* Sat Jan 25 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git9.1
- Linux v3.13-6058-g2d08cd0
- Quiet incorrect usb phy error (rhbz 1057529)

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi>
- Own the /lib/modules dir.

* Sat Jan 25 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial ARM config updates for 3.14
- Disable highbank cpuidle driver
- Enable mtd-nand drivers on ARM
- Update CPU thermal scaling options for ARM

* Fri Jan 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git8.1
- Linux v3.13-5617-g3aacd62

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git7.1
- Linux v3.13-4156-g90804ed

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git6.1.1
- Revert fsnotify changes as they cause slab corruption for multiple people
- Linux v3.13-3995-g0dc3fd0

* Thu Jan 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git5.1
- Linux v3.13-3667-ge1ba845

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git4.1
- Linux v3.13-3477-gdf32e43

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git3.1
- Linux v3.13-3260-g03d11a0

* Wed Jan 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git2.1
- Linux v3.13-2502-gec513b1

* Tue Jan 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.14.0-0.rc0.git1.1
- Linux v3.13-737-g7fe67a1
- Reenable debugging options.  Enable SLUB_DEBUG

* Mon Jan 20 2014 Kyle McMartin <kyle@fedoraproject.org>
- Enable CONFIG_KVM on AArch64.

* Mon Jan 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-1
- Linux v3.13
- Disable debugging options.
- Use versioned perf man pages tarball

* Sat Jan 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc8.git4.1
- Linux v3.13-rc8-76-g7d0d46d

* Sat Jan 18 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable ARM_GLOBAL_TIMER on ARM used by a number of Cortex-A9 and later platforms

* Thu Jan 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc8.git3.1
- Linux v3.13-rc8-46-g85ce70f

* Wed Jan 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc8.git2.1.1
- Linux v3.13-rc8-27-g2e67c56

* Tue Jan 14 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix k-m-e Provides to be explicit to only the package flavor (rhbz 1046246)

* Tue Jan 14 2014 Kyle McMartin <kyle@fedoraproject.org>
- aarch64: enable 4K pages and CONFIG_COMPAT.

* Mon Jan 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc8.git1.1
- Linux v3.13-rc8-5-ga6da83f
- Reenable debugging options.

* Sun Jan 12 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates and cleanups
- Enable generic cpufreq-cpu0 driver on ARM
- Enable thermal userspace support for ARM

* Sun Jan 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc8.git0.1
- Linux v3.13-rc8
- Disable debugging options.

* Sat Jan 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc7.git5.1
- Linux v3.13-rc7-126-g228fdc0

* Fri Jan 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc7.git4.1
- Linux v3.13-rc7-87-g21e20e2

* Thu Jan 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc7.git3.1
- Linux v3.13-rc7-72-g7d1c153

* Wed Jan 08 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Disable aic94xx driver (from Paul Bolle)
- Backport support for ALPS Dolphin devices (rhbz 953211)

* Wed Jan 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc7.git2.1
- Linux v3.13-rc7-67-gceb3b02
- Enable BCMA_DRIVER_GPIO by turning on GPIOLIB everywhere (rhbz 1021098)

* Tue Jan 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Drop -doc subpackage

* Tue Jan 07 2014 Josh Boyer <jwboyer@fedoraproject.com> - 3.13.0-0.rc7.git1.1
- Linux v3.13-rc7-55-gef350bb
- Reenable debugging options.

* Tue Jan 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Change DEFAULT_MMAP_MIN_ADDR to 64k on x86_64

* Mon Jan 06 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add support for Wacom Intuos 5 S devices (rhbz 1046238)
- Fix use after free crash in KVM (rhbz 1047892)
- Fix oops in KVM with invalid root_hpa (rhbz 924916)

* Sun Jan 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.13-0.0.rc7.git0.1
- Linux v3.13-rc7
- Fix xen-netback build failure on ARM

* Mon Dec 30 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc6.git0.1
- Linux v3.13-rc6

* Mon Dec 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc5.git0.1
- Linux v3.13-rc5
- Disable debugging options.

* Sat Dec 21 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git5.1
- Linux v3.13-rc4-256-gb7000ad

* Fri Dec 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix dummy gssd entry (rhbz 1037793)

* Thu Dec 19 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git4.1
- Linux v3.13-rc4-144-ga36c160

* Thu Dec 19 2013 Josh Boyer <jwboyer@fedoraproject.org>
- copy kernel trees around with 'cp -al' so symlinks are preserved.  Fixes
  weird build failures with coreutils 8.22 (rhbz 1044801)

* Wed Dec 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git3.1
- Linux v3.13-rc4-99-g35eecf0

* Wed Dec 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git2.1
- Linux v3.13-rc4-38-gb0031f2

* Wed Dec 18 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Reenable MEMORY_HOTPLUG on x86_64
- Fix nowatchdog-on-virt.patch to actually work in KVM guests

* Tue Dec 17 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git1.1
- Linux v3.13-rc4-21-g0eda402
- Reenable debugging options.

* Mon Dec 16 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc4.git0.1
- Linux v3.13-rc4
- Disable debugging options.

* Sat Dec 14 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git5.1
- Linux v3.13-rc3-362-gb2077eb

* Sat Dec 14 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Wrap doc BR in with_doc
- Stop building perf in build AND install because that's stupid
- Use prebuilt perf man pages

* Fri Dec 13 2013 Josh Boyer <jwboyer@fedoraproject.org>
- More keys fixes from upstream to fix keyctl_get_persisent crash (rhbz 1043033)

* Fri Dec 13 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git4.1
- Linux v3.13-rc3-302-g8d27637

* Thu Dec 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git3.1
- Linux v3.13-rc3-249-g2208f65

* Thu Dec 12 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4587 kvm: out-of-bounds access (rhbz 1030986 1042071)
- CVE-2013-6376 kvm: BUG_ON in apic_cluster_id (rhbz 1033106 1042099)
- CVE-2013-6368 kvm: cross page vapic_addr access (rhbz 1032210 1042090)
- CVE-2013-6367 kvm: division by 0 in apic_get_tmcct (rhbz 1032207 1042081)

* Wed Dec 11 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git2.1
- Linux v3.13-rc3-174-g9538e10

* Wed Dec 11 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to support ETPS/2 Elantech touchpads (rhbz 1030802)

* Tue Dec 10 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git1.2
- Revert upstream selinux change causing sync hang (rhbz 1033965)
- Add patch to fix radeon from crashing

* Tue Dec 10 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git1.1
- Linux v3.13-rc3-157-g17b2112
- Reenable debugging options.

* Mon Dec 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git0.1
- Linux v3.13-rc3
- Disable debugging options.

* Fri Dec 06 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git7.1
- Linux v3.13-rc2-326-g843f4f4

* Fri Dec 06 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git6.1
- Linux v3.13-rc2-295-g002acf1
- Add test fix patch for crypto backtrace (rhbz 1038472)

* Thu Dec 05 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git5.1
- Linux v3.13-rc2-265-gef1e4e3

* Thu Dec 05 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git4.1
- Linux v3.13-rc2-215-g53c6de5
- Enable PR kvm module on ppc64 (rhbz 1038541)

* Wed Dec 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git3.1
- Linux v3.13-rc2-208-g8ecffd7

* Tue Dec  3 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM cleanups and remove obsolete options

* Mon Dec 02 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git2.1
- Linux v3.13-rc2-119-ga45299e

* Mon Dec 02 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc2.git1.1
- Linux v3.13-rc2-1-gaf91706
- Reenable debugging options.

* Sat Nov 30 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates
- Enable sound compressed offload on ARM

* Fri Nov 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc3.git0.1
- Linux v3.13-rc2
- Disable debugging options.

* Fri Nov 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc1.git4.1
- Linux v3.13-rc1-252-gdda9cc3

* Tue Nov 26 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc1.git3.1
- Linux v3.13-rc1-128-g0e4b074

* Tue Nov 26 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix crash driver build and re-enable on s390x (from Dan Horák)
- CVE-2013-6382 xfs: missing check for ZERO_SIZE_PTR (rhbz 1033603 1034670)

* Mon Nov 25 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc1.git2.1
- Linux v3.13-rc1-85-g7e3528c

* Sun Nov 24 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc1.git1.1
- Linux v3.13-rc1-77-g4c1cc40
- Reenable debugging options.

* Sat Nov 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc1.git0.1
- Linux v3.13-rc1
- Disable debugging options.

* Fri Nov 22 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix ARM Utilite DTB

* Fri Nov 22 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git11.1
- Linux v3.12-11097-ga5d6e63
- Drop all the keys-* patches because they were merged upstream.  Yay!

* Thu Nov 21 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Some minor ARM config updates

* Thu Nov 21 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git10.1
- Linux v3.12-10928-g527d151
- Drop ACPI blacklist year options and patch (removed with upstream commit 4c47cb197e13 )

* Wed Nov 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git9.1
- Linux v3.12-10710-gb4789b8

* Tue Nov 19 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CGROUP_HUGETLB on ppc64/ppc64p7 and x86_64 (rhbz 1031984)

* Tue Nov 19 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git8.1
- Linux v3.12-10554-g801a760

* Tue Nov 19 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git7.1
- Linux v3.12-10553-g27b5c3f

* Sun Nov 17 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix up ARM usb gadget config to make it useful

* Sun Nov 17 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git6.1
- Linux v3.12-10087-g1213959
- Update s390x config from Dan Horák

* Sat Nov 16 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git5.1
- Linux v3.12-9888-gf63c482

* Thu Nov 14 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git4.1
- Linux v3.12-8333-g4fbf888
- Build tmon in kernel-tools
- Disable ARM NEON optimised AES and OMAP2PLUS cpufreq because they don't build

* Thu Nov 14 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM configs
- Enable ARM NEON optimised AES

* Wed Nov 13 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git3.2
- Enable USER_NS for root-only processes (rhbz 917708)

* Wed Nov 13 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git3.1
- Linux v3.12-7033-g42a2d92

* Wed Nov 13 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix imx-drm build issues

* Wed Nov 13 2013 Adam Jackson <ajax@redhat.com>
- Hush i915's check_crtc_state()

* Tue Nov 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git2.1
- Linux v3.12-4849-g10d0c97

* Mon Nov 11 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.13.0-0.rc0.git1.3
- Linux v3.12-2839-gedae583
- Reenable debugging options.

* Sat Nov 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-2
- Add patch from Daniel Stone to avoid high order allocations in evdev
- Add qxl backport fixes from Dave Airlie

* Tue Nov 05 2013 Kyle McMartin <kyle@fedoraproject.org>
- Enable crash on {arm,aarch64,ppc64,s390x}

* Mon Nov 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-1
- Linux v3.12
- Disable debugging options.

* Fri Nov 01 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc7.git4.1
- Linux v3.12-rc7-111-g9581b7d

* Fri Nov 01 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc7.git3.1
- Linux v3.12-rc7-79-g4f794ee
- Set NR_CPUS=1024 on non-debug x86_64 builds (MAXSMP is set on debug)

* Fri Nov 01 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4348 net: deadloop path in skb_flow_dissect (rhbz 1007939 1025647)

* Thu Oct 31 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc7.git2.1
- Linux v3.12-rc7-48-g12aee27

* Tue Oct 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc7.git1.1
- Linux v3.12-rc7-9-gc9ca72f
- Fixes sg_open lock held when returning to userspace (rhbz 1018620)
- Reenable debugging options.

* Mon Oct 28 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc7.git0.1
- Linux v3.12-rc7
- Disable debugging options.

* Fri Oct 25 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add touchpad support for Dell XT2 (rhbz 1023413)

* Fri Oct 25 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc6.git4.1
- Linux v3.12-rc6-292-g4208c47

* Thu Oct 24 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch for i.MX6 Utilite device dtb

* Thu Oct 24 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc6.git3.1
- Linux v3.12-rc6-284-ge6036c0

* Wed Oct 23 2013 Kyle McMartin <kyle@fedoraproject.org>
- Clean up some BuildRequires that reference hilariously old packages.
  Replace module-init-tools BR with kmod.

* Wed Oct 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc6.git2.1
- Linux v3.12-rc6-275-g320437af

* Tue Oct 22 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Build virtio drivers as modules (rhbz 1019569)

* Tue Oct 22 2013 Adam Jackson <ajax@redhat.com>
- Drop voodoo1 fbdev driver

* Tue Oct 22 2013 Kyle McMartin <kyle@fedoraproject.org>
- Clean up kernel Provides, nobody references kernel-drm, or kernel-modeset...
  drop pre-F20 ARM flavor names. Turn off AutoProv on the main kernel package.

* Tue Oct 22 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix warning in tcp_fastretrans_alert (rhbz 989251)

* Tue Oct 22 2013 Kyle McMartin <kyle@fedoraproject.org>
- armv7hl,aarch64: re-enable kernel-modules-extra temporarily

* Tue Oct 22 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc6.git1.1
- Linux v3.12-rc6-57-g69c88dc
- Reenable debugging options.

* Tue Oct 22 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config update

* Mon Oct 21 2013 Kyle McMartin <kyle@fedoraproject.org>
- aarch64: add AFTER_LINK to $vdsold for debuginfo generation of the vdso.

* Sun Oct 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Build BIG_KEYS into the kernel (rhbz 1017683)

* Sun Oct 20 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable U8500 SoC (Snowball) on ARM

* Sun Oct 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc6.git0.1
- Linux v3.12-rc6
- Disable debugging options.

* Fri Oct 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc5.git4.1
- Linux v3.12-rc5-123-g04919af

* Fri Oct 18 2013 Josh Boyer <jwboyer@fedoraproject.org> 
- Fix keyring quota misaccounting (rhbz 1017683)

* Thu Oct 17 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc5.git3.1
- Linux v3.12-rc5-78-g056cdce

* Thu Oct 17 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix BusLogic error (rhbz 1015558)
- Fix rt2800usb polling timeouts and throughput issues (rhbz 984696)

* Wed Oct 16 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix btrfs balance/scrub issue (rhbz 1011714)
- Clean up a bunch of stale patches

* Wed Oct 16 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc5.git2.1
- Linux v3.12-rc5-48-g34ec4de

* Wed Oct 16 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM config updates for IIO and enable sensors for ARM platforms

* Wed Oct 16 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Enable VIRTIO_CONSOLE as a module on all ARM (rhbz 1005551)

* Tue Oct 15 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Enable IIO and various sensor options for Win8 laptops (rhbz 995510)

* Tue Oct 15 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc5.git1.1
- Linux v3.12-rc5-36-g1e52db6
- Reenable debugging options.

* Mon Oct 14 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc5.git0.1
- Linux v3.12-rc5
- Disable debugging options.

* Sun Oct 13 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates/cleanups
- ARM GPIO/I2C updates
- ARM usb gadget updates

* Sat Oct 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc4.git4.1
- Linux v3.12-rc4-91-g46f3751

* Fri Oct 11 2013 Kyle McMartin <kyle@fedoraproject.org>
- Turn off some drivers on aarch64 and armv7hl that are unlikely to ever be
  seen there.

* Fri Oct 11 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc4.git3.1
- Fix segfault in cpupower set (rhbz 1000439)
- Linux v3.12-rc4-62-g2fe80d3

* Thu Oct 10 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix large order allocation in dm mq policy (rhbz 993744)

* Wed Oct 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc4.git2.1
- Don't trigger a stack trace on crashing iwlwifi firmware (rhbz 896695)
- Linux v3.12-rc4-29-g0e7a3ed

* Wed Oct 09 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix VFIO IOMMU crash (rhbz 998732)

* Tue Oct 8  2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Tiny ARM config update

* Tue Oct 08 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc4.git1.1
- Linux v3.12-rc4-19-g8b5ede6
- Reenable debugging options.
- Quiet irq remapping stack trace (rhbz 982153)

* Mon Oct 7  2013 Peter Robinson <pbrobinson@fedoraproject.org>
- General ARM config cleanups
- Remove old/dupe ARM config options
- Enable external connectors on ARM
- Enable i.MX and TI thermal controllers
- Enable i.MX RNG driver
- ARM MFD and REGULATOR changes and cleanups
- AM33xx (BeagleBone) config improvements
- Rebase OMAP DVI patch
- Enable console for Zynq-7xxx SoCs

* Sun Oct 06 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc4.git0.1
- Linux v3.12-rc4
- Disable debugging options.

* Fri Oct 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git5.1
- Linux v3.12-rc3-296-g15c83d2

* Thu Oct 03 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git4.1
- Linux v3.12-rc3-267-g6d15ee4

* Thu Oct 03 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to support not importing certs from db

* Thu Oct 03 2013 Kyle McMartin <kyle@fedoraproject.org>
- Add config-no-extra and disable with_extra on ARM and AArch64 to reduce
  time building untestable code (because the hardware doesn't exist, or it
  would be futile.)

* Thu Oct 03 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git3.1
- Linux v3.12-rc3-253-ge6e7fb1

* Wed Oct 02 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git2.1
- Linux v3.12-rc3-186-gc31eeac
- Enable options for Intel Low Power Subsystem Support

* Tue Oct 01 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git1.1
- Linux v3.12-rc3-65-gf927318
- Reenable debugging options.

* Mon Sep 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add support for rf3070 devices from Stanislaw Gruszka (rhbz 974072)
- Drop VC_MUTE patch (rhbz 859485)

* Mon Sep 30 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc3.git0.1
- Linux v3.12-rc3
- Disable debugging options.

* Sun Sep 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc2.git4.1
- Linux v3.12-rc2-160-g669fc2f

* Fri Sep 27 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc2.git3.1
- Linux v3.12-rc2-108-g6cac446

* Fri Sep 27 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix oops from applesmc (rhbz 1011719)
- Add patches to fix soft lockup from elevator changes (rhbz 902012)

* Thu Sep 26 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc2.git2.1
- Linux v3.12-rc2-83-g4b97280

* Wed Sep 25 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc2.git1.1
- Linux v3.12-rc2-33-g22356f4
- Reenable debugging options.

* Wed Sep 25 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix debuginfo_args regex for + separator (rhbz 1009751)
- Fix invalid value passed to pci_unmap_single in skge (rhbz 1008323)

* Tue Sep 24 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc2.git0.1
- Linux v3.12-rc2
- Disable debugging options.

* Mon Sep 23 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Revert rt2x00 commit that breaks connectivity (rhbz 1010431)

* Mon Sep 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git6.1
- Linux v3.12-rc1-336-gd8524ae

* Fri Sep 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git5.1
- Linux v3.12-rc1-250-g7b9e3a6

* Fri Sep 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix RTC updates from ntp (rhbz 985522)

* Fri Sep 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git4.1
- Linux v3.12-rc1-250-g7b9e3a6

* Thu Sep 19 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git3.1
- Linux v3.12-rc1-101-ged24fee

* Wed Sep 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git2.1
- Linux v3.12-rc1-46-g9baa505

* Wed Sep 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git1.1
- Linux v3.12-rc1-27-g62d228b
- Reenable debugging options.

* Tue Sep 17 2013 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2013-4345 ansi_cprng: off by one error in non-block size request (rhbz 1007690 1009136)

* Tue Sep 17 2013 Kyle McMartin <kyle@redhat.com>
- Add nvme.ko to modules.block for anaconda.

* Tue Sep 17 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc1.git0.1
- Linux v3.12-rc1
- Disable debugging options.

* Sun Sep 15 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git26.1
- Linux v3.11-10064-gbff157b

* Sat Sep 14 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Update keys-x509-improv.patch to latest back from upstream git

* Sat Sep 14 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git25.1
- Linux v3.11-10050-g3711d86

* Fri Sep 13 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git24.1
- Linux v3.11-10007-g399a946

* Fri Sep 13 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix btrfs build on ARM
- CVE-2013-4350 net: sctp: ipv6 ipsec encryption bug in sctp_v6_xmit (rhbz 1007872 1007903)
- CVE-2013-4343 net: use-after-free TUNSETIFF (rhbz 1007733 1007741)

* Thu Sep 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git23.1
- Linux v3.11-9747-gff812d7

* Thu Sep 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git22.1
- Linux v3.11-9420-gd5d04bb

* Thu Sep 12 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git21.1
- Linux v3.11-9411-gc2d9572

* Wed Sep 11 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git20.1
- Linux v3.11-9031-ga22a0fd

* Tue Sep 10 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git19.1
- Linux v3.11-8935-g31f7c3a

* Tue Sep 10 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git18.1
- Linux v3.11-8716-g26b0332

* Mon Sep  9 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable OF option to allocate CMA memory using device tree on ARM

* Mon Sep 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git17.1
- Linux fscache-fixes-for-ceph-8429-g300893b

* Mon Sep 09 2013 Kyle McMartin <kyle@redhat.com>
- [arm] re-enable CONFIG_PCIEPORTBUS, now that tegra is fixed upstream.

* Mon Sep 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git16.1
- Linux v3.11-7890-ge5c832d

* Mon Sep 09 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git15.1
- Linux v3.11-7547-g44598f9

* Sun Sep  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor updates to OMAP and AM33xx

* Sat Sep 07 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix ARM kernel neon build

* Fri Sep 06 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git14.1
- Linux v3.11-6855-g4de9ad9

* Fri Sep 06 2013 Kyle McMartin <kyle@redhat.com>
- [arm] enable KERNEL_MODE_NEON, safe to do, as the raid6 code tests hwcaps
  so it won't impact tegra.

* Fri Sep 06 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git13.1
- Linux v3.11-6422-g2e03285

* Thu Sep 05 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git12.1
- Linux v3.11-4809-ga09e9a7

* Thu Sep 05 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git11.1
- Fix perf build on ARM (from Kyle McMartin)

* Thu Sep 05 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.11-3891-gae7a835

* Thu Sep 05 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git10.1
- Linux v3.11-3120-g816434e

* Thu Sep 5 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fixup perf build

* Wed Sep 4 2013 Kyle McMartin <kyle@redhat.com>
- [arm] Disable CONFIG_PCIEPORTBUS in arm-generic, causes untold problems
  with registering bus windows on tegra.

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git9.1
- Linux v3.11-3070-gcb3e433

* Wed Sep 4 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Update linux-firmware requirements for newer radeon firmware (rhbz 988268 972518)

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git8.1
- Linux v3.11-2654-g458c3f6

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git7.1
- Linux v3.11-2529-ga923874

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git6.1
- Linux v3.11-2455-g40031da

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git5.1
- Linux v3.11-2200-gf66c83d

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git4.1
- Linux v3.11-1851-g7511442

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git3.1
- Linux v3.11-782-g1d1fdd9

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git2.1
- Linux v3.11-716-gb3b4911

* Wed Sep  4 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch set to fix MMC on AM33xx
- Add support for BeagleBone Black (very basic!)
- Renable cpuidle on ARM, was disabled sometime back due to instability

* Wed Sep 04 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.12.0-0.rc0.git1.1
- Linux v3.11-351-g1ccfd5e
- Reenable debugging options.

* Tue Sep 03 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-3
- Add system_keyring patches back in

* Tue Sep 03 2013 Kyle McMartin <kyle@redhat.com>
- Pull in some Calxeda highbank fixes that are destined for 3.12
- Add a %with_extra twiddle to disable building kernel-modules-extra
  subpackages.
- Fix dtbs install path to use %install_image_path (not that it's different
  at the moment.)

* Tue Sep 03 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add keyring patches to support krb5 (rhbz 1003043)

* Tue Sep 03 2013 Kyle McMartin <kyle@redhat.com>
- [arm64] disable VGA_CONSOLE and PARPORT_PC
- [arm64] install dtb as on %{arm}

* Tue Sep 03 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-1
- Linux v3.11
- Disable debugging options.

* Mon Sep 02 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git5.1
- Linux v3.11-rc7-96-ga878764

* Sun Sep  1 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Build in OMAP MMC again (fix at least omap3)

* Sat Aug 31 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git4.1
- Linux v3.11-rc7-42-gd9eda0f

* Fri Aug 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Fix HID CVEs.  Absurd.
- CVE-2013-2888 rhbz 1000451 1002543 CVE-2013-2889 rhbz 999890 1002548
- CVE-2013-2891 rhbz 999960 1002555  CVE-2013-2892 rhbz 1000429 1002570
- CVE-2013-2893 rhbz 1000414 1002575 CVE-2013-2894 rhbz 1000137 1002579
- CVE-2013-2895 rhbz 1000360 1002581 CVE-2013-2896 rhbz 1000494 1002594
- CVE-2013-2897 rhbz 1000536 1002600 CVE-2013-2899 rhbz 1000373 1002604

* Fri Aug 30 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git3.1
- Linux v3.11-rc7-30-g41615e8

* Fri Aug 30 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Rework Secure Boot support to use the secure_modules approach
- Drop pekey

* Thu Aug 29 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git2.1
- Linux v3.11-rc7-24-gc95389b
- Add mei patches that fix various s/r issues (rhbz 994824 989373)

* Wed Aug 28 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git1.1
- Linux v3.11-rc7-14-gfa8218d
- Reenable debugging options.

* Tue Aug 27 2013 Kyle McMartin <kyle@redhat.com>
- [arm] build pinctrl-single in, needed to prevent deferral of
  omap_serial registration.

* Mon Aug 26 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc7.git0.1
- Linux v3.11-rc7
- Disable debugging options.

* Fri Aug 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git4.1
- Linux v3.11-rc6-139-g89b53e5

* Fri Aug 23 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git3.1
- Linux v3.11-rc6-76-g6a7492a

* Fri Aug 23 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config cleanups
- Enable some IOMMU drivers on ARM
- Enable some i.MX sound drivers

* Thu Aug 22 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git2.1
- Linux v3.11-rc6-72-g1f8b766

* Thu Aug 22 2013 Kyle McMartin <kyle@redhat.com>
- Drop arm-tegra-remove-direct-vbus-regulator-control.patch, proper fix
  will be in the next rebase.

* Wed Aug 21 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git1.2
- Add patch to fix brcmsmac oops (rhbz 989269)
- CVE-2013-0343 handling of IPv6 temporary addresses (rhbz 914664 999380)

* Tue Aug 20 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git1.1
- Linux v3.11-rc6-28-gfd3930f
- Reenable debugging options.

* Tue Aug 20 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Disable Dell RBU so userspace firmware path isn't selected (rhbz 997149)

* Mon Aug 19 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc6.git0.1
- Linux v3.11-rc6
- Disable debugging options.

* Mon Aug 19 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor kernel configs cleanup merging duplicated config opts into generic

* Sun Aug 18 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc5.git6.1
- Linux v3.11-rc5-168-ga08797e

* Sat Aug 17 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc5.git5.1
- Linux v3.11-rc5-165-g215b28a

* Fri Aug 16 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM drivers config for Zynq 7000 devices

* Fri Aug 16 2013 Josh Boyer <jwboyer@fedoraproject.org> - 3.11.0-0.rc5.git4.1
- Linux v3.11-rc5-150-g0f7dd1a

* Fri Aug 16 2013 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Nathanael Noblet to fix mic on Gateway LT27 (rhbz 845699)

* Thu Aug 15 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Major cleanup of arm64 config
- Add patch to enable build exynos5 as multi platform for lpae
- Minor cleanup of ARMv7 configs

* Thu Aug 15 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc5.git3.1
- Enable CONFIG_HID_SENSOR_HUB (rhbz 995510)
- Add patch to fix regression on TeVII S471 devices (rhbz 963715)
- Linux v3.11-rc5-35-gf1d6e17

* Wed Aug 14 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc5.git2.1
- Linux v3.11-rc5-21-g28fbc8b
- Disable WIMAX.  It's fairly broken and abandoned upstream.

* Tue Aug 13 2013 Josh Boyer <jwboyer@gmail.com> - 3.11.0-0.rc5.git1.1
- Linux v3.11-rc5-13-g584d88b
- Reenable debugging options.

* Mon Aug 12 2013 Josh Boyer <jwboyer@gmail.com> - 3.11.0-0.rc5.git0.1
- Linux v3.11-rc5
- Disable debugging options.

* Sun Aug 11 2013 Josh Boyer <jwboyer@gmail.com> - 3.11.0-0.rc4.git5.1
- Linux v3.11-rc4-216-g77f63b4

* Sun Aug 11 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop a bunch of generic dupe config from aarch64

* Sat Aug 10 2013 Josh Boyer <jwboyer@gmail.com> - 3.11.0-0.rc4.git4.1
- Linux v3.11-rc4-162-g14e9419

* Fri Aug 09 2013 Josh Boyer <jwboyer@gmail.com> - 3.11.0-0.rc4.git3.1
- Linux v3.11-rc4-103-g6c2580c

* Wed Aug 07 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc4.git2.1
- Linux v3.11-rc4-27-ge4ef108
- Add zero file length check to make sure pesign didn't fail (rhbz 991808)

* Tue Aug 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc4.git1.1
- Linux v3.11-rc4-20-g0fff106
- Reenable debugging options.
- Don't package API man pages in -doc (rhbz 993905)

* Mon Aug 05 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc4.git0.1
- Linux v3.11-rc4
- Disable debugging options.

* Sun Aug 04 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc3.git4.1
- Linux v3.11-rc3-376-g72a67a9

* Sat Aug 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc3.git3.1
- Linux v3.11-rc3-288-gabe0308

* Fri Aug 02 2013 Kyle McMartin <kyle@redhat.com> - 3.11.0-0.rc3.git2.1
- radeon-si_calculate_leakage-use-div64.patch: fix a compile error on i686.
- arm: disable CONFIG_LOCK_STAT, bloats .data massively, revisit shortly.
- arm: build-in more rtc drivers.

* Fri Aug 02 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc3.git2.1
- Linux v3.11-rc3-207-g64ccccf

* Thu Aug  1 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config update

* Thu Aug 01 2013 Josh Boyer <jwboyer@redhat.com>
- Fix mac80211 connection issues (rhbz 981445)
- Fix firmware issues with iwl4965 and rfkill (rhbz 977053)
- Drop hid-logitech-dj patch that was breaking enumeration (rhbz 989138)

* Tue Jul 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.11.0-0.rc3.git1.1
- Linux v3.11-rc3-4-g36f571e
- Reenable debugging options.

* Tue Jul 30 2013 Josh Boyer <jwboyer@redhat.com>
- Revert some changes to make Logitech devices function properly (rhbz 989138)

* Mon Jul 29 2013 Kyle McMartin <kyle@redhat.com> - 3.11.0-0.rc3.git0.1
- arm-sound-soc-samsung-dma-avoid-another-64bit-division.patch: ditto

* Mon Jul 29 2013 Kyle McMartin <kyle@redhat.com>
- arm-dma-amba_pl08x-avoid-64bit-division.patch: STAHP libgcc callouts

* Mon Jul 29 2013 Josh Boyer <jwboyer@redhat.com>
- Linux v3.11-rc3
- Disable debugging options.
- Always include x509.genkey in Sources list

* Fri Jul 26 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git4.1
- Linux v3.11-rc2-333-ga9b5f02

* Fri Jul 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix NULL deref in iwlwifi (rhbz 979581)

* Thu Jul 25 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git3.1
- Linux v3.11-rc2-185-g07bc9dc

* Wed Jul 24 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git2.1
- Linux v3.11-rc2-158-g04012e3

* Tue Jul 23 2013 Kyle McMartin <kyle@redhat.com>
- arm-tegra-remove-direct-vbus-regulator-control.patch: backport patches
  to fix ehci-tegra.

* Tue Jul 23 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git1.1
- Linux v3.11-rc2-93-gb3a3a9c

* Mon Jul 22 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git0.2
- let flavors/variants end with "+$flavor" in the uname patch from harald@redhat.com
- Reenable debugging options.

* Mon Jul 22 2013 Josh Boyer <jwboyer@redhat.com>
- Fix timer issue in bridge code (rhbz 980254)

* Mon Jul 22 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc2.git0.1
- Linux v3.11-rc2
- Disable debugging options.

* Sun Jul 21 2013 Kyle McMartin <kmcmartin@redhat.com> - 3.11.0-0.rc1.git4.1
- Linux v3.11-rc1-247-g90db76e

* Sun Jul 21 2013 Kyle McMartin <kyle@redhat.com>
- arm-omap-bbb-dts.patch: disable for now, it needs too much work for
  a sunday morning.

* Fri Jul 19 2013 Kyle McMartin <kyle@redhat.com>
- arm-omap-bbb-dts.patch: fix arch/arm/boot/dtb/Makefile rule

* Fri Jul 19 2013 Kyle McMartin <kmcmartin@redhat.com> - 3.11.0-0.rc1.git3.1
- Linux v3.11-rc1-181-gb8a33fc

* Fri Jul 19 2013 Kyle McMartin <kmcmartin@redhat.com> - 3.11.0-0.rc1.git2.1
- Linux v3.11-rc1-135-g0a693ab

* Thu Jul 18 2013 Kyle McMartin <kyle@redhat.com>
- Applied patch from Kay Sievers to kill initscripts Conflicts & Requires and
  udev Conflicts...
- And then clean up some of the ancient crap from our Conflicts and Requires
  which reference versions not shipped since 2006.

* Thu Jul 18 2013 Kyle McMartin <kyle@redhat.com>
- devel-sysrq-secure-boot-20130717.patch: add a patch that allows the user to
  disable secure boot restrictions from the local console or local serial
  (but not /proc/sysrq-trigger or via uinput) by using SysRQ-x.

* Wed Jul 17 2013 Kyle McMartin <kyle@redhat.com> - 3.11.0-0.rc1.git1.1
- Linux v3.11-rc1-19-gc0d15cc
- Reenable debugging options.

* Wed Jul 17 2013 Kyle McMartin <kyle@redhat.com>
- update s390x config [Dan Horák]

* Wed Jul 17 2013 Petr Pisar <ppisar@redhat.com> - 3.11.0-0.rc1.git0.2
- Perl 5.18 rebuild

* Wed Jul 17 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch for BeagleBone Black DTB

* Tue Jul 16 2013 Kyle McMartin <kyle@redhat.com> - 3.11.0-0.rc1.git0.1
- Linux v3.11-rc1
- Disable debugging options.
- Fix %kernel_modules warning.

* Sun Jul 14 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM config
- Enable USB gadget module on ARM to fix build i.MX usb modules

* Sun Jul 14 2013 Dennis Gilmore <dennis@ausil.us>
- update and reenable wandboard quad dtb patch

* Fri Jul 12 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc0.git7.1
- Linux v3.10-9289-g9903883

* Fri Jul 12 2013 Dave Jones <davej@redhat.com> - 3.11.0-0.rc0.git6.4
- Disable LATENCYTOP/SCHEDSTATS in non-debug builds.

* Fri Jul 12 2013 Josh Boyer <jwboyer@redhat.com>
- Add iwlwifi fix for connection issue (rhbz 885407)

* Thu Jul 11 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc0.git6.1
- Linux v3.10-9080-g19d2f8e

* Thu Jul 11 2013 Kyle McMartin <kyle@redhat.com>
- Enable USB on Wandboard Duallite and other i.MX based boards, patch
  from Niels de Vos.

* Thu Jul 11 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM config cleanups and changes for 3.11

* Wed Jul 10 2013 Kyle McMartin <kyle@redhat.com>
- Fix crash-driver.patch to properly use page_is_ram. 

* Tue Jul 09 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc0.git3.1
- Linux v3.10-6378-ga82a729

* Mon Jul  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial ARM config for 3.11

* Mon Jul 08 2013 Justin M. Forbes <jforbes@redhat.com> - 3.11.0-0.rc0.git2.1
- Linux v3.10-6005-gd2b4a64
- Reenable debugging options.

* Fri Jul 05 2013 Josh Boyer <jwboyer@redhat.com>
- Add vhost-net use-after-free fix (rhbz 976789 980643)
- Add fix for timer issue in bridge code (rhbz 980254)

* Wed Jul 03 2013 Josh Boyer <jwboyer@redhat.com>
- Add patches to fix iwl skb managment (rhbz 977040)

* Tue Jul 02 2013 Dennis Gilmore <dennis@ausil.us> - 3.10-2
- create a dtb for wandboard quad

* Mon Jul 01 2013 Justin M. Forbes <jforbes@redhat.com> - 3.10-1
- Linux v3.10

* Fri Jun 28 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Only enable ARM A15 errata on the LPAE kernel as it breaks A8

* Thu Jun 27 2013 Josh Boyer <jwboyer@redhat.com>
- Fix stack memory usage for DMA in ath3k (rhbz 977558)

* Wed Jun 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add two patches to fix bridge networking issues (rhbz 880035)

* Mon Jun 24 2013 Josh Boyer <jwboyer@redhat.com>
- Fix battery issue with bluetooth keyboards (rhbz 903741)

* Mon Jun 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc7.git0.1
- Linux v3.10-rc7
- Disable debugging options.

* Tue Jun 18 2013 Dave Jones <davej@redhat.com>
- Disable MTRR sanitizer by default.

* Tue Jun 18 2013 Justin M. Forbes <jforbes@redhat.com> - 3.10.0-0.rc6.git0.4
- Testing the test harness

* Tue Jun 18 2013 Justin M. Forbes <jforbes@redhat.com> - 3.10.0-0.rc6.git0.3
- Reenable debugging options.

* Mon Jun 17 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix radeon issues on powerpc

* Mon Jun 17 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc6.git0.1
- Linux v3.10-rc6

* Fri Jun 14 2013 Kyle McMartin <kyle@redhat.com>
- ARM64 support (config-arm64)
  Split out some config-armv7-generic options common between 32-bit and 64-bit
  ARM into a new config-arm-generic, and use that as a base for
  both.
  Buildable in rawhide, and F-19 by installing {gcc,binutils}-aarch64-linux-gnu
  and running:
  rpmbuild --rebuild --target $ARCH --with cross --without perf \
    --without tools --without debuginfo --define "_arch aarch64" \
    --define "_build_arch aarch64" \
    --define "__strip /usr/bin/aarch64-linux-gnu-strip" kernel*.src.rpm
  As rpm in F-19 doesn't have aarch64-linux macros yet.

* Thu Jun 13 2013 Kyle McMartin <kyle@redhat.com>
- Introduce infrastructure for cross-compiling Fedora kernels. Intended to
  assist building for secondary architectures like ppc64, s390x, and arm.
  To use, create an .src.rpm using "fedpkg srpm" and then run
  "rpmbuild --rebuild --target t --with cross --without perf --without tools \
    kernel*.src.rpm" to cross compile. This requires binutils and gcc
  packages named like %_target_cpu, which all but powerpc64 currently provides
  in rawhide/F-19. Can't (currently) cross compile perf or kernel-tools, since
  libc is missing from the cross environment.

* Thu Jun 13 2013 Kyle McMartin <kyle@redhat.com>
- arm-export-read_current_timer.patch: drop upstream patch
  (results in duplicate exports)

* Wed Jun 12 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates

* Wed Jun 12 2013 Kyle McMartin <kmcmarti@redhat.com>
- Merge %{with_pae} and %{with_lpae} so both ARM and i686 use the same
  flavours. Set %{pae} to the flavour name {lpae, PAE}. Merging
  the descriptions would be nice, but is somewhat irrelevant...

* Wed Jun 12 2013 Josh Boyer <jwboyer@redhat.com>
- Fix KVM divide by zero error (rhbz 969644)
- Add fix for rt5390/rt3290 regression (rhbz 950735)

* Tue Jun 11 2013 Dave Jones <davej@redhat.com>
- Disable soft lockup detector on virtual machines. (rhbz 971139)

* Tue Jun 11 2013 Josh Boyer <jwboyer@redhat.com>
- Add patches to fix MTRR issues in 3.9.5 (rhbz 973185)
- Add two patches to fix issues with vhost_net and macvlan (rhbz 954181)

* Tue Jun 11 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc5.git0.1
- Linux v3.10-rc5
- CVE-2013-2164 information leak in cdrom driver (rhbz 973100 973109)

* Mon Jun 10 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Freescale i.MX platforms and initial config

* Fri Jun 07 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2851 block: passing disk names as format strings (rhbz 969515 971662)
- CVE-2013-2852 b43: format string leaking into error msgs (rhbz 969518 971665)

* Thu Jun 06 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2148 fanotify: info leak in copy_event_to_user (rhbz 971258 971261)
- CVE-2013-2147 cpqarray/cciss: information leak via ioctl (rhbz 971242 971249)

* Wed Jun 05 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2140 xen: blkback: insufficient permission checks for BLKIF_OP_DISCARD (rhbz 971146 971148)

* Tue Jun 04 2013 Dave Jones <davej@redhat.com> - 3.10.0-0.rc4.git0.1
- 3.10-rc4
  merged: radeon-use-max_bus-speed-to-activate-gen2-speeds.patch
  merged: iscsi-target-fix-heap-buffer-overflow-on-error.patch

* Mon Jun 03 2013 Josh Boyer <jwboyer@redhat.com>
- Fix UEFI anti-bricking code (rhbz 964335)

* Mon Jun  3 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config changes

* Sun Jun  2 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix DRM/X on omap (panda)
- Enable Cortex-A8 errata on multiplatform kernels (omap3)
- Minor ARM config updates

* Fri May 31 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-2850 iscsi-target: heap buffer overflow on large key error (rhbz 968036 969272)

* Thu May 30 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config update for tegra (AC100)

* Mon May 27 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc3.git0.1
- Linux v3.10-rc3
- Disable debugging options.

* Mon May 27 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM updates

* Fri May 24 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to quiet irq remapping failures (rhbz 948262)

* Fri May 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc2.git3.1
- Linux v3.10-rc2-328-g0e255f1

* Fri May 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc2.git2.1
- Linux v3.10-rc2-221-g514e250

* Thu May 23 2013 Kyle McMartin <kyle@redhat.com>
- Fix modules.* removal from /lib/modules/$KernelVer

* Thu May 23 2013 Josh Boyer <jwboyer@redhat.com>
- Fix oops from incorrect rfkill set in hp-wmi (rhbz 964367)

* Wed May 22 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc2.git1.1
- Linux v3.10-rc2-68-gbb3ec6b
- Reenable debugging options.

* Tue May 21 2013 Kyle McMartin <kyle@redhat.com>
- Rewrite the modinfo license check to generate significantly less noise in
  build logs.
- Ditto for the modules.* removal (and move it earlier, as pointed out by jwb)

* Tue May 21 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable OMAP5 on ARM multiplatform

* Tue May 21 2013 Kyle McMartin <kyle@redhat.com> - 3.10.0-0.rc2.git0.2
- Disable debugging options.

* Mon May 20 2013 Kyle McMartin <kyle@redhat.com> - 3.10.0-0.rc2.git0.1
- Linux v3.10-rc2
- Disable debugging options

* Mon May 20 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM update

* Mon May 20 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git7.1
- Linux v3.10-rc1-369-g343cd4f

* Fri May 17 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git6.1
- Linux v3.10-rc1-266-gec50f2a

* Thu May 16 2013 Josh Boyer <jwboyer@redhat.com>
- Enable memory cgroup swap accounting (rhbz 918951)
- Fix config-local usage (rhbz 950841)

* Wed May 15 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git5.1
- Linux v3.10-rc1-185-gc240a53

* Wed May 15 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Harald Hoyer to migrate to using kernel-install

* Wed May 15 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git4.1
- Linux v3.10-rc1-120-gb973425

* Tue May 14 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git3.1
- Linux v3.10-rc1-113-ga2c7a54

* Tue May 14 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git2.1
- Linux v3.10-rc1-79-gdbbffe6

* Mon May 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git1.1
- Linux v3.10-rc1-34-g1f63876

* Mon May 13 2013 Josh Boyer <jwboyer@redhat.com>
- Add radeon fixes for PCI-e gen2 speed issues (rhbz 961527)

* Mon May 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git0.2
- Reenable debugging options.

* Mon May 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc1.git0.1
- Linux v3.10-rc1
- Disable debugging options.

* Sat May 11 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Another patch to fix ARM kernel build

* Fri May 10 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix exynosdrm build, drop old tegra patches, minor config updates

* Fri May 10 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git26.1
- Linux v3.9-12555-g2dbd3ca

* Fri May 10 2013 Josh Boyer <jwboyer@redhat.com>
- Enable RTLWIFI_DEBUG in debug kernels (rhbz 889425)
- Switch the loop driver to a module and change to doing on-demand creation
  (rhbz 896160)
- Disable CRYPTOLOOP as F18 util-linux is the last to support it (rhbz 896160)

* Fri May 10 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git25.1
- Linux v3.9-12316-g70eba42

* Thu May 09 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git24.1
- Linux v3.9-12070-g8cbc95e

* Thu May  9 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable DMA for ARM sound drivers

* Thu May 09 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git23.1
- Linux v3.9-11789-ge0fd9af

* Wed May  8 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable RemoteProc drivers on ARM

* Wed May 08 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git22.1
- Linux v3.9-11572-g5af43c2

* Tue May 07 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git21.1
- Linux v3.9-11485-gbb9055b

* Tue May 07 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git20.1
- Linux v3.9-10996-g0f47c94

* Tue May 07 2013 Josh Boyer <jwboyer@redhat.com>
- Fix dmesg_restrict patch to avoid regression (rhbz 952655)

* Mon May 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git19.1
- Linux v3.9-10936-g51a26ae

* Mon May  6 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable TPS65217 (am33xx) and EC on ChromeOS devices

* Mon May 06 2013 Josh Boyer <jwboyer@redhat.com>
- Don't remove headers explicitly exported via UAPI (rhbz 959467)

* Mon May 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git18.1
- Linux v3.9-10518-gd7ab730

* Mon May 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git17.1
- Linux v3.9-10104-g1aaf6d3

* Sun May  5 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM config

* Sat May 04 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git16.1
- Linux v3.9-9472-g1db7722

* Fri May 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git15.1
- Linux v3.9-9409-g8665218

* Fri May 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git14.1
- Linux v3.9-8933-gce85722

* Fri May  3 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM 3.10 merge and general cleanup
- Drop dedicated tegra kernel as now Multiplatform enabled
- Enable Tegra and UX500 (Snowball) in Multiplatform

* Thu May 02 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git13.1
- Linux v3.9-8153-g5a148af

* Thu May 02 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git12.1
- Linux v3.9-7992-g99c6bcf

* Thu May 02 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git11.1
- Linux v3.9-7391-g20b4fb4

* Wed May 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git10.1
- Linux v3.9-5308-g8a72f38

* Wed May 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git9.1
- Linux v3.9-5293-g823e75f

* Wed May  1 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM updates

* Wed May 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git8.1
- Linux v3.9-5165-g5f56886

* Tue Apr 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git7.1
- Linux v3.9-4597-g8c55f14

* Tue Apr 30 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable CONFIG_SERIAL_8250_DW on ARM

* Tue Apr 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git6.1
- Linux v3.9-4516-gc9ef713

* Tue Apr 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git5.1
- Linux v3.9-3520-g5a5a1bf

* Tue Apr 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git4.1
- Linux v3.9-3143-g56847d8

* Mon Apr 29 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git3.1
- Linux v3.9-2154-gec25e24

* Mon Apr 29 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git2.1
- Linux v3.9-332-g92ddcf4

* Mon Apr 29 2013 Josh Boyer <jwboyer@redhat.com> - 3.10.0-0.rc0.git1.1
- Linux v3.9-84-g916bb6d7
- Reenable debugging options.

* Mon Apr 29 2013 Neil Horman <nhorman@redhat.com>
- Enable CONFIG_PACKET_DIAG (rhbz 956870)

* Mon Apr 29 2013 Josh Boyer <jwboyer@redhat.com>
- Linux v3.9

* Fri Apr 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to prevent scheduling while atomic error in blkcg

* Wed Apr 24 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix EFI boot on Macs (rhbz 953447)

* Mon Apr 22 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc8.git0.1
- Linux v3.9-rc8
- Disable debugging options.

* Mon Apr 22 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM updates

* Fri Apr 19 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix RCU splat from perf events

* Fri Apr 19 2013 Peter Robinson <pbrobinson@fedoraproject.org> 
- Temporaily disable cpu idle on ARM as it appears to be causing stability issues

* Fri Apr 19 2013 Josh Boyer <jwboyer@redhat.com>
- Disable Intel HDA and enable RSXX block dev on ppc64/ppc64p7

* Thu Apr 18 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc7.git3.1
- Linux v3.9-rc7-70-gd202f05

* Wed Apr 17 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc7.git2.1
- Linux v3.9-rc7-24-g542a672

* Wed Apr 17 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates
- Add patch for DT DMA issues that affect at least highbank/tegra ARM devices

* Tue Apr 16 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc7.git1.1
- Linux v3.9-rc7-4-gbb33db7
- Reenable debugging options.

* Tue Apr 16 2013 Josh Boyer <jwboyer@redhat.com>
- Fix uninitialized variable free in iwlwifi (rhbz 951241)
- Fix race in regulatory code (rhbz 919176)

* Mon Apr 15 2013 Josh Boyer <jwboyer@redhat.com>
- Fix debug patches to build on s390x/ppc

* Mon Apr 15 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc7.git0.1
- Linux v3.9-rc7
- Disable debugging options.

* Fri Apr 12 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_LDM_PARTITION (rhbz 948636)

* Fri Apr 12 2013 Justin M. Forbes <jforbes@redhat.com>
- Fix forcedeth DMA check error (rhbz 928024)

* Thu Apr 11 2013 Dave Jones <davej@redhat.com>
- Print out some extra debug information when we hit bad page tables.

* Thu Apr 11 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc6.git2.1
- Linux v3.9-rc6-115-g7ee32a6
- libsas: use right function to alloc smp response (rhbz 949875)

* Tue Apr 09 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc6.git1.1
- Linux v3.9-rc6-36-ge8f2b54
- Reenable debugging options.

* Tue Apr  9 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix building some ARM tegra modules
- Some minor ARM OMAP updates

* Mon Apr 08 2013 Neil Horman <nhorman@redhat.com>
- Fix dma unmap error in e100 (rhbz 907694)

* Mon Apr 08 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc6.git0.1
- Disable debugging options.
- Linux-3.9-rc6

* Thu Apr 04 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc5.git3.1
- Linux v3.9-rc5-183-g22d1e6f

* Wed Apr 03 2013 Dave Jones <davej@redhat.com>
- Enable MTD_CHAR/MTD_BLOCK (Needed for SFC)
  Enable 10gigE on 64-bit only.

* Wed Apr 03 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc5.git2.1
- Linux v3.9-rc5-146-gda241ef

* Wed Apr  3 2013 Peter Robinson <pbrobinson@fedoraproject.org> 
- Add upstream usb-next OMAP patch to fix usb on omap/mvebu

* Tue Apr 02 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_FB_MATROX_G on powerpc

* Tue Apr 02 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc5.git1.1
- Linux v3.9-rc5-108-g118c9a4
- Reenable debugging options.

* Tue Apr 02 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_SCSI_DMX3191D (rhbz 919874)

* Mon Apr 01 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_MCE_INJECT (rhbz 927353)

* Mon Apr 01 2013 Justin M. Forbes <jforbes@redhat.com> - 3.9.0-0.rc5.git0.1
- Disable debugging options.
- Linux v3.9-rc5
- fix htmldoc build for 8250 rename. Patch from Kyle McMartin

* Mon Apr  1 2013 Peter Robinson <pbrobinson@fedoraproject.org> 
- Minor ARM LPAE updates

* Sun Mar 31 2013 Peter Robinson <pbrobinson@fedoraproject.org> 
- Make tegra inherit armv7-generic, fix and re-enable tegra
- Enable SPI on ARM
- Drop config-arm-generic
- ARM config updates

* Thu Mar 28 2013 Peter Robinson <pbrobinson@fedoraproject.org> 
- Update ARM unified config for OMAP

* Tue Mar 26 2013 Justin M. Forbes <jforbes@redhat.com>
- Fix child thread introspection of of /proc/self/exe (rhbz 927469)

* Tue Mar 26 2013 Dave Jones <davej@redhat.com>
- Enable CONFIG_DM_CACHE (rhbz 924325)

* Tue Mar 26 2013 Josh Boyer <jwboyer@redhat.com>
- Add quirk for Realtek card reader to avoid 10 sec boot delay (rhbz 806587)
- Add quirk for MSI keyboard backlight to avoid 10 sec boot delay (rhbz 907221)

* Mon Mar 25 2013 Justin M. Forbes <jforbes@redhat.com>
- disable whci-hcd since it doesnt seem to have users (rhbz 919289)

* Sun Mar 24 2013 Dave Jones <davej@redhat.com> -3.9.0-0.rc4.git0.1
- Linux 3.9-rc4
  merged: drm-i915-bounds-check-execbuffer-relocation-count.patch

* Sun Mar 24 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM config for OMAP/mvebu/lpae

* Fri Mar 22 2013 Dave Jones <davej@redhat.com>
- Fix calculation of current frequency in intel_pstate driver. (rhbz 923942)
- Add missing build-req for perl-Carp

* Thu Mar 21 2013 Josh Boyer <jwboyer@redhat.com>
- Fix workqueue crash in mac80211 (rhbz 920218)

* Thu Mar 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc3.git1.1
- Linux v3.9-rc3-148-g2ffdd7e
- Fixes CVE-2013-1796, CVE-2013-1797, CVE-2013-1798 in kvm.

* Wed Mar 20 2013 Dave Jones <davej@redhat.com>
- Enable CONFIG_DM_DELAY (rhbz 923721)

* Tue Mar 19 2013 Dave Jones <davej@redhat.com> - 3.9.0-0.rc3.git0.5
- Reenable debugging options.

* Tue Mar 19 2013 Dave Jones <davej@redhat.com>
- cpufreq/intel_pstate: Add function to check that all MSR's are valid (rhbz 922923)

* Mon Mar 18 2013 Dave Jones <davej@redhat.com> - 3.9.0-0.rc3.git0.4
- s390x config option changes from Dan Horák <dan@danny.cz>
   - enable PCI
   - disable few useless drivers
   - disable drivers conflicting with s390x

* Mon Mar 18 2013 Dave Jones <davej@redhat.com> - 3.9.0-0.rc3.git0.3
- Linux v3.9-rc3
  merged: w1-fix-oops-when-w1_search-is-called-from.patch
- Disable debugging options.

* Sun Mar 17 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Merge OMAP support into ARM unified kernel
- Add ARM LPAE kernel for Cortex A-15 devices that support LPAE and HW virtualisation
- Unified ARM kernel provides highbank and OMAP support
- Drop remantents of ARM softfp kernels

* Fri Mar 15 2013 Josh Boyer <jwboyer@redhat.com>
- Fix divide by zero on host TSC calibration failure (rhbz 859282)

* Fri Mar 15 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc2.git1.1
- Linux v3.9-rc2-292-ga2362d2
- Fixes CVE-2013-1860 kernel: usb: cdc-wdm buffer overflow triggered by device

* Thu Mar 14 2013 Dave Jones <davej@redhat.com>
- Move cpufreq drivers to be modular (rhbz 746372)

* Wed Mar 13 2013 Dave Jones <davej@redhat.com> - 3.9.0-0.rc2.git0.3
- Reenable debugging options.

* Tue Mar 12 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix ieee80211_do_stop (rhbz 892599)
- Add patches to fix cfg80211 issues with suspend (rhbz 856863)
- CVE-2013-0913 drm/i915: head writing overflow (rhbz 920471 920529)
- CVE-2013-0914 sa_restorer information leak (rhbz 920499 920510)

* Tue Mar 12 2013 Dave Airlie <airlied@redhat.com>
- add QXL driver (f19 only)

* Mon Mar 11 2013 Dave Jones <davej@redhat.com> - 3.9.0-0.rc2.git0.2
- Disable debugging options.

* Mon Mar 11 2013 Dave Jones <davej@redhat.com>
- Linux 3.9-rc2

* Mon Mar 11 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to allow "8250." prefix to keep working (rhbz 911771)
- Add patch to fix w1_search oops (rhbz 857954)

* Sun Mar 10 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc1.git2.1
- Linux v3.9-rc1-278-g8343bce

* Sun Mar 10 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Xilinx Zynq
- Enable highbank cpufreq driver

* Fri Mar 08 2013 Josh Boyer <jwboyer@redhat.com>
- Add turbostat and x86_engery_perf_policy debuginfo to kernel-tools-debuginfo

* Fri Mar 08 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc1.git1.1
- Linux v3.9-rc1-211-g47b3bc9
- Reenable debugging options.
- CVE-2013-1828 sctp: SCTP_GET_ASSOC_STATS stack buffer overflow (rhbz 919315 919316)

* Thu Mar 07 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1792 keys: race condition in install_user_keyrings (rhbz 916646 919021)

* Wed Mar 06 2013 Josh Boyer <jwboyer@redhat.com>
- Adjust secure-boot patchset to work with boot_params sanitizing
- Don't clear efi_info in boot_params (rhbz 918408)

* Wed Mar 06 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM mvebu config

* Wed Mar 06 2013 Dave Jones <davej@redhat.com>
- drop acpi debugging patch.

* Wed Mar 06 2013 Justin M. Forbes <jforbes@redhat.com>
- Remove Ricoh multifunction DMAR patch as it's no longer needed (rhbz 880051)

* Tue Mar 05 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc1.git0.3
- Fix intel_pstate init error path (rhbz 916833)

* Tue Mar  5 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Temporarily disable tegra until we get a fix from upstream

* Tue Mar 05 2013 Josh Boyer <jwboyer@redhat.com>
- Add 3 fixes for efi issues (rhbz 917984)
- Enable CONFIG_IP6_NF_TARGET_MASQUERADE

* Mon Mar 04 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc1.git0.1
- Linux v3.9-rc1
- Add patch from Dirk Brandewie to fix intel pstate divide error (rhbz 916833)
- Disable debugging options.

* Mon Mar  4 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update vexpress and omap options (fix MMC on qemu, hopefully fix OMAP3)

* Sun Mar 03 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git15.1
- Linux v3.8-10734-ga7c1120

* Fri Mar 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git14.1
- Linux v3.8-10206-gb0af9cd

* Fri Mar 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git13.1
- Linux v3.8-9761-gde1a226

* Thu Feb 28 2013 Kyle McMartin <kmcmarti@redhat.com>
- Make iso9660 a module.

* Thu Feb 28 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git12.1
- Linux v3.8-9633-g2a7d2b9

* Wed Feb 27 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop ARM kirkwood kernel
- Enable SPI on ARM
- General 3.9 updates

* Wed Feb 27 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git11.1
- Linux v3.8-9456-g309667e

* Wed Feb 27 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git10.1
- Linux v3.8-9405-gd895cb1

* Tue Feb 26 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git9.1
- Linux v3.8-9165-g1cef935

* Tue Feb 26 2013 Kyle McMartin <kmcmarti@redhat.com>
- Move VMXNET3 to config-x86-generic from config-generic, it's VMware
  virtual ethernet.

* Tue Feb 26 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git8.1
- Linux v3.8-8664-gc41b381

* Tue Feb 26 2013 Kyle McMartin <kmcmarti@redhat.com>
- Add blk_queue_physical_block_size and register_netdevice to the symbols
  used for initrd generation (synched from .el6)
- ipr.ko driven SAS VRAID cards found on x86_64 machines these days, and not
  just on ppc64

* Tue Feb 26 2013 Josh Boyer <jwboyer@redhat.com>
- Fix vmalloc_fault oops during lazy MMU (rhbz 914737)

* Mon Feb 25 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git7.1
- Honor dmesg_restrict for /dev/kmsg (rhbz 903192)
- Linux v3.8-7888-gab78265

* Sun Feb 24 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git6.1
- Linux v3.8-6988-g9e2d59a

* Sun Feb 24 2013 Josh Boyer <jwboyer@redhat.com>
- CVE-2013-1763 sock_diag: out-of-bounds access to sock_diag_handlers (rhbz 915052,915057)

* Fri Feb 22 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git5.1
- Linux v3.8-6071-g8b5628a

* Fri Feb 22 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git4.1
- Linux v3.8-6071-g8b5628a
- Enable the rtl8192e driver (rhbz 913753)

* Thu Feb 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git3.1
- Linux v3.8-3195-g024e4ec
- Shut up perf about missing build things we don't care about
- Drop the old aic7xxx driver, from Paul Bolle

* Thu Feb 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git2.1
- Linux v3.8-3040-ga0b1c42

* Thu Feb 21 2013 Josh Boyer <jwboyer@redhat.com> - 3.9.0-0.rc0.git1.1
- Linux v3.8-523-gece8e0b
- Reenable debugging options.

* Tue Feb 19 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-2
- Add pekey support from David Howells and rework secure-boot patchset on top
- Add support for Atheros 04ca:3004 bluetooth devices (rhbz 844750)
- Backport support for newer ALPS touchpads (rhbz 812111)
- Enable CONFIG_AUDIT_LOGINUID_IMMUTABLE

* Tue Feb 19 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-1
- Linux v3.8
- Fix build with CONFIG_EFI disabled, reported by Peter Bowey (rhbz 911833)
- Disable debugging options.

* Mon Feb 18 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc7.git4.1
- Linux v3.8-rc7-93-gf741656

* Thu Feb 14 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc7.git3.1
- Linux v3.8-rc7-73-g323a72d

* Thu Feb 14 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to fix corruption on newer M6116 SATA bridges (rhbz 909591)
- CVE-2013-0228 xen: xen_iret() invalid %ds local DoS (rhbz 910848 906309)

* Wed Feb 13 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable tegra30

* Wed Feb 13 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc7.git2.1
- Linux v3.8-rc7-32-gecf223f

* Tue Feb 12 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch to create a convenient mount point for pstore (rhbz 910126)

* Tue Feb 12 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc7.git1.1
- Linux v3.8-rc7-6-g211b0cd
- Reenable debugging options.

* Mon Feb 11 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Kees Cook to restrict MSR writting in secure boot mode
- Build PATA_MACIO in on powerpc (rhbz 831361)

* Fri Feb 08 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc7.git0.1
- Linux v3.8-rc7
- Add patch to fix atomic sleep issue on alloc_pid failure (rhbz 894623)
- Disable debugging options.

* Thu Feb  7 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM build fixes

* Wed Feb 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc6.git3.3
- Enable CONFIG_NAMESPACES everywhere (rhbz 907576)
- Add patch to fix ath9k dma stop checks (rhbz 892811)

* Wed Feb 06 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc6.git3.1
- Linux v3.8-rc6-98-g1589a3e
- Add patch to honor MokSBState (rhbz 907406)

* Tue Feb 05 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc6.git2.1
- Linux v3.8-rc6-62-gfe547d7
- Enable CONFIG_DRM_VMWGFX_FBCON (rhbz 907620)
- Enable CONFIG_DETECT_HUNG_TASK

* Mon Feb 04 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc6.git1.1
- Linux v3.8-rc6-22-g6edacf0
- Enable CONFIG_EXT4_DEBUG
- Fix rtlwifi scheduling while atomic from Larry Finger (rhbz 903881)

* Fri Feb 01 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc6.git0.1
- Linux v3.8-rc6
- Enable CONFIG_DMA_API_DEBUG
- Add patches to improve mac80211 latency and throughput (rhbz 830151)

* Thu Jan 31 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc5.git3.1
- Linux v3.8-rc5-245-g04c2eee
- Enable CONFIG_DEBUG_STACK_USAGE

* Wed Jan 30 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc5.git2.1
- Linux v3.8-rc5-218-ga56e160
- Enable NAMESPACES and CHECKPOINT_RESTORE on x86_64 for F19 CRIU feature
- Enable CONFIG_DEBUG_ATOMIC_SLEEP

* Tue Jan 29 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc5.git1.1
- Linux v3.8-rc5-150-g6abb7c2

* Tue Jan 29 2013 Josh Boyer <jwboyer@redhat.com>
- Backport driver for Cypress PS/2 trackpad (rhbz 799564)

* Mon Jan 28 2013 Josh Boyer <jwboyer@redhat.com> - 3.8.0-0.rc5.git0.1
- Linux v3.8-rc5
- Add patches to fix issues with iwlwifi (rhbz 863424)
- Enable CONFIG_PROVE_RCU

* Sun Jan 27 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Reenable perf on ARM (was suppose to be temporary)
- Build and package dtbs on ARM
- Enable FB options for qemu vexpress on unified

* Fri Jan 25 2013 Kyle McMartin <kmcmarti@redhat.com>
- Sign all modules with the mod-extra-sign.sh script, ensures nothing gets
  missed because of .config differences between invocations of BuildKernel.

* Fri Jan 25 2013 Justin M. Forbes <jforbes@redhat.com>
- Turn off THP for 32bit

* Fri Jan 25 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc4.git5.1
- Linux v3.8-rc4-277-g66e2d3e
- Enable slub debug

* Thu Jan 24 2013 Josh Boyer <jwboyer@redhat.com>
- Update secure-boot patchset

* Thu Jan 24 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc4.git4.1
- Linux v3.8-rc4-183-gff7532c
- Enable lockdep

* Wed Jan 23 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc4.git3.1
- Linux v3.8-rc4-139-g1d85490
- Enable debug spinlocks

* Wed Jan 23 2013 Dave Jones <davej@redhat.com>
- Remove warnings about empty IPI masks.

* Sun Jan 20 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Remove obsolete ARM configs
- Update OMAP config for TI AM35XX SoCs
- Add patch to fix versatile build failure

* Sat Jan 19 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc4.git1.1
- Linux v3.8-rc4-42-g5da1f88

* Fri Jan 18 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc4.git0.1
- Linux v3.8-rc4
- Disable debugging options.

* Fri Jan 18 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable problematic PL310 ARM errata
- Minor ARM config tweaks
- OMAP DRM driver to fix OMAP kernel build

* Wed Jan 16 2013 Josh Boyer <jwboyer@redhat.com>
- Fix power management sysfs on non-secure boot machines (rhbz 896243)

* Wed Jan 16 2013 Dave Jones <davej@redhat.com>
- Experiment: Double the length of the brcmsmac transmit timeout.

* Wed Jan 16 2013 Josh Boyer <jwboyer@redhat.com>
- Add patch from Stanislaw Gruszka to fix iwlegacy IBSS cleanup (rhbz 886946)

* Tue Jan 15 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc3.git2.1
- Linux v3.8-rc3-293-g406089d

* Tue Jan 15 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_DVB_USB_V2 (rhbz 895460)

* Mon Jan 14 2013 Josh Boyer <jwboyer@redhat.com>
- Enable Orinoco drivers in kernel-modules-extra (rhbz 894069)

* Mon Jan 14 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc3.git1.1
- Linux v3.8-rc3-74-gb719f43

* Fri Jan 11 2013 Josh Boyer <jwboyer@redhat.com>
- Update secure-boot patchset

* Thu Jan 10 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc3.git0.2
- Reenable debugging options.

* Thu Jan 10 2013 Dave Jones <davej@redhat.com>
- Drop old Montevina era E1000 workaround.

* Thu Jan 10 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc3.git0.1
- Linux v3.8-rc3
- Disable debugging options.

* Wed Jan 09 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc2.git4.1
- Linux v3.8-rc2-370-g57a0c1e

* Wed Jan  9 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM mvebu config

* Wed Jan 09 2013 Josh Boyer <jwboyer@redhat.com>
- Enable CONFIG_CIFS_DEBUG as it was on before it was split out

* Tue Jan 08 2013 Kyle McMartin <kmcmarti@redhat.com>
- Ensure modules are signed even if *-debuginfo rpms are not produced by
  re-defining __spec_install_post and adding a hook after all strip
  invocations. Ideally, in the future, we could patch the rpm macro and
  remove the re-define from kernel.spec, but that's another windmill to tilt
  at.

* Tue Jan 08 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc2.git3.1
- Linux v3.8-rc2-222-g2a893f9

* Mon Jan 07 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc2.git2.1
- Linux v3.8-rc2-191-gd287b87
- remove the namei-include.patch, it's upstream now

* Mon Jan 07 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc2.git1.2
- Reenable debugging options.

* Mon Jan  7 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Further ARM config updates
- Add patch to fix building omapdrm

* Mon Jan 07 2013 Justin M. Forbes <jforbes@redhat.com>
- Bye sparc

* Mon Jan 07 2013 Justin M. Forbes <jforbes@redhat.com>
- Fix up configs for build

* Mon Jan 07 2013 Josh Boyer <jwboyer@redhat.com>
- Patch to fix efivarfs underflow from Lingzhu Xiang (rhbz 888163)

* Sat Jan  5 2013 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial update of ARM configs for 3.8
- Enable DRM driver for tegra
- Drop separate imx kernel. Will be reintroduced soon in unified

* Fri Jan 04 2013 Justin M. Forbes <jforbes@redhat.com> - 3.8.0-0.rc2.git1.1
- Linux v3.8-rc2-116-g5f243b9

* Thu Jan 03 2013 Justin M. Forbes <jforbes@redhat.com>
- Initial 3.8-rc2 rebase

* Wed Jan 02 2013 Josh Boyer <jwboyer@redhat.com>
- BR the hostname package (rhbz 886113)

* Tue Dec 18 2012 Dave Jones <davej@redhat.com>
- On rebases, list new config options.
  (Revert to pre-18 behaviour)

* Mon Dec 17 2012 Josh Boyer <jwboyer@redhat.com>
- Fix oops in sony-laptop setup (rhbz 873107)

* Fri Dec 14 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix arm imx drm driver build

* Wed Dec 12 2012 Josh Boyer <jwboyer@redhat.com>
- Fix infinite loop in efi signature parser
- Don't error out if db doesn't exist

* Tue Dec 11 2012 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM configs for latest 3.7
- Drop highbank kernel build variant as its in unified kernel

* Tue Dec 11 2012 Josh Boyer <jwboyer@redhat.com>
- Update secure boot patches to include MoK support
- Fix IBSS scanning in mac80211 (rhbz 883414)

* Tue Dec 11 2012 Dave Jones <davej@redhat.com> - 3.7.0-2
- Reenable debugging options.

* Tue Dec 11 2012 Dave Jones <davej@redhat.com> - 3.7.0-1
- Linux v3.7

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
