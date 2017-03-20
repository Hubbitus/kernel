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
%global signkernel 1
%global signmodules 1
%global zipmodules 1
%else
%global signkernel 0
%global signmodules 1
%global zipmodules 0
%endif

%if %{zipmodules}
%global zipsed -e 's/\.ko$/\.ko.xz/'
%endif

# define buildid .local

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
%define base_sublevel 10

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 4.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%global rcrev 3
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 4.%{upstream_sublevel}.0
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
# kernel PAE (only valid for i686 (PAE) and ARM (lpae))
%define with_pae       %{?_without_pae:       0} %{?!_without_pae:       1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
%define with_cross_headers   %{?_without_cross_headers:   0} %{?!_without_cross_headers:   1}
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
%define debugbuildsenabled 1

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
%define kversion 4.%{base_sublevel}

%define make_target bzImage
%define image_install_path boot

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
# Needed because we override almost everything involving build-ids
# and debuginfo generation. Currently we rely on the old alldebug setting.
%global _build_id_links alldebug

# kernel PAE is only built on i686 and ARMv7.
%ifnarch i686 armv7hl
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_pae 0
%define with_debug 0
%endif

# if requested, only build pae kernel
%if %{with_paeonly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%define with_pae 0
%endif
%define with_pae 0
%define with_tools 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 %{power64} s390 s390x aarch64
%endif

# Overrides for generic default options

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_cross_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# bootwrapper is only on ppc
# sparse blows up on ppc
%ifnarch %{power64}
%define with_bootwrapper 0
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
%define pae PAE
%define all_arch_configs kernel-%{version}-i?86*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch %{power64}
%define asmarch powerpc
%define hdrarch powerpc
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%ifarch ppc64 ppc64p7
%define all_arch_configs kernel-%{version}-ppc64*.config
%endif
%ifarch ppc64le
%define all_arch_configs kernel-%{version}-ppc64le*.config
%endif
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_tools 0
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
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
%define with_cross_headers 0
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
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}
%define listnewconfig_fail 0
%define configmismatch_fail 0
%else
%define listnewconfig_fail 1
%define configmismatch_fail 1
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
%define cpupowerarchs %{ix86} x86_64 %{power64} %{arm} aarch64

#
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  coreutils, systemd >= 203-2, /usr/bin/kernel-install
%define initrd_prereq  dracut >= 027


Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2 and Redistributable, no modification permitted
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: %{all_x86} x86_64 ppc64 ppc64p7 s390 s390x %{arm} aarch64 ppc64le
ExclusiveOS: Linux
%ifnarch %{nobuildarches}
Requires: kernel-core-uname-r = %{KVERREL}%{?variant}
Requires: kernel-modules-uname-r = %{KVERREL}%{?variant}
%endif


#
# List the packages used during the kernel build
#
BuildRequires: kmod, patch, bash, sh-utils, tar, git
BuildRequires: bzip2, xz, findutils, gzip, m4, perl, perl-Carp, perl-devel, perl-generators, make, diffutils, gawk
BuildRequires: gcc, binutils, redhat-rpm-config, hmaccalc
BuildRequires: net-tools, hostname, bc, elfutils-devel
%if %{with_sparse}
BuildRequires: sparse
%endif
%if %{with_perf}
BuildRequires: zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed) bison flex xz-devel
BuildRequires: audit-libs-devel
%ifnarch s390 s390x %{arm}
BuildRequires: numactl-devel
%endif
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext ncurses-devel
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb
%if %{with_debuginfo}
BuildRequires: rpm-build, elfutils
%define debuginfo_args --strict-build-id -r
%endif

%if %{signkernel}%{signmodules}
BuildRequires: openssl openssl-devel
%if %{signkernel}
BuildRequires: pesign >= 0.10-4
%endif
%endif

%if %{with_cross}
BuildRequires: binutils-%{_build_arch}-linux-gnu, gcc-%{_build_arch}-linux-gnu
%define cross_opts CROSS_COMPILE=%{_build_arch}-linux-gnu-
%endif

Source0: https://www.kernel.org/pub/linux/kernel/v4.x/linux-%{kversion}.tar.xz

Source10: perf-man-%{kversion}.tar.gz
Source11: x509.genkey
Source12: remove-binary-diff.pl
Source15: merge.pl
Source16: mod-extra.list
Source17: mod-extra.sh
Source18: mod-sign.sh
Source90: filter-x86_64.sh
Source91: filter-armv7hl.sh
Source92: filter-i686.sh
Source93: filter-aarch64.sh
Source95: filter-ppc64.sh
Source96: filter-ppc64le.sh
Source97: filter-s390x.sh
Source98: filter-ppc64p7.sh
Source99: filter-modules.sh
%define modsign_cmd %{SOURCE18}

Source20: kernel-aarch64.config
Source21: kernel-aarch64-debug.config
Source22: kernel-armv7hl.config
Source23: kernel-armv7hl-debug.config
Source24: kernel-armv7hl-lpae.config
Source25: kernel-armv7hl-lpae-debug.config
Source26: kernel-i686.config
Source27: kernel-i686-debug.config
Source28: kernel-i686-PAE.config
Source29: kernel-i686-PAEdebug.config
Source30: kernel-ppc64.config
Source31: kernel-ppc64-debug.config
Source32: kernel-ppc64le.config
Source33: kernel-ppc64le-debug.config
Source34: kernel-ppc64p7.config
Source35: kernel-ppc64p7-debug.config
Source36: kernel-s390x.config
Source37: kernel-s390x-debug.config
Source38: kernel-x86_64.config
Source39: kernel-x86_64-debug.config

Source40: generate_all_configs.sh
Source41: generate_debug_configs.sh

Source42: check_configs.awk

# This file is intentionally left empty in the stock kernel. Its a nicety
# added for those wanting to do custom rebuilds with altered config opts.
Source1000: kernel-local

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-4.%{base_sublevel}.%{stable_base}.xz
Source5000: %{stable_patch_00}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Source5000: patch-4.%{upstream_sublevel}-rc%{rcrev}.xz
%if 0%{?gitrev}
Source5001: patch-4.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.xz
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Source5000: patch-4.%{base_sublevel}-git%{gitrev}.xz
%endif
%endif
%endif

## Patches needed for building this package

# build tweak for build ID magic, even for -vanilla
Patch001: kbuild-AFTER_LINK.patch

## compile fixes

# ongoing complaint, full discussion delayed until ksummit/plumbers
Patch002: 0001-iio-Use-event-header-from-kernel-tree.patch

%if !%{nopatches}

# Git trees.

# Standalone patches

# a tempory patch for QCOM hardware enablement. Will be gone by end of 2016/F-26 GA
Patch420: qcom-QDF2432-tmp-errata.patch

# http://www.spinics.net/lists/arm-kernel/msg490981.html
Patch421: geekbox-v4-device-tree-support.patch

# http://www.spinics.net/lists/linux-tegra/msg26029.html
Patch422: usb-phy-tegra-Add-38.4MHz-clock-table-entry.patch

# Fix OMAP4 (pandaboard)
Patch423: arm-revert-mmc-omap_hsmmc-Use-dma_request_chan-for-reque.patch

# Not particularly happy we don't yet have a proper upstream resolution this is the right direction
# https://www.spinics.net/lists/arm-kernel/msg535191.html
Patch424: arm64-mm-Fix-memmap-to-be-initialized-for-the-entire-section.patch

# http://patchwork.ozlabs.org/patch/587554/
Patch425: ARM-tegra-usb-no-reset.patch

Patch426: AllWinner-h3.patch
Patch427: AllWinner-net-emac.patch

# http://www.spinics.net/lists/devicetree/msg163238.html
Patch430: bcm2837-initial-support.patch

# http://www.spinics.net/lists/dri-devel/msg132235.html
Patch433: drm-vc4-Fix-OOPSes-from-trying-to-cache-a-partially-constructed-BO..patch

# bcm283x mmc for wifi http://www.spinics.net/lists/arm-kernel/msg567077.html
Patch434: bcm283x-mmc-bcm2835.patch

# Upstream fixes for i2c/serial/ethernet MAC addresses
Patch435: bcm283x-fixes.patch

# https://lists.freedesktop.org/archives/dri-devel/2017-February/133823.html
Patch436: vc4-fix-vblank-cursor-update-issue.patch

# http://www.spinics.net/lists/arm-kernel/msg552554.html
Patch438: arm-imx6-hummingboard2.patch

Patch460: lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

Patch466: input-kill-stupid-messages.patch

Patch467: die-floppy-die.patch

Patch468: no-pcspkr-modalias.patch

Patch470: silence-fbcon-logo.patch

Patch471: Kbuild-Add-an-option-to-enable-GCC-VTA.patch

Patch472: crash-driver.patch

Patch473: efi-lockdown.patch

Patch487: Add-EFI-signature-data-types.patch

Patch488: Add-an-EFI-signature-blob-parser-and-key-loader.patch

# This doesn't apply. It seems like it could be replaced by
# https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5ac7eace2d00eab5ae0e9fdee63e38aee6001f7c
# which has an explicit line about blacklisting
Patch489: KEYS-Add-a-system-blacklist-keyring.patch

Patch490: MODSIGN-Import-certificates-from-UEFI-Secure-Boot.patch

Patch491: MODSIGN-Support-not-importing-certs-from-db.patch

Patch493: drm-i915-hush-check-crtc-state.patch

Patch494: disable-i8042-check-on-apple-mac.patch

Patch495: lis3-improve-handling-of-null-rate.patch

Patch497: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

Patch498: criu-no-expert.patch

Patch499: ath9k-rx-dma-stop-check.patch

Patch500: xen-pciback-Don-t-disable-PCI_COMMAND-on-PCI-device-.patch

Patch501: Input-synaptics-pin-3-touches-when-the-firmware-repo.patch

Patch502: firmware-Drop-WARN-from-usermodehelper_read_trylock-.patch

# Patch503: drm-i915-turn-off-wc-mmaps.patch

Patch509: MODSIGN-Don-t-try-secure-boot-if-EFI-runtime-is-disa.patch

#CVE-2016-3134 rhbz 1317383 1317384
Patch665: netfilter-x_tables-deal-with-bogus-nextoffset-values.patch

# grabbed from mailing list
Patch667: v3-Revert-tty-serial-pl011-add-ttyAMA-for-matching-pl011-console.patch

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
Provides: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
Requires(pre): linux-firmware >= 20150904-56.git6ebf5d57\
Requires(preun): systemd >= 200\
Conflicts: xfsprogs < 4.3.0-1\
Conflicts: xorg-x11-drv-vmmouse < 13.0.99\
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
%if "0%{?variant}"
Obsoletes: kernel-headers < %{rpmversion}-%{pkg_release}
Provides: kernel-headers = %{rpmversion}-%{pkg_release}
%endif
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc
Group: Development/System
%description cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.


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
Provides: installonlypkg(kernel)
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
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/lsgpio(\.debug)?|.*%%{_bindir}/gpio-hammer(\.debug)?|.*%%{_bindir}/gpio-event-mon(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

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
Provides: installonlypkg(kernel)\
AutoReqProv: no\
%description %{?1:%{1}-}debuginfo\
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
Provides: kernel-devel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
AutoReqProv: no\
Requires(pre): findutils\
Requires: findutils\
Requires: perl\
%description %{?1:%{1}-}devel\
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
Provides: kernel%{?1:-%{1}}-modules-extra-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules-extra\
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
Provides: kernel%{?1:-%{1}}-modules-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Requires: kernel-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
AutoReq: no\
AutoProv: yes\
%description %{?1:%{1}-}modules\
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
Requires: kernel-%{1}-core-uname-r = %{KVERREL}%{?variant}+%{1}\
Requires: kernel-%{1}-modules-uname-r = %{KVERREL}%{?variant}+%{1}\
Provides: installonlypkg(kernel)\
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
Provides: kernel-%{?1:%{1}-}core-uname-r = %{KVERREL}%{?variant}%{?1:+%{1}}\
Provides: installonlypkg(kernel)\
%{expand:%%kernel_reqprovconf}\
%if %{?1:1} %{!?1:0} \
%{expand:%%kernel_meta_package %{?1:%{1}}}\
%endif\
%{expand:%%kernel_devel_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_modules_extra_package %{?1:%{1}} %{!?{-n}:%{1}}%{?{-n}:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %{?1:%{1}}}\
%{nil}

# Now, each variant package.

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
    if [ "${patch:0:8}" != "patch-4." ] ; then
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
%define vanillaversion 4.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 4.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 4.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 4.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 4.%{base_sublevel}
%endif
%endif
%endif

# %%{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %%{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%%{kversion}%%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-4.*' \
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

cp %{SOURCE12} .

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    xzcat %{SOURCE5000} | ./remove-binary-diff.pl | patch -p1 -F1 -s
%if 0%{?gitrev}
    xzcat %{SOURCE5001} | ./remove-binary-diff.pl | patch -p1 -F1 -s
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    xzcat %{SOURCE5000} | ./remove-binary-diff.pl | patch -p1 -F1 -s
%endif
%endif
    git init
    git config user.email "kernel-team@fedoraproject.org"
    git config user.name "Fedora Kernel Team"
    git config gc.auto 0
    git add .
    git commit -a -q -m "baseline"

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
if [ ! -d .git ]; then
    git init
    git config user.email "kernel-team@fedoraproject.org"
    git config user.name "Fedora Kernel Team"
    git config gc.auto 0
    git add .
    git commit -a -q -m "baseline"
fi


# released_kernel with possible stable updates
%if 0%{?stable_base}
# This is special because the kernel spec is hell and nothing is consistent
xzcat %{SOURCE5000} | patch -p1 -F1 -s
git commit -a -m "Stable update"
%endif

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .
cp %{SOURCE1000} .
cp %{SOURCE15} .
cp %{SOURCE40} .
cp %{SOURCE41} .

%if !%{debugbuildsenabled}
# The normal build is a really debug build and the user has explicitly requested
# a release kernel. Change the config files into non-debug versions.
%if !%{with_release}
VERSION=%{version} ./generate_debug_configs.sh
%else
VERSION=%{version} ./generate_all_configs.sh
%endif

%else
VERSION=%{version} ./generate_all_configs.sh
%endif

# Merge in any user-provided local config option changes
%ifnarch %nobuildarches
for i in %{all_arch_configs}
do
  mv $i $i.tmp
  ./merge.pl %{SOURCE1000} $i.tmp > $i
  rm $i.tmp
done
%endif

# Note: Even in the "nopatches" path some patches (build tweaks and compile
# fixes) will always get applied; see patch defition above for details

git am %{patches}

# END OF PATCH APPLICATIONS

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

CheckConfigs() {
     ./check_configs.awk $1 $2 > .mismatches
     if [ -s .mismatches ]
     then
	echo "Error: Mismatches found in configuration files"
	cat .mismatches
	exit 1
     fi
}

cp %{SOURCE42} .
# now run oldconfig over all the config files
for i in *.config
do
  cat $i > temp-$i
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
%if %{configmismatch_fail}
  CheckConfigs configs/$i temp-$i
%endif
  rm temp-$i
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

    %if %{signkernel}%{signmodules}
    cp %{SOURCE11} certs/.
    %endif

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags} %{?kernel_mflags}
    %{make} -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

    mkdir -p $RPM_BUILD_ROOT/%{image_install_path}
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/%{image_install_path}
%endif

%ifarch %{arm} aarch64
    %{make} -s ARCH=$Arch V=1 dtbs dtbs_install INSTALL_DTBS_PATH=$RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer
    cp -r $RPM_BUILD_ROOT/%{image_install_path}/dtb-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/dtb
    find arch/$Arch/boot/dts -name '*.dtb' -type f | xargs rm -f
%endif

    # Start installing the results
    install -m 644 .config $RPM_BUILD_ROOT/boot/config-$KernelVer
    install -m 644 .config $RPM_BUILD_ROOT/lib/modules/$KernelVer/config
    install -m 644 System.map $RPM_BUILD_ROOT/boot/System.map-$KernelVer
    install -m 644 System.map $RPM_BUILD_ROOT/lib/modules/$KernelVer/System.map

    # We estimate the size of the initramfs because rpm needs to take this size
    # into consideration when performing disk space calculations. (See bz #530778)
    dd if=/dev/zero of=$RPM_BUILD_ROOT/boot/initramfs-$KernelVer.img bs=1M count=20

    if [ -f arch/$Arch/boot/zImage.stub ]; then
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/%{image_install_path}/zImage.stub-$KernelVer || :
      cp arch/$Arch/boot/zImage.stub $RPM_BUILD_ROOT/lib/modules/$KernelVer/zImage.stub-$KernelVer || :
    fi
    %if %{signkernel}
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
    cp $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer $RPM_BUILD_ROOT/lib/modules/$KernelVer/$InstallName

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;
    cp $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac $RPM_BUILD_ROOT/lib/modules/$KernelVer/.vmlinuz.hmac

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
    rm -rf $RPM_BUILD_ROOT/lib/modules/$KernelVer/vdso/.build-id
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
    if [ -f tools/objtool/objtool ]; then
      cp -a tools/objtool/objtool $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/tools/objtool/ || :
    fi
    if [ -d arch/$Arch/scripts ]; then
      cp -a arch/$Arch/scripts $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch} || :
    fi
    if [ -f arch/$Arch/*lds ]; then
      cp -a arch/$Arch/*lds $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/arch/%{_arch}/ || :
    fi
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*.o
    rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/scripts/*/*.o
%ifarch %{power64}
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
%ifarch aarch64
    # arch/arm64/include/asm/xen references arch/arm
    cp -a --parents arch/arm/include/asm/xen $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    # arch/arm64/include/asm/opcodes.h references arch/arm
    cp -a --parents arch/arm/include/asm/opcodes.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    # include the machine specific headers for ARM variants, if available.
%ifarch %{arm}
    if [ -d arch/%{asmarch}/mach-${Flavour}/include ]; then
      cp -a --parents arch/%{asmarch}/mach-${Flavour}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    # include a few files for 'make prepare'
    cp -a --parents arch/arm/tools/gen-mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/arm/tools/mach-types $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/

%endif
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include
%ifarch %{ix86} x86_64
    # files for 'make prepare' to succeed with kernel-devel
    cp -a --parents arch/x86/entry/syscalls/syscall_32.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscalltbl.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscallhdr.sh $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/entry/syscalls/syscall_64.tbl $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_32.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_64.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs_common.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/tools/relocs.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents tools/include/tools/le_byteshift.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/purgatory.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/sha256.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/sha256.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/stack.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/setup-x86_64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/purgatory/entry64.S $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/string.c $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    cp -a --parents arch/x86/boot/ctype.h $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
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

    # Call the modules-extra script to move things around
    %{SOURCE17} $RPM_BUILD_ROOT/lib/modules/$KernelVer %{SOURCE16}

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
    find lib/modules/$KernelVer/kernel -mindepth 1 -type d | sort -n > module-dirs.list

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
    cp certs/signing_key.pem certs/signing_key.pem.sign${Flav}
    cp certs/signing_key.x509 certs/signing_key.x509.sign${Flav}
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

%global perf_make \
  make -s EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 NO_JVMTI=1 prefix=%{_prefix}
%if %{with_perf}
# perf
# make sure check-headers.sh is executable
chmod +x tools/perf/check-headers.sh
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
pushd tools/iio/
%{make}
popd
pushd tools/gpio/
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
      %{modsign_cmd} certs/signing_key.pem.sign+%{pae} certs/signing_key.x509.sign+%{pae} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}/ \
    fi \
    if [ "%{with_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+debug certs/signing_key.x509.sign+debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+debug/ \
    fi \
    if [ "%{with_pae_debug}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign+%{pae}debug certs/signing_key.x509.sign+%{pae}debug $RPM_BUILD_ROOT/lib/modules/%{KVERREL}+%{pae}debug/ \
    fi \
    if [ "%{with_up}" -ne "0" ]; then \
      %{modsign_cmd} certs/signing_key.pem.sign certs/signing_key.x509.sign $RPM_BUILD_ROOT/lib/modules/%{KVERREL}/ \
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

%if %{with_cross_headers}
mkdir -p $RPM_BUILD_ROOT/usr/tmp-headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr/tmp-headers headers_install_all

find $RPM_BUILD_ROOT/usr/tmp-headers/include \
     \( -name .install -o -name .check -o \
        -name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# Copy all the architectures we care about to their respective asm directories
for arch in arm arm64 powerpc s390 x86 ; do
mkdir -p $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include
mv $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-${arch} $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/asm
cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-generic $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/.
done

# Remove the rest of the architectures
rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/arch*
rm -rf $RPM_BUILD_ROOT/usr/tmp-headers/include/asm-*

# Copy the rest of the headers over
for arch in arm arm64 powerpc s390 x86 ; do
cp -a $RPM_BUILD_ROOT/usr/tmp-headers/include/* $RPM_BUILD_ROOT/usr/${arch}-linux-gnu/include/.
done

rm -rf $RPM_BUILD_ROOT/usr/tmp-headers
%endif

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT lib=%{_lib} install-bin install-traceevent-plugins
# remove the 'trace' symlink.
rm -f %{buildroot}%{_bindir}/trace
# remove the perf-tips
rm -rf %{buildroot}%{_docdir}/perf-tip

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
pushd tools/iio
make INSTALL_ROOT=%{buildroot} install
popd
pushd tools/gpio
make DESTDIR=%{buildroot} install
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
%post -n kernel-tools-libs
/sbin/ldconfig

%postun -n kernel-tools-libs
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
/bin/kernel-install add %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_modules_post %{?-v*}}\
%{expand:%%kernel_modules_extra_post %{?-v*}}\
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
/bin/kernel-install remove %{KVERREL}%{?1:+%{1}} /lib/modules/%{KVERREL}%{?1:+%{1}}/vmlinuz || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

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

%if %{with_cross_headers}
%files cross-headers
%defattr(-,root,root)
/usr/*-linux-gnu/include/*
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
%{_datadir}/perf-core/*
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
%{_bindir}/iio_event_monitor
%{_bindir}/iio_generic_buffer
%{_bindir}/lsiio
%{_bindir}/lsgpio
%{_bindir}/gpio-hammer
%{_bindir}/gpio-event-mon
%endif

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.1

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
%{!?_licensedir:%global license %%doc}\
%license linux-%{KVERREL}/COPYING\
/lib/modules/%{KVERREL}%{?2:+%{2}}/%{?-k:%{-k*}}%{!?-k:vmlinuz}\
%ghost /%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:+%{2}}\
/lib/modules/%{KVERREL}%{?2:+%{2}}/.vmlinuz.hmac \
%ghost /%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:+%{2}}.hmac \
%ifarch %{arm} aarch64\
/lib/modules/%{KVERREL}%{?2:+%{2}}/dtb \
%ghost /%{image_install_path}/dtb-%{KVERREL}%{?2:+%{2}} \
%endif\
%attr(600,root,root) /lib/modules/%{KVERREL}%{?2:+%{2}}/System.map\
%ghost /boot/System.map-%{KVERREL}%{?2:+%{2}}\
/lib/modules/%{KVERREL}%{?2:+%{2}}/config\
%ghost /boot/config-%{KVERREL}%{?2:+%{2}}\
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
%defverify(not mtime)\
/usr/src/kernels/%{KVERREL}%{?2:+%{2}}\
%{expand:%%files %{?2:%{2}-}modules-extra}\
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
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} %{pae}
%kernel_variant_files %{with_pae_debug} %{pae}debug

# plz don't put in a version string unless you're going to tag
# and build.
#
#
%changelog
* Mon Mar 20 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc3.git0.1
- Linux v4.11-rc3
- Fix for debuginfo conflicts (rhbz 1431296)

* Mon Mar 20 2017 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options.

* Sun Mar 19 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Rebase AllWinner sun8i emac driver to latest proposed upstream

* Fri Mar 17 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc2.git4.1
- Linux v4.11-rc2-235-gd528ae0

* Thu Mar 16 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable STi Serial Console

* Thu Mar 16 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc2.git3.1
- Linux v4.11-rc2-208-g69eea5a

* Wed Mar 15 2017 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options like nothing ever happened.

* Wed Mar 15 2017 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options for sync to f26

* Wed Mar 15 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc2.git2.1
- Linux v4.11-rc2-157-gae50dfd

* Tue Mar 14 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- bcm283x mmc improvements round 2

* Tue Mar 14 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc2.git1.1
- Linux v4.11-rc2-24-gfb5fe0f

* Tue Mar 14 2017 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options.

* Mon Mar 13 2017 Peter Robinson <pbrobinson@fedoraproject.org> 4.11.0-0.rc2.git0.2
- Disable bcm283x mmc improvements due to corner case issues

* Mon Mar 13 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc2.git0.1
- Linux v4.11-rc2

* Mon Mar 13 2017 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options.

* Sun Mar 12 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Update kernel source location now ftp is retired
- Enable STi h407 SoC
- Minor ARM config cleanups
- bcm283x mmc driver improvements

* Fri Mar 10 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc1.git3.1
- Linux v4.11-rc1-136-gc1aa905

* Thu Mar 09 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc1.git2.1
- Linux v4.11-rc1-96-gea6200e

* Thu Mar 09 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc1.git1.2
- Bump and build for updated buildroot

* Wed Mar 08 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc1.git1.1
- Linux v4.11-rc1-88-gec3b93a

* Wed Mar 08 2017 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options.

* Tue Mar 07 2017 Laura Abbott <labbott@fedoraproject.org>
- CVE-2017-2636 Race condition access to n_hdlc.tbuf causes double free in n_hdlc_release (rhbz 1430049)

* Mon Mar 06 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc1.git0.1
- Linux v4.11-rc1

* Mon Mar 06 2017 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options.

* Fri Mar 03 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git9.1
- Linux v4.10-11319-gc82be9d

* Thu Mar 02 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git8.2
- rebuilt

* Thu Mar 02 2017 Laura Abbott <labbott@fedoraproject.org>
- Enable CONFIG_NET_L3_MASTER_DEV (rhbz 1428530)

* Thu Mar 02 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git8.1
- Linux v4.10-11073-g4977ab6

* Wed Mar 01 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git7.1
- Linux v4.10-10770-g2d6be4a

* Wed Mar  1 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Tiny DRM on ARM platforms
- ARM config updates
- General config cleanups
- Add patch to fix desktop lockups on RPi (vc4) RHBZ# 1389163

* Tue Feb 28 2017 Laura Abbott <labbott@fedoraproject.org>
- Fix for yet another stack variable in crypto (rhbz 1427593)

* Tue Feb 28 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git6.1
- Linux v4.10-10531-g86292b3

* Tue Feb 28 2017 Thorsten Leemhuis <fedora@leemhuis.info>
- apply patches with build tweaks (build-AFTER-LINK.patch) and compile fixes
  all the time

* Tue Feb 28 2017 Justin M. Forbes <jforbes@fedoraproject.org> 
- Fix kernel-devel virtual provide

* Mon Feb 27 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git5.1
- Linux v4.10-10320-ge5d56ef
- Disable a series of s390x configuration options

* Fri Feb 24 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git4.1
- Linux v4.10-9579-gf1ef09f

* Thu Feb 23 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git3.1
- Linux v4.10-6476-gbc49a78

* Wed Feb 22 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git2.1
- Linux v4.10-2512-g7bb0338

* Tue Feb 21 2017 Laura Abbott <labbott@fedoraproject.org> - 4.11.0-0.rc0.git1.1

- Linux v4.10-1242-g9763dd6

* Tue Feb 21 2017 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options.

* Mon Feb 20 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-1
- Disable debugging options.
- Linux v4.10

* Sat Feb 18 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Update some Raspberry Pi patches
- Add Raspberry Pi fixes for UART/i2c/stable eth MAC

* Fri Feb 17 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc8.git2.1
- Linux v4.10-rc8-62-g6dc39c5

* Thu Feb 16 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc8.git1.1
- Linux v4.10-rc8-39-g5a81e6a

* Wed Feb 15 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable PWRSEQ_SIMPLE module (fixes rhbz 1377816)
- Add patch to work around crash on RPi3

* Tue Feb 14 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc8.git0.2
- Reenable debugging options.
- CVE-2017-5967 Disable CONFIG_TIMER_STATS (rhbz 1422138 1422140)

* Mon Feb 13 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc8.git0.1
- Disable debugging options.
- Linux v4.10-rc8

* Fri Feb 10 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc7.git4.1
- Linux v4.10-rc7-127-g3d88460

* Thu Feb 09 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc7.git3.1
- Linux v4.10-rc7-114-g55aac6e

* Thu Feb  9 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix OOPSes in vc4 (Raspberry Pi)

* Wed Feb 08 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc7.git2.1
- Linux v4.10-rc7-65-g926af627

* Tue Feb 07 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc7.git1.1
- Linux v4.10-rc7-29-g8b1b41e
- Reenable debugging options.
- CVE-2017-5897 ip6_gre: Invalid reads in ip6gre_err (rhbz 1419848 1419851)

* Mon Feb 06 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc7.git0.1
- Disable debugging options.
- Linux v4.10-rc7

* Fri Feb 03 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc6.git3.1
- Linux v4.10-rc6-110-g34e00ac

* Wed Feb 01 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc6.git2.1
- Linux v4.10-rc6-85-g6d04dfc
- enable CONFIG_SENSORS_JC42 (rhbz 1417454)

* Tue Jan 31 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc6.git1.1
- Linux v4.10-rc6-24-gf1774f4
- Reenable debugging options.
- Fix kvm nested virt CVE-2017-2596 (rhbz 1417812 1417813)

* Mon Jan 30 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc6.git0.1
- Linux v4.10-rc6
- Disable debugging options.

* Sat Jan 28 2017 Laura Abbott <labbott@redhat.com> - 4.10.0-0.rc5.git4.2
- Temporary workaround for gcc7 and arm64

* Fri Jan 27 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git4.1
- Linux v4.10-rc5-367-g1b1bc42

* Thu Jan 26 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git3.1
- Linux v4.10-rc5-122-gff9f8a7

* Thu Jan 26 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- arm64: dma-mapping: Fix dma_mapping_error() when bypassing SWIOTLB

* Wed Jan 25 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git2.1
- Linux v4.10-rc5-107-g883af14
- CVE-2017-5576 CVE-2017-5577 vc4 overflows (rhbz 1416436 1416437 1416439)

* Tue Jan 24 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git1.1
- Linux v4.10-rc5-71-ga4685d2

* Tue Jan 24 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git0.2
- Reenable debugging options.

* Mon Jan 23 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc5.git0.1
- Linux v4.10-rc5
- Disable debugging options.

* Fri Jan 20 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git4.1
- Linux v4.10-rc4-199-ge90665a

* Fri Jan 20 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Initial DT support for Hummingboard 2 (Edge/Gate)

* Thu Jan 19 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git3.1
- Linux v4.10-rc4-122-g81aaeaa

* Wed Jan 18 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git2.1
- Linux v4.10-rc4-101-gfa19a76

* Wed Jan 18 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable bcm283x VEC composite output

* Tue Jan 17 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git1.1
- Linux v4.10-rc4-78-g4b19a9e

* Tue Jan 17 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git0.3
- Reenable debugging options.

* Mon Jan 16 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc4.git0.1
- Disable debugging options.
- Linux v4.10-rc4

* Mon Jan 16 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM updates

* Fri Jan 13 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git4.1
- Linux v4.10-rc3-187-g557ed56

* Thu Jan 12 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git3.1
- Linux v4.10-rc3-163-ge28ac1f

* Wed Jan 11 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git2.1
- Linux v4.10-rc3-98-gcff3b2c

* Tue Jan 10 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git1.1
- Linux v4.10-rc3-52-gbd5d742

* Tue Jan 10 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git0.2
- Reenable debugging options.

* Mon Jan 09 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc3.git0.1
- Disable debugging options.
- Linux v4.10-rc3

* Mon Jan  9 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to improve MMC/SD speed on Raspberry Pi (bcm283x)

* Fri Jan 06 2017 Laura Abbott <labbott@fedoraproject.org>
- Disable JVMTI for perf (rhbz 1410296)

* Fri Jan 06 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git4.1
- Linux v4.10-rc2-207-g88ba6ca

* Fri Jan  6 2017 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates

* Thu Jan 05 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git3.1
- Linux v4.10-rc2-183-gc433eb7

* Wed Jan 04 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git2.1
- Linux v4.10-rc2-43-g62f8c40

* Tue Jan 03 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git1.1
- Linux v4.10-rc2-20-g0f64df3

* Tue Jan 03 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git0.3
- Reenable debugging options.

* Tue Jan 03 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git0.2
- Disable debugging options.

* Mon Jan 02 2017 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc2.git0.1
- Linux v4.10-rc2

* Thu Dec 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc1.git1.1
- Linux v4.10-rc1-17-g2d706e7
- Fix generate-git-snapshtot.sh to work with SHA512 sources

* Tue Dec 27 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Linux v4.10-rc1
- ARM config updates, minor general config cleanups
- Enable Amlogic (meson) SoCs for ARMv7/aarch64

* Fri Dec 23 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git9.1
- Linux v4.9-11999-g50f6584

* Thu Dec 22 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git8.1
- Linux v4.9-11937-g52bce91

* Wed Dec 21 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git7.1
- Linux v4.9-11893-gba6d973

* Tue Dec 20 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git6.1
- Linux v4.9-11815-ge93b1cc

* Tue Dec 20 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates
- Enable some Qualcomm QDF2432 server platform options

* Mon Dec 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git5.1
- Linux v4.9-11744-gb0b3a37

* Fri Dec 16 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git4.1
- Linux v4.9-10415-g73e2e0c

* Thu Dec 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git3.1
- Linux v4.9-8648-g5cc60ae

* Wed Dec 14 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git2.1
- Linux v4.9-7150-gcdb98c2

* Tue Dec 13 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.10.0-0.rc0.git1.1
- Linux v4.9-2682-ge7aa8c2

* Tue Dec 13 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.9.0-2
- Reenable debugging options.

* Mon Dec 12 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-1
- Linux v4.9

* Mon Dec 12 2016 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options.

* Sat Dec 10 2016 Christopher Covington <cov@codeaurora.org>
- Re-add ACPI SPCR (serial console) support

* Fri Dec 09 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc8.git4.1
- Linux v4.9-rc8-85-ga37102d

* Thu Dec 08 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc8.git3.1
- Linux v4.9-rc8-78-g318c893

* Thu Dec 08 2016 Peter Jones <pjones@redhat.com>
- Work around thinkpad firmware memory layout issues and efi_mem_reserve()

* Wed Dec 07 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc8.git2.1
- Linux v4.9-rc8-55-gce779d6
- Disable CONFIG_AF_KCM (rhbz 1402489)

* Tue Dec 06 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc8.git1.1
- Linux v4.9-rc8-9-gd9d0452
- Fix DMA from stack in virtio-net (rhbz 1401612)

* Tue Dec 06 2016 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options.

* Mon Dec 05 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc8.git0.1
- Linux v4.9-rc8

* Mon Dec 05 2016 Laura Abbott <labbott@fedoraproject.org>
- Disable debugging options.

* Fri Dec 02 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc7.git4.1
- Linux v4.9-rc7-45-g2caceb3

* Thu Dec 01 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc7.git3.1
- Linux v4.9-rc7-39-g43c4f67

* Wed Nov 30 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc7.git2.1
- Linux v4.9-rc7-23-gded6e84

* Tue Nov 29 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add upstream i.MX6sx Udoo NEO support

* Tue Nov 29 2016 Laura Abbott <labbott@fedoraproject.org> - 4.9.0-0.rc7.git1.1
- Linux v4.9-rc7-7-g88abd82

* Tue Nov 29 2016 Laura Abbott <labbott@fedoraproject.org>
- Reenable debugging options.

* Mon Nov 28 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc7.git0.1
- Linux v4.9-rc7

* Mon Nov 28 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Mon Nov 28 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates
- General config cleanups
- Enable two 802.15.4 drivers
- Add upstream patch to fix all ARMv7 devices set to initial 200Mhz

* Wed Nov 23 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc6.git2.1
- Linux v4.9-rc6-124-gded9b5d

* Tue Nov 22 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc6.git1.1
- Linux v4.9-rc6-86-g3b404a5

* Tue Nov 22 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Tue Nov 22 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Dave Anderson to fix live system crash analysis on Aarch64

* Mon Nov 21 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc6.git0.1
- Linux v4.9-rc6

* Mon Nov 21 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Sun Nov 20 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Various ARMv7/aarch64 updates
- Enable CEC media input devices
- Build gpio tools
- General config cleanups

* Fri Nov 18 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc5.git4.1
- Linux v4.9-rc5-264-g6238986

* Thu Nov 17 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc5.git3.1
- Linux v4.9-rc5-213-g961b708
- Fix CIFS bug with VMAP_STACK

* Wed Nov 16 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc5.git2.1
- Linux v4.9-rc5-177-g81bcfe5

* Tue Nov 15 2016 Laura Abbott <labbott@redhat.com>
- Linux v4.9-rc5-172-ge76d21c

* Tue Nov 15 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Tue Nov 15 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch from Dan Horák to change default CPU type for s390x to z10

* Mon Nov 14 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc5.git0.1
- Linux v4.9-rc5

* Mon Nov 14 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Sun Nov 13 2016 Hans de Goede <jwrdegoede@fedoraproject.org>
- ARM config updates to fix boot issues on Allwinner A23, A31 and A33

* Fri Nov 11 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc4.git4.1
- Linux v4.9-rc4-107-g015ed94

* Thu Nov 10 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc4.git3.1
- Linux v4.9-rc4-58-g27bcd37

* Wed Nov 09 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc4.git2.1
- Linux v4.9-rc4-21-ge3a00f6

* Tue Nov 08 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc4.git1.1
- Linux v4.9-rc4-15-gb58ec8b

* Tue Nov 08 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Tue Nov  8 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Sync some ARM patches from F-25 branch

* Mon Nov 07 2016 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_EXT4_ENCRYPTION (rhbz 1389509)
- Enable CONFIG_NFSD_FLEXFILELAYOUT
- Enable CONFIG_HIST_TRIGGERS (rhbz 1390783)

* Mon Nov  7 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates

* Mon Nov 07 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc4.git0.1
- Linux v4.9-rc4

* Mon Nov 07 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Fri Nov 04 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc3.git2.1
- Linux v4.9-rc3-261-g577f12c

* Wed Nov  2 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Some OMAP4 fixes
- ARM64 fix for NUMA

* Tue Nov 01 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc3.git1.1
- Linux v4.9-rc3-243-g0c183d9

* Tue Nov 01 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Oct 31 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- arm64: Enable 48bit VA

* Mon Oct 31 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc3.git0.1
- Linux v4.9-rc3

* Mon Oct 31 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Fri Oct 28 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc2.git2.1
- Linux v4.9-rc2-138-g14970f2

* Thu Oct 27 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Refresh SB patchset to fix bisectability issue

* Thu Oct 27 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- CVE-2016-9083 CVE-2016-9084 vfio multiple flaws (rhbz 1389258 1389259 1389285)

* Tue Oct 25 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc2.git1.1
- Linux v4.9-rc2-40-g9fe68ca

* Tue Oct 25 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Oct 24 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc2.git0.2
- Rebuild for build problems
- Add fix for rng with VMAP_STACK (rhbz 1383451)

* Mon Oct 24 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc2.git0.1
- Linux v4.9-rc2

* Mon Oct 24 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Fri Oct 21 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.9.0-0.rc1.git4.1
- Linux v4.9-rc1-193-g6edc51a

* Thu Oct 20 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.9.0-0.rc1.git3.1
- Linux v4.9-rc1-145-gf4814e6

* Wed Oct 19 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc1.git2.1
- Linux v4.9-rc1-67-g1a1891d
- Switch to v2 of the aarch64 boot regression patch
- Enable CONFIG_LEDS_MLXCPLD per request on mailing list

* Tue Oct 18 2016 Laura Abbott <labbott@redhat.com>
- Gracefully bail out of secureboot when EFI runtime is disabled
- Fix for aarch64 boot regression (rhbz 1384701)

* Tue Oct 18 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable ACPI_CPPC_CPUFREQ on aarch64

* Tue Oct 18 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc1.git1.1
- Linux v4.9-rc1-3-g14155ca

* Tue Oct 18 2016 Laura Abbott <labbott@redhat.com>
- Reenable debugging options.

* Mon Oct 17 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc1.git0.2
- Disable CONFIG_RTC_DRV_DS1307_CENTURY

* Mon Oct 17 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc1.git0.1
- Linux v4.8-rc1

* Mon Oct 17 2016 Laura Abbott <labbott@redhat.com>
- Disable debugging options.

* Sat Oct 15 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config cleanups
- Re-enable omap-aes as should now be fixed

* Fri Oct 14 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git9.1
- Linux v4.8-14604-g29fbff8

* Thu Oct 13 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git8.1
- Linux v4.8-14230-gb67be92

* Wed Oct 12 2016 Laura Abbott <labbott@redhat.com>
- Add script to remove binary diffs

* Wed Oct 12 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git7.1
- Linux v4.8-14109-g1573d2c
- Drop the extra parallel build optiosn from perf since perf does that on
  its own.

* Wed Oct 12 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Adjust aarch64 config options

* Tue Oct 11 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git6.2
- Revert possible commits causing perf build failures

* Tue Oct 11 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git6.1
- Linux v4.8-11825-g101105b

* Mon Oct 10 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git5.2
- Fix typo in dts Makefile

* Mon Oct 10 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git5.1
- Linux v4.8-11417-g24532f7

* Fri Oct 07 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git4.1
- Linux v4.8-9431-g3477d16

* Thu Oct 06 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git3.2
- Disable CONFIG_DEBUG_TEST_DRIVER_REMOVE

* Thu Oct 06 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git3.1
- Linux v4.8-8780-gd230ec7

* Wed Oct 05 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git2.1
- Linux v4.8-2283-ga3443cd

* Tue Oct 04 2016 Laura Abbott <labbott@redhat.com> - 4.9.0-0.rc0.git1.1
- Linux v4.8-1558-g21f54dd
- Reenable debugging options.

* Mon Oct 03 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-1
- Disable debugging options.
- Linux v4.8

* Sun Oct  2 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM config cleanups, some minor general cleanups
- Some bcm283x VC4 fixes for Raspberry Pi

* Fri Sep 30 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc8.git3.1
- Linux v4.8-rc8-28-g9a2172a

* Thu Sep 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc8.git2.1
- Linux v4.8-rc8-13-g53061af

* Wed Sep 28 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc8.git1.1
- Linux v4.8-rc8-8-gae6dd8d
- Reenable debugging options.

* Mon Sep 26 2016 Laura Abbott <labbott@fedoraproject.org>
- Enable CONFIG_DEBUG_MODULE_RONX for arm targets

* Mon Sep 26 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc8.git0.1
- Linux v4.8-rc8
- Disable debugging options.

* Sun Sep 25 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Updates to crash driver from Dave Anderson

* Fri Sep 23 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc7.git4.1
- Linux v4.8-rc7-158-g78bbf15

* Thu Sep 22 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc7.git3.1
- Linux v4.8-rc7-142-gb1f2beb

* Wed Sep 21 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc7.git2.1
- Linux v4.8-rc7-42-g7d1e042

* Tue Sep 20 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc7.git1.1
- Linux v4.8-rc7-37-gd2ffb01
- Reenable debugging options.

* Mon Sep 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc7.git0.1
- Linux v4.8-rc7
- Disable debugging options.
- CVE-2016-7425 SCSI arcmsr buffer overflow (rhbz 1377330 1377331)

* Sat Sep 17 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable CPU IDLE on ARMv7
- Tweak big.LITTLE on ARMv7
- Update ARM64 pci-e quicks to latest upstream, update x-gene quirks patch

* Fri Sep 16 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc6.git4.1
- Linux v4.8-rc6-231-g024c7e3

* Thu Sep 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc6.git3.1
- Linux v4.8-rc6-214-g4cea877

* Thu Sep 15 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch for bcm2837 (RPi3) HDMI EDID detection

* Wed Sep 14 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc6.git2.1
- Linux v4.8-rc6-211-g77e5bdf

* Wed Sep 14 2016 Laura Abbott <labbott@fedoraproject.org>
- Fix for incorrect return checking in cpupower (rhbz 1374212)
- Let iio tools build on older kernels

* Tue Sep 13 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc6.git1.1
- Linux v4.8-rc6-147-ge8988e0
- Reenable debugging options.

* Mon Sep 12 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc6.git0.1
- Linux v4.8-rc6
- Disable debugging options.

* Sat Sep 10 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config tweaks

* Fri Sep 09 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc5.git4.1
- Linux v4.8-rc5-176-gd0acc7d

* Thu Sep 08 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc5.git3.1
- Linux v4.8-rc5-129-g711bef6

* Thu Sep  8 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable some popular audio addon drivers

* Wed Sep 07 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc5.git2.1
- Linux v4.8-rc5-62-gd060e0f
- Reenable debugging options.

* Tue Sep 06 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc5.git1.1
- Linux v4.8-rc5-5-gbc4dee5
- Disable debugging options.

* Sun Sep  4 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Use IIO BMP280 driver instead of old misc driver, wider HW support
- Minor sensor driver changes
- Disable omap_aes currently broken

* Fri Sep 02 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc4.git4.1
- Linux v4.8-rc4-199-gcc4163d

* Thu Sep 01 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc4.git3.1
- Linux v4.8-rc4-162-g071e31e

* Wed Aug 31 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc4.git2.1
- Linux v4.8-rc4-155-g86a1679

* Tue Aug 30 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc4.git1.1
- Linux v4.8-rc4-119-ge4e98c4

* Mon Aug 29 2016 Laura Abbott <labbott@fedoraproject.org>
- Add event decoding fix (rhbz 1360688)

* Mon Aug 29 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- Reenable debugging options.
- Add SELinux OverlayFS support.

* Mon Aug 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc4.git0.1
- Disable debugging options.
- Linux v4.8-rc4

* Sun Aug 28 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM updates

* Thu Aug 25 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc3.git2.1
- Linux v4.8-rc3-39-g61c0457

* Wed Aug 24 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Config updates and fixes for ARMv7 platforms

* Wed Aug 24 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc3.git1.1
- Linux v4.8-rc3-26-gcad9d20
- Reenable debugging options.
- Fix keyboard input for some devices (rhbz 1366224)

* Tue Aug 23 2016 Laura Abbott <labbott@fedoraproject.org>
- Fix for inabiltiy to send zero sized UDP packets (rhbz 1365940)

* Tue Aug 23 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Qualcomm QDF2432 errata fix
- Move to upstream patches for ACPI SPCR (serial console)
- Adjust max CPUs on ARM platforms to reflect newer real world hardware

* Mon Aug 22 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc3.git0.1
- Linux v4.8-rc3
- Disable debugging options.

* Sat Aug 20 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add fix for RTC crash on ARMv7 am33xx devices

* Fri Aug 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc2.git4.1
- Linux v4.8-rc2-348-g6040e57

* Fri Aug 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc2.git3.1
- Linux v4.8-rc2-232-g3408fef

* Fri Aug 19 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor Tegra changes

* Wed Aug 17 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc2.git2.1
- Linux v4.8-rc2-42-g5ff132c
- CVE-2016-6828 tcp fix use after free in tcp_xmit_retransmit_queue (rhbz 1367091 1367092)

* Tue Aug 16 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc2.git1.1
- Linux v4.8-rc2-17-gae5d68b
- Add patch for qxl cursor bug (rhbz 1200901)
- Reenable debugging options.

* Mon Aug 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc2.git0.1
- Linux v4.8-rc2
- Disable debugging options.

* Fri Aug 12 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git5.1
- Linux v4.8-rc1-166-g9909170

* Thu Aug 11 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git4.1
- Linux v4.8-rc1-88-g3b3ce01

* Thu Aug 11 2016 Laura Abbott <labbott@fedoraproject.org>
- Fix for crash seen with open stack (rhbz 1361414)

* Thu Aug 11 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config updates
- Disable long running watchdog in VM patch (in theory fixed)
- Enable NUMA on aarch64
- Enable Cavium ThunderX
- Enable Atmel i2c TPM on ARM platforms

* Wed Aug 10 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git3.1
- Linux v4.8-rc1-70-g9512c47

* Wed Aug 10 2016 Laura Abbott <labbott@fedoraproject.org>
- Fix false positive VM_BUG() in page_add_file_rmap (rhbz 1365686)

* Wed Aug 10 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git2.1
- Linux v4.8-rc1-53-ga0cba21

* Tue Aug 09 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git1.1
- Linux v4.8-rc1-19-g81abf25
- Reenable debugging options.

* Mon Aug 08 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Build CONFIG_POWERNV_CPUFREQ in on ppc64* (rhbz 1351346)

* Mon Aug 08 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc1.git0.1
- Linux v4.8-rc1
- Disable debugging options.

* Fri Aug 05 2016 Laura Abbott <labbott@redhat.com> - 4.8.0-0.rc0.git7.1
- Linux v4.7-11891-gdd7fd3a

* Thu Aug 04 2016 Laura Abbott <labbott@redhat.com> - 4.8.0-0.rc0.git6.1
- Linux v4.7-11544-g96b5852

* Wed Aug 03 2016 Laura Abbott <labbott@redhat.com> - 4.8.0-0.rc0.git5.1
- Linux v4.7-11470-gd52bd54

* Tue Aug  2 2016 Hans de Goede <jwrdegoede@fedoraproject.org>
- Sync skylake hdaudio __unclaimed_reg WARN_ON fix with latest upstream version
- Drop drm-i915-skl-Add-support-for-the-SAGV-fix-underrun-hangs.patch for now

* Tue Aug 02 2016 Laura Abbott <labbott@redhat.com> - 4.8.0-0.rc0.git4.1
- Linux v4.7-10753-g731c7d3

* Fri Jul 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc0.git3.1
- Linux v4.7-6438-gc624c86

* Fri Jul 29 2016 Bastien Nocera <bnocera@redhat.com>
- Add touchscreen and pen driver for the Surface 3
- Add CrystalCove PWM support, for CherryTrail devices

* Thu Jul 28 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.0-0.rc0.git2.1
- Linux v4.7-5906-g194dc87

* Thu Jul 28 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-5412 powerpc: kvm: Infinite loop in HV mode (rhbz 1349916 1361040)

* Thu Jul 28 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.8.0-0.rc0.git1.1
- Filter nvme rdma modules to extras
- Fix IP Wireless driver filtering (rhbz 1356043) thanks lkundrak
- Build IIO tools

* Wed Jul 27 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- Linux v4.7-3199-g0e06f5c
- Reenable debugging options.

* Tue Jul 26 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-2
- rebuild for koji errors

* Mon Jul 25 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-6136 race condition in auditsc.c (rhbz 1353533 1353534)

* Mon Jul 25 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-1
- Linux v4.7

* Tue Jul 19 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add aarch64 ACPI pci-e patches headed for 4.8

* Mon Jul 18 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc7.git4.1
- Linux v4.7-rc7-92-g47ef4ad

* Mon Jul 18 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- ARM config updates, update bcm238x patches

* Fri Jul 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.7.0-0.rc7.git3.1
- Linux v4.7-rc7-78-gfa3a9f574

* Thu Jul 14 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Fix various i915 uncore oopses (rhbz 1340218 1325020 1342722 1347681)

* Wed Jul 13 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.7.0-0.rc7.git2.1
- Linux v4.7-rc7-27-gf97d104

* Tue Jul 12 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.7.0-0.rc7.git1.1
- Linux v4.7-rc7-6-g63bab22
- Reenable debugging options.

* Tue Jul 12 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-5389 CVE-2016-5696 tcp challenge ack info leak (rhbz 1354708 1355615)

* Mon Jul 11 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.7.0-0.rc7.git0.1
- Disable debugging options.
- linux v4.7-rc7

* Fri Jul 08 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc6.git2.2
- Workaround for glibc change

* Fri Jul 08 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc6.git2.1
- Linux v4.7-rc6-94-gcc23c61

* Thu Jul 07 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc6.git1.1
- Linux v4.7-rc6-74-g076501f
- Reenable debugging options.

* Thu Jul 07 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Fix oops in qla2xxx driver (rhbz 1346753)
- Fix blank screen on some nvidia cards (rbhz 1351205)

* Thu Jul  7 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Marvell mvebu for aarch64

* Tue Jul 05 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc6.git0.1
- Linux v4.7-rc6
- Disable debugging options.

* Fri Jul 01 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc5.git3.1
- Linux v4.7-rc5-254-g1a0a02d

* Thu Jun 30 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc5.git2.1
- Linux v4.7-rc5-227-ge7bdea7
- Reenable debugging options.

* Tue Jun 28 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc5.git1.1
- Linux v4.7-rc5-28-g02184c6

* Mon Jun 27 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc5.git0.1
- Linux v4.7-rc5
- Disable debugging options.

* Fri Jun 24 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc4.git3.1
- Linux v4.7-rc4-76-g63c04ee

* Thu Jun 23 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc4.git2.1
- Linux v4.7-rc4-20-gf9020d1

* Wed Jun 22 2016 Hans de Goede <jwrdegoede@fedoraproject.org>
- Bring in patch-series from drm-next to fix skl_update_other_pipe_wm issues
  (rhbz 1305038)
- Disable fbc on haswell by default (fdo#96461)

* Tue Jun 21 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc4.git1.1
- Linux v4.7-rc4-14-g67016f6
- Reenable debugging options.

* Mon Jun 20 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc4.git0.1
- Linux v4.7-rc4
- Disable debugging options.

* Fri Jun 17 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc3.git3.1
- Linux v4.7-rc3-87-gbb96727
- enable CONFIG_PWM (rhbz 1347454)

* Thu Jun 16 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc3.git2.1
- Linux v4.7-rc3-55-gd325ea8

* Wed Jun 15 2016 Laura Abbott <labbott@fedoraproject.org>
- hp-wmi: fix wifi cannot be hard-unblock (rhbz 1338025)

* Wed Jun 15 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-4470 keys: uninitialized variable crash (rhbz 1341716 1346626)

* Wed Jun 15 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable support for TI dm81xx devices (kwizart)

* Tue Jun 14 2016 Laura Abbott <labbott@redhat.com>
- ath9k: fix GPIO mask for AR9462 and AR9565 (rhbz 1346145)

* Tue Jun 14 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc3.git1.1
- Linux v4.7-rc3-9-gdb06d75
- Reenable debugging options.

* Tue Jun 14 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Infiniband on ARM now we have HW

* Mon Jun 13 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc3.git0.1
- Linux v4.7-rc3
- Disable debugging options.

* Fri Jun 10 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.7.0-0.rc2.git3.2
- Fix Power64 module filters
- Minor ARM updates

* Fri Jun 10 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc2.git3.1
- Linux v4.7-rc2-64-g147d9e7

* Thu Jun  9 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable ARM big.LITTLE on ARMv7 LPAE kernels

* Wed Jun 08 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc2.git2.1
- Linux v4.7-rc2-20-gc8ae067

* Wed Jun  8 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM/aarch64 config updates

* Tue Jun 07 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc2.git1.1
- Linux v4.7-rc2-4-g3613a62

* Tue Jun 07 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-5244 info leak in rds (rhbz 1343338 1343337)
- CVE-2016-5243 info leak in tipc (rhbz 1343338 1343335)

* Mon Jun 06 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc2.git0.1
- Linux v4.7-rc2
- Disable debugging options.

* Fri Jun 03 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git4.1
- Linux v4.7-rc1-122-g4340fa5

* Thu Jun 02 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git3.1
- Linux v4.7-rc1-104-g719af93

* Wed Jun 01 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git2.2
- Add filtering for i686 as well

* Wed Jun 01 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git2.1
- Linux v4.7-rc1-94-g6b15d66
- Reenable debugging options.

* Tue May 31 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git1.2
- Update module filters

* Tue May 31 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc1.git1.1
- Linux v4.7-rc1-12-g852f42a
- Disable debugging options.

* Mon May 30 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Update Utilite patch
- Minor ARM cleanups
- Initial Qualcomm ARM64 support (Dragonboard 410c)

* Fri May 27 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git10.1
- Linux v4.6-11010-gdc03c0f
- Kconfig, Kbuild, ceph, nfs, xfs, mmc, hwmon merges

* Thu May 26 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git9.1
- Linux v4.6-10675-g2f7c3a1
- EFI, sched, perf, objtool, acpi, pm, drm merges

* Wed May 25 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git8.1
- Linux v4.6-10530-g28165ec
- ARM SoC, asm-generic, nfsd, ext4, spi, mtd, xen, merges

* Tue May 24 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.7.0-0.rc0.git7.1
- Linux v4.6-10203-g84787c572d40
- Enable CONFIG_MEMORY_HOTPLUG_DEFAULT_ONLINE (rhbz 1339281)
- Fixup SB patchset to work with upstream changes

* Mon May 23 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git6.1
- Linux v4.6-8907-g7639dad
- trace, f2fs, btrfs, rtc, mailbox, akpm, staging, driver core, char, usb,
  tty, clk, net, devicetree, rdma, mfd, iio, powerpc, arm merges

* Fri May 20 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git5.1
- Linux v4.6-6148-g03b979d
- Docs, i2c, md, iommu, sound, pci, pinctrl, dmaengine, kvm, security merges

* Fri May 20 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-4440 kvm: incorrect state leading to APIC register access (rhbz 1337806 1337807)

* Fri May 20 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM cleanups, enable Tegra USB-3 controller

* Thu May 19 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git4.1
- Linux v4.6-5028-g2600a46
- trace, audit, input, media, scsi, armsoc merges

* Wed May 18 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git3.1
- Linux v4.6-3623-g0b7962a
- ata, regulator, gpio, HID, livepatching, networking, dm, block, vfs, fs,
  timers, crypto merges

* Tue May 17 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git2.2
- Adjust solib for cpupower

* Tue May 17 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git2.1
- Linux v4.6-1278-g1649098
- Enable CONFIG_INTEL_POWERCLAMP
- pm, ACPI, mmc, regulator, i2c, hwmon, edac, led, arm64, x86, sched, RAS merges

* Mon May 16 2016 Laura Abbott <labbott@redhat.com> - 4.7.0-0.rc0.git1.1
- Linux v4.6-153-g3469d26
- Reenable debugging options.
- locking, efi, signals, rcu merges

* Mon May 16 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- Disable CONFIG_DEBUG_VM_PGFLAGS on non debug kernels (rhbz 1335173)

* Mon May 16 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-1
- Linux v4.6
- CVE-2016-3713 kvm: out-of-bounds access in set_var_mtrr_msr (rhbz 1332139 1336410)

* Fri May 13 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc7.git3.1
- Linux v4.6-rc7-116-ga2ccb68b1e6a

* Thu May 12 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Some minor ARMv7 platform fixes from F-24
- Enable PCI_HOST_GENERIC for all ARM arches (Jeremy Linton)

* Wed May 11 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc7.git2.1
- Linux v4.6-rc7-55-gc5114626f33b

* Tue May 10 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc7.git1.1
- Linux v4.6-rc7-45-g2d0bd9534c8d

* Tue May 10 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Enable XEN SCSI front and backend (rhbz 1334512)
- CVE-2016-4569 info leak in sound module (rhbz 1334643 1334645)

* Mon May 09 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc7.git0.1
- Linux v4.6-rc7

* Fri May 06 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc6.git4.1
- Linux v4.6-rc6-165-g9caa7e78481f

* Thu May 05 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc6.git3.1
- Linux v4.6-rc6-123-g21a9703de304
- CVE-2016-4486 CVE-2016-4485 info leaks (rhbz 1333316 1333309 1333321)

* Wed May 04 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc6.git2.1
- Linux v4.6-rc6-113-g83858a701cf3
- Enable NFC_NXP_NCI options (rhbz 1290556)
- CVE-2016-4482 info leak in devio.c (rhbz 1332931 1332932)

* Tue May 03 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc6.git1.1
- Linux v4.6-rc6-72-g33656a1f2ee5

* Mon May 02 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc6.git0.1
- Linux v4.6-rc6
- Disable debugging options.

* Fri Apr 29 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc5.git3.1
- Linux v4.6-rc5-153-g92c19ea95357

* Thu Apr 28 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix KVM with THP corruption (rhbz 1331092)

* Thu Apr 28 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc5.git2.1
- Linux v4.6-rc5-89-gb75a2bf899b6

* Thu Apr 28 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix i.MX6 gpu module loading
- Add patch to fix Jetson TX1 usb

* Wed Apr 27 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc5.git1.1
- Linux v4.6-rc5-69-gf28f20da704d
- Require /usr/bin/kernel-install to fix installation after systemd package
  swizzling (rhbz 1331012)
- Reenable debugging options.

* Tue Apr 26 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Enable IEEE802154_AT86RF230 on more arches (rhbz 1330356)

* Mon Apr 25 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc5.git0.1
- Linux v4.6-rc5
- Disable debugging options.

* Fri Apr 22 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc4.git3.1
- Linux v4.6-rc4-124-g5f44abd041c5

* Thu Apr 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc4.git2.1
- Linux v4.6-rc4-17-g55f058e7574c

* Wed Apr 20 2016 Laura Abbott <labbott@fedoraproject.org>
- Allow antenna selection for rtl8723be (rhbz 1309487)

* Wed Apr 20 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc4.git1.1
- Linux v4.6-rc4-13-g9a0e3eea25d3
- Reenable debugging options.

* Tue Apr 19 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Enable XILLYBUS (rhbz 1328394)

* Mon Apr 18 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc4.git0.1
- Linux v4.6-rc4
- Disable debugging options.

* Fri Apr 15 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-3961 xen: hugetlbfs use may crash PV guests (rhbz 1327219 1323956)

* Fri Apr 15 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc3.git2.1
- Linux v4.6-rc3-99-g806fdcce017d

* Thu Apr 14 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Disable oprofile driver as userspace oprofile only uses perf (rhbz 1326944)

* Thu Apr 14 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc3.git1.1
- Linux v4.6-rc3-57-g90de6800c240
- Reenable debugging options.

* Mon Apr 11 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc3.git0.1
- Linux v4.6-rc3
- Disable debugging options.

* Sun Apr 10 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Use the correct MMC driver for some ARM platforms

* Fri Apr 08 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.6.0-0.rc2.git4.1
- Linux v4.6-rc2-151-g3c96888

* Thu Apr 07 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.6.0-0.rc2.git3.1
- Linux v4.6-rc2-88-gc4004b0

* Wed Apr 06 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.6.0-0.rc2.git2.1
- Linux v4.6-rc2-84-g541d8f4

* Tue Apr 05 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.6.0-0.rc2.git1.1
- Linux v4.6-rc2-42-g1e1e5ce
- Reenable debugging options.

* Mon Apr 04 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.6.0-0.rc2.git0.1
- Linux v4.6-rc2

* Sun Apr  3 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Some minor ARMv7/aarch64 cleanups

* Thu Mar 31 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add another patch for CVE-2016-2184

* Wed Mar 30 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Fix undefined __always_inline in exported headers (rhbz 1321749)
- Make sure to install objtool in -devel subpackage if it exists (rhbz 1321628)

* Wed Mar 30 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Add ARMv7 mvebu fixes headed upstream
- Minor ARMv7 cleanups
- Boot fix for aarch64 devices with 64K page size requirements (Seattle)

* Sun Mar 27 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc1.git0.1
- Linux v4.6-rc1
- Disable debugging options.

* Fri Mar 25 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git26.1
- Linux v4.5-12596-g11caf57f6a4b
- asm-generic, pm+acpi, rtc, hwmon, block, mtd, ubifs, nfsd, kbuild, parisc,
  h8, arm64, armsoc

* Thu Mar 24 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git25.1
- Linux v4.5-12330-ge46b4e2b46e1
- trace, thermal, nfsd merges

* Thu Mar 24 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git24.1
- Linux v4.5-12257-g8b97be054572
- staging, timers, perf, irq, x86, sched, locking merges

* Thu Mar 24 2016 jwboyer@gmail.com - 4.6.0-0.rc0.git23.1
- Linux v4.5-12149-gaca04ce
- net, pwm, target, platform-drivers merges

* Wed Mar 23 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git22.1
- Linux v4.5-12013-gc13042362033
- crypto, mailbox, clk merges

* Wed Mar 23 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git21.1
- Linux v4.5-11787-ga24e3d414e59
- akpm, kvm, rdma

* Wed Mar 23 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix Tegra Jetson TK1

* Tue Mar 22 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git20.1
- Linux v4.5-11312-g01cde1538e1d
- nfs, overlayfs, fuse, xen, i2c, target, pci, sound, iommu merges

* Tue Mar 22 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-3136 mct_u232: oops on invalid USB descriptors (rhbz 1317007 1317010)
- CVE-2016-2187 gtco: oops on invalid USB descriptors (rhbz 1317017 1317010)

* Tue Mar 22 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git19.1
- Linux v4.5-11118-g968f3e374faf
- btrfs, mmc, md merges

* Mon Mar 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git18.1
- Linux v4.5-10883-g770c4c1119db
- drm, arm64-perf, arc, udf, quota merges

* Mon Mar 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git17.1
- Linux v4.5-9714-g53d2e6976bd4
- xfs, f2fs, cgroup merges

* Mon Mar 21 2016 Laura Abbott <labbott@fedoraproject.org>
- uas: Limit qdepth at the scsi-host level (rhbz 1315013)
- Fix for performance regression caused by thermal (rhbz 1317190)
- Input: synaptics - handle spurious release of trackstick buttons, again (rhbz 1318079)

* Mon Mar 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git16.1
- Linux v4.5-9542-g643ad15d4741
- pekeys, efi, objtool merges

* Mon Mar 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git15.1
- Linux v4.5-9406-g46e595a17dcf
- xtensa, mailbox, vhost, all the armsoc merges

* Mon Mar 21 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor aarch64 cleanups

* Mon Mar 21 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git14.1
- Linux v4.5-8524-g1e75a9f34a5e
- watchdog, firewire, vfs, linux-arm, sh, powerpc, audit, device tree merges

* Sat Mar 19 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git13.1
- Linux v4.5-8194-g1200b6809dfd
- net merge

* Sat Mar 19 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git12.1
- Linux v4.5-6486-g6b5f04b6cf8e
- cgroup, libata, workqueue, block, akpm, usb merges

* Sat Mar 19 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM cleanups
- Drop ARM_PATCH_IDIV work around
- Update geekbox patch to v4
- Upstream fix for stmmac driver regressions (AllWinner Gb NICs)

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git11.1
- Linux v4.5-6229-gf7813ad5cbfd
- ipmi, mfd, sound merges

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Change requires to updated package names and correctly Requires findutils
  in -devel package (rhbz 1319131)

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git10.1
- Linux v4.5-5842-g9ea446352047
- staging, rdma merges

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git9.1
- Linux v4.5-4071-g10fdfee7f7fd
- input, livepatching, trivial, hid, gpio, m68knommu, arm64, selftest merges

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org>
- ims-pcu: sanity checking on missing interfaces
- CVE-2016-3140 digi_acceleport: oops on invalid USB descriptors (rhbz 1317010 1316995)
- CVE-2016-3138 cdc_acm: oops on invalid USB descriptors (rhbz 1317010 1316204)
- CVE-2016-2185 ati_remote2: oops on invalid USB descriptors (rhbz 1317014 1317471)
- CVE-2016-2188 iowarrior: oops on invalid USB descriptors (rhbz 1317018 1317467)
- CVE-2016-2186 powermate: oops on invalid USB descriptors (rhbz 1317015 1317464)
- CVE-2016-3137 cypress_m8: oops on invalid USB descriptors (rhbz 1317010 1316996)
- CVE-2016-2184 alsa: panic on invalid USB descriptors (rhbz 1317012 1317470)

* Fri Mar 18 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git8.1
- Linux v4.5-3654-g5cd0911a9e0e
- Fix oops from tsc subsystem (rhbz 1318596)
- crypto, security, docs, rproc, dmaengine, powersupply, hsi, vfio, driver-core,
  tty, char, usb, configfs, ext4, dlm, gfs2, pstore merges

* Thu Mar 17 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add temporary patch to fix intel_pstate oops and lockdep report on
  various atom based CPUs.

* Thu Mar 17 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git7.1
- Linux v4.5-2535-g09fd671ccb24
- fbdev, media, libnvdimm, dm, scsi, ibft merges

* Thu Mar 17 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git6.1
- Linux v4.5-1822-g63e30271b04c
- PCI, PM+ACPI merges

* Wed Mar 16 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git5.1
- Linux v4.5-1523-g271ecc5253e2
- akpm patches (mm subsystem, various)

* Wed Mar 16 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git4.1
- Linux v4.5-1402-gaa6865d83641
- s390, m68k, avr32, KVM, EDAC merges

* Wed Mar 16 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git3.1
- Linux v4.5-1127-g9256d5a308c9
- pinctrl, LED, rtc, hwmon, regulator, regmap, spi merges

* Wed Mar 16 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-3135 ipv4: DoS when destroying a network interface (rhbz 1318172 1318270)

* Wed Mar 16 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git2.1
- Linux v4.5-760-g710d60cbf1b3

* Tue Mar 15 2016 Josh Boyer <jwboyer@fedoraproject.org> - 4.6.0-0.rc0.git1.1
- Linux v4.5-481-ge23604edac2a
- Enable RANDOMIZE_BASE
- Reenable debugging options.

* Mon Mar 14 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-1
- Linux v4.5
- Disable debugging options.

* Mon Mar 14 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-3134 netfilter: missing bounds check in ipt_entry struct (rhbz 1317383 1317384)
- CVE-2016-3135 netfilter: size overflow in x_tables (rhbz 1317386 1317387)

* Fri Mar 11 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch for ICP DAS I-756xU devices (rhbz 1316136)

* Thu Mar 10 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc7.git3.1
- Linux v4.5-rc7-215-gf2c1242

* Wed Mar 09 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc7.git2.1
- Linux v4.5-rc7-159-g7f02bf6

* Tue Mar 08 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc7.git1.1
- Linux v4.5-rc7-116-ge2857b8
- Reenable debugging options.

* Tue Mar 08 2016 Thorsten Leemhuis <fedora@leemhuis.info>
- add signkernel macro to make signing kernel and signing modules
  independent from each other
- sign modules on all archs

* Mon Mar  7 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.5.0-0.rc7.git0.2
- Disble ARM_PATCH_IDIV as a work around to fix rhbz 1303147

* Mon Mar 07 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc7.git0.1
- Disable debugging options.
- Linux v4.5-rc7

* Sat Mar  5 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Updates and new SoCs for aarch64 and ARMv7
- Add aarch64 support for PINE64 and Geekbox devices
- Fix ethernet naming on Armada 38x devices
- Serial console fixes for Tegra

* Fri Mar 04 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc6.git3.1
- Linux v4.5-rc6-41-ge3c2ef4

* Thu Mar 03 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc6.git2.1
- Linux v4.5-rc6-18-gf983cd3

* Wed Mar 02 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc6.git1.1
- Linux v4.5-rc6-8-gf691b77
- Reenable debugging options.
- enable VIDEO_GO7007

* Mon Feb 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc6.git0.1
- Linux v4.5-rc6

* Mon Feb 29 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Enable DHT11 (rhbz 1312888)
- Fix erroneously installed .o files in python-perf subpackage (rhbz 1312102)

* Thu Feb 25 2016 Laura Abbott <labbott@fedoraproject.org>
- Re-enable ZONE_DMA (rhbz 1309658)

* Thu Feb 25 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.5.0-0.rc5.git0.2
- Fix tegra nouveau module load (thank kwizart for reference)
- PowerPC Little Endian ToC fix

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
