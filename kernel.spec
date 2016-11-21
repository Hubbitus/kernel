# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

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

%define buildid .pf6.hu.1

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
%global baserelease 301
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 8

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
#+Hu Pf against 4.8.6 v4.8-pf6: https://pf.natalenko.name/news/?p=217
%define stable_update 6
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
%define rcrev 0
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
#URL: http://www.kernel.org/
# Hubbitus patched fork of Fedora Kernel. Post-factum (https://pf.natalenko.name/) branch.
# Binaries could be found at: http://hubbitus.info/wiki/Repository
URL: https://github.com/Hubbitus/kernel/
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

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v4.x/linux-%{kversion}.tar.xz

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

Source50: config-powerpc64-generic
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
#*Hu %%define    stable_patch_00  patch-4.%%{base_sublevel}.%%{stable_base}.xz
%global stable_patch_00 https://pf.natalenko.name/sources/4.8/patch-4.8-pf6.xz
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

# build tweak for build ID magic, even for -vanilla
Source5005: kbuild-AFTER_LINK.patch

%if !%{nopatches}

# Git trees.

# Standalone patches

# http://www.spinics.net/lists/arm-kernel/msg523359.html
Patch420: arm64-ACPI-parse-SPCR-table.patch

# a tempory patch for QCOM hardware enablement. Will be gone by end of 2016/F-26 GA
Patch421: qcom-QDF2432-tmp-errata.patch

# http://www.spinics.net/lists/arm-kernel/msg490981.html
Patch422: geekbox-v4-device-tree-support.patch

# http://www.spinics.net/lists/linux-pci/msg53991.html
# https://patchwork.kernel.org/patch/9337113/
Patch425: arm64-pcie-quirks.patch

# http://www.spinics.net/lists/linux-tegra/msg26029.html
Patch426: usb-phy-tegra-Add-38.4MHz-clock-table-entry.patch

# Fix OMAP4 (pandaboard)
Patch427: arm-revert-mmc-omap_hsmmc-Use-dma_request_chan-for-reque.patch
Patch428: ARM-OMAP4-Fix-crashes.patch

# Not particularly happy we don't yet have a proper upstream resolution this is the right direction
# https://www.spinics.net/lists/arm-kernel/msg535191.html
Patch429: arm64-mm-Fix-memmap-to-be-initialized-for-the-entire-section.patch

# http://patchwork.ozlabs.org/patch/587554/
Patch430: ARM-tegra-usb-no-reset.patch

Patch431: bcm2837-initial-support.patch

Patch432: bcm283x-vc4-fixes.patch

Patch433: AllWinner-net-emac.patch

Patch460: lib-cpumask-Make-CPUMASK_OFFSTACK-usable-without-deb.patch

Patch466: input-kill-stupid-messages.patch

Patch467: die-floppy-die.patch

Patch468: no-pcspkr-modalias.patch

Patch470: silence-fbcon-logo.patch

Patch471: Kbuild-Add-an-option-to-enable-GCC-VTA.patch

Patch472: crash-driver.patch

Patch473: Add-secure_modules-call.patch

Patch474: PCI-Lock-down-BAR-access-when-module-security-is-ena.patch

Patch475: x86-Lock-down-IO-port-access-when-module-security-is.patch

Patch476: ACPI-Limit-access-to-custom_method.patch

Patch477: asus-wmi-Restrict-debugfs-interface-when-module-load.patch

Patch478: Restrict-dev-mem-and-dev-kmem-when-module-loading-is.patch

Patch479: acpi-Ignore-acpi_rsdp-kernel-parameter-when-module-l.patch

Patch480: kexec-Disable-at-runtime-if-the-kernel-enforces-modu.patch

Patch481: x86-Restrict-MSR-access-when-module-loading-is-restr.patch

Patch482: Add-option-to-automatically-enforce-module-signature.patch

Patch483: efi-Disable-secure-boot-if-shim-is-in-insecure-mode.patch

Patch485: efi-Add-EFI_SECURE_BOOT-bit.patch

Patch486: hibernate-Disable-in-a-signed-modules-environment.patch

Patch487: Add-EFI-signature-data-types.patch

Patch488: Add-an-EFI-signature-blob-parser-and-key-loader.patch

# This doesn't apply. It seems like it could be replaced by
# https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5ac7eace2d00eab5ae0e9fdee63e38aee6001f7c
# which has an explicit line about blacklisting
Patch489: KEYS-Add-a-system-blacklist-keyring.patch

Patch490: MODSIGN-Import-certificates-from-UEFI-Secure-Boot.patch

Patch491: MODSIGN-Support-not-importing-certs-from-db.patch

Patch492: Add-sysrq-option-to-disable-secure-boot-mode.patch

Patch493: drm-i915-hush-check-crtc-state.patch

Patch494: disable-i8042-check-on-apple-mac.patch

Patch495: lis3-improve-handling-of-null-rate.patch

# In theory this has been fixed so should no longer be needed, it also causes problems with aarch64 DMI, so disable to see for sure if it's fixed
# Patch496: watchdog-Disable-watchdog-on-virtual-machines.patch

Patch497: scsi-sd_revalidate_disk-prevent-NULL-ptr-deref.patch

Patch498: criu-no-expert.patch

Patch499: ath9k-rx-dma-stop-check.patch

Patch500: xen-pciback-Don-t-disable-PCI_COMMAND-on-PCI-device-.patch

Patch501: Input-synaptics-pin-3-touches-when-the-firmware-repo.patch

Patch502: firmware-Drop-WARN-from-usermodehelper_read_trylock-.patch

# Patch503: drm-i915-turn-off-wc-mmaps.patch

Patch508: kexec-uefi-copy-secure_boot-flag-in-boot-params.patch

#CVE-2016-3134 rhbz 1317383 1317384
Patch665: netfilter-x_tables-deal-with-bogus-nextoffset-values.patch

#rhbz 1200901 (There should be something better upstream at some point)
Patch842: qxl-reapply-cursor-after-SetCrtc-calls.patch

# From kernel list, currently in linux-next
Patch845: HID-microsoft-Add-Surface-4-type-cover-pro-4-JP.patch

# SELinux OverlayFS support (queued for 4.9)
Patch846: security-selinux-overlayfs-support.patch

#rhbz 1360688
Patch847: rc-core-fix-repeat-events.patch

#rhbz 1374212
Patch848: 0001-cpupower-Correct-return-type-of-cpu_power_is_cpu_onl.patch

#ongoing complaint, full discussion delayed until ksummit/plumbers
Patch849: 0001-iio-Use-event-header-from-kernel-tree.patch

# CVE-2016-9083 CVE-2016-9084 rhbz 1389258 1389259 1389285
Patch850: v3-vfio-pci-Fix-integer-overflows-bitmask-check.patch

#rhbz 1325354
Patch852: 0001-HID-input-ignore-System-Control-application-usages-i.patch

#rhbz 1391279
Patch853: 0001-dm-raid-fix-compat_features-validation.patch

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
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|.*%%{_bindir}/tmon(\.debug)?|.*%%{_bindir}/iio_event_monitor(\.debug)?|.*%%{_bindir}/iio_generic_buffer(\.debug)?|.*%%{_bindir}/lsiio(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

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
Provides: kernel-devel = %{version}-%{release}%{?1:+%{1}}\
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
#Hu basename to allow use URLs in patches
  local patch=$( basename $1 )
  local patchURL=$1
  shift
  if [ ! -f $RPM_SOURCE_DIR/$patch ]; then
    exit 1
  fi
  if ! grep -E "^Patch[0-9]+: $patchURL\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-4." ] ; then
      echo "ERROR: Patch [$patch] not listed as a source patch in specfile"
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

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    xzcat %{SOURCE5000} | patch -p1 -F1 -s
%if 0%{?gitrev}
    xzcat %{SOURCE5001} | patch -p1 -F1 -s
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    xzcat %{SOURCE5000} | patch -p1 -F1 -s
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
#+Hu: Place for manual hotfixes!
#patch -p1 < %%{SOURCE5002}
git commit -a -m "Stable update"
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

# The kbuild-AFTER_LINK patch is needed regardless so we list it as a Source
# file and apply it separately from the rest.
git am %{SOURCE5005}

%if !%{nopatches}

git am %{patches}

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir -p configs

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

%define make make %{?cross_opts}

# now run oldconfig over all the config files
for i in %{all_arch_configs}
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
  make -s EXTRA_CFLAGS="${RPM_OPT_FLAGS}" LDFLAGS="%{__global_ldflags}" %{?cross_opts} %{?_smp_mflags} -C tools/perf V=1 NO_PERF_READ_VDSO32=1 NO_PERF_READ_VDSOX32=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_STRLCPY=1 NO_BIONIC=1 prefix=%{_prefix}
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
#-Hu1 pushd tools/iio/
#-Hu1 %{make}
#-Hu1 popd
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
#-Hu1 pushd tools/iio
#-Hu1 make INSTALL_ROOT=%{buildroot} install
#-Hu1 popd
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
#-Hu1 %{_bindir}/iio_event_monitor
#-Hu1 %{_bindir}/iio_generic_buffer
#-Hu1 %{_bindir}/lsiio
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
* Wed Nov 09 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.6-301.pf6.hu.1
- Rebase Fedora changes - kernel 4.8.6.
- Update pf patch to v4.8-pf6 - https://pf.natalenko.name/news/?p=217

* Wed Nov  2 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.6-301
- dm raid: fix compat_features validation (rhbz 1391279)

* Tue Nov  1 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.8.6-300
- Linux v4.8.6
- Add revert to fix omap4 mmc (panda)
- Other minor omap4 fixes
- Adjust config for some AllWinner devices that don't like modular bits
- Add patch for aarch64 memory regions

* Mon Oct 31 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.5-300.pf5.hu.3
- CONFIG_SCHED_MUQSS=y

* Mon Oct 31 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.5-300.pf5.hu.2
- Try build with CONFIG_SCHED_MUQSS=n by suggestipon of Oleksandr Natalenko in mail.

* Sun Oct 30 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.5-300.pf5.hu.1
- Kernel 4.8.5.
- Pull Fedora changes.
- Update pf patch to v4.8-pf5 https://pf.natalenko.name/news/?p=213.

* Sat Oct 29 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor VC4 bug fix

* Fri Oct 28 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.5-300
- Linux v4.8.5

* Thu Oct 27 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.4-301.pf4.hu.1
- Pull Fedora changes. Step to 4.8.4.
- Due to the error build on epel http://koji.fedoraproject.org/koji/getfile?taskID=16206974&name=build.log&offset=-4000 DISABLE build tools/iio!
- Upodate pf to 4.8-pf4 - https://pf.natalenko.name/news/?p=211.

* Thu Oct 27 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- CVE-2016-9083 CVE-2016-9084 vfio multiple flaws (rhbz 1389258 1389259 1389285)
- Skylake i915 fixes from 4.9
- Fix MS input devices identified as joysticks (rhbz 1325354)

* Mon Oct 24 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.8.4-301
- Upstream fix for Raspberry Pi to fix setting low-resolution video modes on HDMI
- A collection of other clock fixes in -next for the RPi

* Mon Oct 24 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.4-300
- Linux v4.8.4

* Sat Oct 22 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.2-300.pf2.hu.1
- Update to v4.8-pf2 - https://pf.natalenko.name/news/?p=207
    There BFS CPU scheduler has been replaced by its successor, MuQSS. Detailes: https://ck-hack.blogspot.de/2016/10/muqss-multiple-queue-skiplist-scheduler.html
- Change naming scheme to 4.8.0-300.pf2.hu.1 from 4.8.0-300.hu.1.pf2


* Thu Oct 20 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.3-300
- Linux v4.8.3
- CVE-2016-5195 (rhbz 1384344 1387080)

* Tue Oct 18 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix memory corruption caused by p8_ghash
- Make __xfs_xattr_put_listen preperly report errors (rhbz 1384606)

* Tue Oct 18 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable ACPI_CPPC_CPUFREQ on aarch64
- Add ethernet driver for AllWinner sun8i-emac (H3/OrangePi and Pine64)

* Mon Oct 17 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.2-300
- Linux v4.8.2
- i8042 - skip selftest on ASUS laptops

* Sat Oct 15 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Build in AXP20X_I2C (should fix rhbz 1352140)

* Tue Oct 11 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.8.0-1.hu.1.pf1
- Step to build kernels for Fedora 25.
- Use new pf patch v4.8-pf1 - https://pf.natalenko.name/news/?p=204

* Fri Oct 07 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- update baserelease for Fedora 25

* Fri Oct 07 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.8.1-1
- Linux v4.8.1

* Tue Oct 04 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix Xorg starting with virtio (rhbz 1366842)

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

#* Tue Sep 20 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.7.4-200.hu.2.pf4
#- Add patch1 http://ck.kolivas.org/patches/bfs/4.0/4.7/Pending/bfs497-build_other_arches.patch from Oleksand Natalenko

#* Mon Sep 19 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.7.4-200.hu.1.pf4
#- Merge Fedora upstream: kernel 4.7.4.
#- Update pf patch: 4.7-pf4 - https://pf.natalenko.name/news/?p=195

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

#* Tue Mar 08 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.4.4-301.hu.1.pf6
#- Merge Fedora changes.
#- Step to kernel 4.4.4.
#- Update pf patch: v4.4-pf6 - https://pf.natalenko.name/news/?p=161

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

#* Mon Feb 22 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.4.2-300.hu.1.pf5
#- Merge upstream changes. Step to 4.4.2!
#- Update pf patch to v4.4-pf5

* Sun Feb 21 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc5.git0.1
- Disable debugging options.
- Linux v4.5-rc5

* Fri Feb 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc4.git3.1
- Linux v4.5-rc4-137-g23300f6

* Thu Feb 18 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc4.git2.1
- Linux v4.5-rc4-95-g2850713

* Wed Feb 17 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc4.git1.1
- Linux v4.5-rc4-37-g65c23c6
- Reenable debugging options.

* Tue Feb 16 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor Aarch64 cleanups

* Mon Feb 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc4.git0.1
- Disable debugging options.
- Linux v4.5-rc4

* Fri Feb 12 2016 Laura Abbott <labbott@fedoraproject.org>
- Fix warning spew from vmware sockets (rhbz 1288684)

* Fri Feb 12 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc3.git3.1
- Linux v4.5-rc3-83-gc05235d

* Thu Feb 11 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc3.git2.1
- Linux v4.5-rc3-57-g721675f

* Tue Feb 09 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc3.git1.1
- Linux v4.5-rc3-19-g7cf91ad

* Tue Feb  9 2016 Laura Abbott <labbott@fedoraproject.org>
- Let 'make prepare' succeed with kernel-devel

* Tue Feb  9 2016 Peter Robinson <pbrobinson@fedoraproject.org> 4.5.0-0.rc3.git0.2
- Fix Power64 kernel build

* Mon Feb 08 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc3.git0.1
- Disable debugging options.
- Linux v4.5-rc3

* Fri Feb 05 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc2.git3.1
- Linux v4.5-rc2-212-gdf48ab3

* Wed Feb 03 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc2.git2.1
- Linux v4.5-rc2-192-gb37a05c

* Tue Feb 02 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc2.git1.1
- Linux v4.5-rc2-163-g34229b2
- Reenable debugging options.

* Mon Feb 01 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc1.git0.1
- Disable debugging options.
- Linux v4.5-rc2

* Fri Jan 29 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Backport HID sony patch to fix some gamepads (rhbz 1255235)

* Fri Jan 29 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc1.git2.1
- Linux v4.5-rc1-32-g26cd836

* Thu Jan 28 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix suprious NEWLINK netlink messages (rhbz 1302037)

* Thu Jan 28 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc1.git1.1
- Linux v4.5-rc1-28-g03c21cb
- Reenable debugging options.

* Wed Jan 27 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc1.git0.2
- Only apply KEY_FLAG_KEEP to a key if a parent keyring has it set (rhbz 1301099)

#* Tue Jan 26 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.3.3-303.hu.2.pf4
#- While Fedora step to 4.3.4, pf is still 4.3.4. But merging Fedora patch changes.

* Mon Jan 25 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc1.git0.1
- Disable debugging options.
- Linux v4.5-rc1

#* Sat Jan 23 2016 Pavel Alexeev <Pahan@Hubbitus.info> - 4.3.3-303.hu.1.pf4
#- Merge Fedora 15 patches.
#- 4.3.3-303.hu.1.pf4

* Fri Jan 22 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git9.1
- Linux v4.4-10454-g3e1e21c

* Fri Jan 22 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Fix backtrace from PNP conflict on Haswell-ULT (rhbz 1300955)

* Thu Jan 21 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git8.1
- Linux v4.4-10062-g30f0530

* Thu Jan 21 2016 Josh Boyer <jwboyer@fedoraproject.org>
- Fix incorrect country code issue on RTL8812AE devices (rhbz 1279653)

* Wed Jan 20 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git7.1
- Linux v4.4-8950-g2b4015e

* Wed Jan 20 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2016-0723 memory disclosure and crash in tty layer (rhbz 1296253 1300224)

* Tue Jan 19 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git6.1
- Linux v4.4-8855-ga200dcb
- CVE-2016-0728 Keys: reference leak in join_session_keyring (rhbz 1296623)

* Tue Jan 19 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix boot on TI am33xx/omap devices

* Mon Jan 18 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git5.1
- Linux v4.4-8606-g5807fca

* Sun Jan 17 2016 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor updates and cleanups to aarch64/ARMv7/PowerPC
- ARM: enable nvmem drivers
- Build usb gadget/OTG on aarch64

* Fri Jan 15 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git4.1
- Linux v4.4-5966-g7d1fc01

* Thu Jan 14 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git3.1
- Linux v4.4-5593-g7fdec82

* Wed Jan 13 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git2.1
- Linux v4.4-3408-g6799060

* Tue Jan 12 2016 Justin M. Forbes <jforbes@fedoraproject.org>
- drop i915 patch to turn off wc mmaps

* Tue Jan 12 2016 Justin M. Forbes <jforbes@fedoraproject.org> - 4.5.0-0.rc0.git1.1
- Linux v4.4-1175-g03891f9
- Reenable debugging options.

* Tue Jan 12 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-7566 usb: visor: Crash on invalid USB dev descriptors (rhbz 1296466 1297517)
- Fix backtrace from PNP conflict on Broadwell (rhbz 1083853)

* Mon Jan 11 2016 Laura Abbott <labbott@redhat.com> - 4.4.0-1
- Linux v4.4
- Disable debugging options.

* Fri Jan 08 2016 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc8.git3.1
- Linux v4.4-rc8-36-g02006f7a

* Thu Jan 07 2016 Laura Abbott <labbott@redhat.com>
- Fix unlocked gem warning (rhbz 1295646)

* Thu Jan 07 2016 Laura Abbott <labbott@redhat.com>
- Bring back patches for Lenovo Yoga touchpad (rhbz 1275718)

* Thu Jan 07 2016 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc8.git2.1
- Linux v4.4-rc8-26-gb06f3a1

* Thu Jan 07 2016 Josh Boyer <jwboyer@fedorparoject.org>
- Quiet i915 gen8 irq messages

* Wed Jan 06 2016 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc8.git1.1
- Linux v4.4-rc8-5-gee9a7d2
- Reenable debugging options.

* Tue Jan 05 2016 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-8709 ptrace: potential priv escalation with userns (rhbz 1295287 1295288)

* Tue Jan 05 2016 Laura Abbott <labbott@redhat.com>
- Drop patches for Lenovo Yoga Touchpad (rhbz 1275718)

* Mon Jan 04 2016 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc8.git0.1
- Linux v4.4-rc8
- Disable debugging options.

* Sun Dec 27 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7/aarch64/ppc/s390 config cleanups
- Enable rk3368 aarch64 platforms

* Wed Dec 23 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc6.git1.1
- Linux v4.4-rc6-23-g24bc3ea
- Reenable debugging options.

* Mon Dec 21 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc6.git0.1
- Linux v4.4-rc6
- Disable debugging options.

* Fri Dec 18 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc5.git3.1
- Linux v4.4-rc5-168-g73796d8

* Thu Dec 17 2015 Laura Abbott <labbott@redhat.com>
- Enable XEN_PVN support (rhbz 1211904)

* Thu Dec 17 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc5.git2.1
- Linux v4.4-rc5-25-ga5e90b1
- Reenable debugging options.

* Thu Dec 17 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-8569 info leak from getsockname (rhbz 1292045 1292047)

* Wed Dec 16 2015 Laura Abbott <labbott@redhat.com>
- Enable a set of RDMA drivers (rhbz 1291902)

* Wed Dec 16 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc5.git1.1
- Linux v4.4-rc5-18-gedb42dc

* Tue Dec 15 2015 Laura Abbott <labbott@fedoraproject.org>
- Add support for Yoga touch input (rhbz 1275718)

* Tue Dec 15 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-8543 ipv6: DoS via NULL pointer dereference (rhbz 1290475 1290477)

* Mon Dec 14 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc5.git0.1
- Linux v4.4-rc5
- Disable debugging options.

* Mon Dec 14 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-7550 Race between read and revoke keys (rhbz 1291197 1291198)

* Fri Dec 11 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc4.git4.1
- Linux v4.4-rc4-113-g0bd0f1e

* Thu Dec 10 2015 Laura Abbott <labbott@redhat.com>
- Ignore errors from scsi_dh_add_device (rhbz 1288687)

* Thu Dec 10 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc4.git3.1
- Linux v4.4-rc4-86-g6764e5e

* Thu Dec 10 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix rfkill issues on ideapad Y700-17ISK (rhbz 1286293)

* Wed Dec 09 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc4.git2.1
- Linux v4.4-rc4-48-gaa53685

* Tue Dec 08 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc4.git1.1
- Linux v4.4-rc4-16-g62ea1ec
- Reenable debugging options.

* Mon Dec 07 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc4.git0.1
- Linux v4.4-rc4
- Disable debugging options.

* Fri Dec 04 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc3.git4.1
- Linux v4.4-rc3-171-g071f5d1

* Thu Dec 03 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc3.git3.1
- Linux v4.4-rc3-24-g25364a9

* Thu Dec 03 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix palm rejection on certain touchpads (rhbz 1287819)

* Wed Dec 02 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc3.git2.1
- Linux v4.4-rc3-8-g6a24e72

* Tue Dec 01 2015 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_X86_INTEL_MPX (rhbz 1287279)

* Tue Dec 01 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-7515 aiptek: crash on invalid device descriptors (rhbz 1285326 1285331)
- CVE-2015-7833 usbvision: crash on invalid device descriptors (rhbz 1270158 1270160)

* Tue Dec 01 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc3.git1.1
- Linux v4.4-rc3-5-g2255702
- Reenable debugging options.

* Mon Nov 30 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc3.git0.1
- Linux v4.4-rc3
- Fix for cgroup use after free (rhbz 1282706)
- Disable debugging options.

* Wed Nov 25 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc2.git2.1
- Linux v4.4-rc2-44-g6ffeba9

* Tue Nov 24 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc2.git1.1
- Linux v4.4-rc2-3-ga293154
- Reenable debugging options.

* Mon Nov 23 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Update AMD xgbe driver for 4.4

* Mon Nov 23 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc2.git0.1
- Linux v4.4-rc2
- Disable debugging options.

* Sun Nov 22 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix sound issue on some ARM devices (tested on Arndale)

* Fri Nov 20 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc1.git3.1
- Linux v4.4-rc1-223-g86eaf54

* Thu Nov 19 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc1.git2.1
- Linux v4.4-rc1-118-g34258a3
- Reenable debugging options.

* Wed Nov 18 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc1.git1.1
- Linux v4.4-rc1-96-g7f151f1

* Mon Nov 16 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc1.git0.1
- Linux v4.4-rc1
- Disable debugging options.
- Add potential fix for set_features breakage in networking

* Fri Nov 13 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git9.1
- Linux v4.3-11742-gf6d07df

* Thu Nov 12 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git8.1
- Linux v4.3-11626-g5d50ac7
- Set CONFIG_SECTION_MISMATCH_WARN_ONLY since powerpc has mismatches

* Thu Nov 12 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-5327 x509 time validation

* Wed Nov 11 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git7.2
- Drop CONFIG_DRM_DW_HDMI_AHB_AUDIO for now

* Wed Nov 11 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git7.1
- Linux v4.3-11481-gc5a3788
- Actually drop CONFIG_DMADEVICES_VDEBUG

* Tue Nov 10 2015 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_CMA on x86_64 (rhbz 1278985)

* Tue Nov 10 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git6.1
- Linux v4.3-9393-gbd4f203

* Tue Nov 10 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix Yoga 900 rfkill switch issues (rhbz 1275490)
- Fix incorrect size calculations in megaraid with 64K pages (rhbz 1269300)
- CVE-2015-8104 kvm: DoS infinite loop in microcode DB exception (rhbz 1278496 1279691)
- CVE-2015-5307 kvm: DoS infinite loop in microcode AC exception (rhbz 1277172 1279688)

* Tue Nov 10 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Don't build Serial 8250 on ppc platforms (fix FBTFS)
- Enable some more common sensors on ARMv7

* Mon Nov 09 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git5.1
- Linux v4.3-9269-gce5c2d2

* Sun Nov  8 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7 updates

* Fri Nov 06 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git4.2
- Fix ARM dt compilation error

* Fri Nov 06 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git4.1
- Linux v4.3-7965-gd1e41ff

* Fri Nov  6 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable Exynos IOMMU as it crashes
- Minor ARMv7 update for battiery/charging

#* Sat Nov 07 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.2.5-300.hu.1.pf3
#- Update to Fedora23.
#- Merge fc23 branch.
#- Adjust hibernate-Disable-in-a-signed-modules-environment.patch.

#* Thu Nov 05 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.2.5-201.hu.1.pf3.fc22
#- Update to pf3 - v4.2-pf3: https://pf.natalenko.name/forum/index.php?topic=363.0
#- 4.2.5-201.hu.1.pf3

* Thu Nov 05 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git3.1
- Linux v4.3-6681-g8e483ed

* Wed Nov 04 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git2.1
- Linux v4.3-1107-g66ef349

* Wed Nov  4 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7 config updates

* Tue Nov 03 2015 Laura Abbott <labbott@redhat.com> - 4.4.0-0.rc0.git1.1
- Linux v4.3-272-g5062ecd
- Reenable debugging options.

* Tue Nov 03 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-7799 slip:crash when using PPP char dev driver (rhbz 1271134 1271135)

* Tue Nov  3 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Add patch to fix crash in omap_wdt (headed upstream)
- Build in ARM generic crypto optomisation modules
- Minor ARM updates

* Mon Nov 02 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-1
- Linux v4.3
- Disable debugging options.

* Fri Oct 30 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Drop kdbus

* Thu Oct 29 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-7099 RDS: race condition on unbound socket null deref (rhbz 1276437 1276438)

* Thu Oct 29 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Move iscsi_tcp and related modules to kernel-core (rhbz 1249424)

* Wed Oct 28 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc7.git2.1
- Linux v4.3-rc7-32-g8a28d67

* Wed Oct 28 2015 Laura Abbott <labbott@redhat.com>
- Disable CONFIG_DMADEVICES_VDEBUG

* Wed Oct 28 2015 Laura Abbott <labbott@redhat.com>
- Add new PCI ids for wireless, including Lenovo Yoga

* Tue Oct 27 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc7.git1.1
- Linux v4.3-rc7-19-g858e904
- Reenable debugging options.

* Mon Oct 26 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc7.git0.1
- Linux v4.3-rc7
- Disable debugging options.

* Fri Oct 23 2015 Laura Abbott <labbott@redhat.com>
- Enable CONFIG_FS_DAX (rhbz 1274844)

* Fri Oct 23 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc6.git3.1
- Linux v4.3-rc6-232-g0386729

* Thu Oct 22 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc6.git2.1
- Linux v4.3-rc6-117-g8a70dd2

* Tue Oct 20 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc6.git1.1
- Linux v4.3-rc6-108-gce1fad2
- Reenable debugging options.

* Mon Oct 19 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc6.git0.1
- Linux v4.3-rc6
- Disable debugging options.

* Mon Oct 19 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix crash in key garbage collector when using request_key (rhbz 1272172)

* Fri Oct 16 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc5.git2.1
- Linux v4.3-rc5-65-g69984b6

* Wed Oct 14 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc5.git1.1
- Linux v4.3-rc5-37-g5b5f145
- Reenable debugging options.

* Mon Oct 12 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc5.git0.1
- Linux v4.3-rc5
- Disable debugging options.

* Thu Oct 08 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc4.git3.1
- Linux v4.3-rc4-61-gc6fa8e6

* Wed Oct 07 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc4.git2.1
- Linux v4.3-rc4-46-g8ace60f

* Wed Oct 07 2015 Laura Abbott <labbott@fedoraproject.org>
- Disable hibernation for powerpc (rhbz 1267395)

* Wed Oct 07 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Increase the default number of runtime UARTS (rhbz 1264383)
- Enable X86_NUMACHIP

* Tue Oct 06 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc4.git1.1
- Linux v4.3-rc4-15-gf670268
- Reenable debugging options.

* Mon Oct 05 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc4.git0.1
- Linux v4.3-rc4
- Disable debugging options.

* Mon Oct 05 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix qxl locking issues (rhbz 1238803 1249850)

* Sun Oct  4 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Add support for BeagleBone Green

* Fri Oct 02 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git4.1
- Linux v4.3-rc3-145-g36f8daf

* Thu Oct 01 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git3.1
- Linux v4.3-rc3-65-gf97b870

* Wed Sep 30 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git2.2
- Reenable debugging options.

* Tue Sep 29 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git2.1
- Linux v4.3-rc3-42-g3225031

* Tue Sep 29 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Revert upstream guesture disabling patch on synaptics (rhbz 1262434)

* Mon Sep 28 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git1.1
- Linux v4.3-rc3-40-g097f70b
- Disable debugging options.

* Mon Sep 28 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc3.git0.1
- Linux v4.3-rc3

* Mon Sep 28 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARMv7 updates

* Thu Sep 24 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-5257 Null ptr deref in usb whiteheat driver (rhbz 1265607 1265612)

* Tue Sep 22 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc2.git1.1
- Linux v4.3-rc2-19-gbcee19f
- Reenable debugging options.

* Mon Sep 21 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc2.git0.2
- Linux v4.3-rc2
- Disable debugging options.

* Fri Sep 18 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc1.git4.1
- Linux v4.3-rc1-131-ga7d5c18

* Fri Sep 18 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix oops in 32-bit kernel on 64-bit AMD cpus (rhbz 1263762)

* Thu Sep 17 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc1.git3.1
- Linux v4.3-rc1-47-g7271484

* Wed Sep 16 2015 Laura Abbott <labbott@redhat.com> - 4.3.0-0.rc1.git2.1
- Linux v4.3-rc1-21-g865ca08

* Tue Sep 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc1.git1.1
- Linux v4.3-rc1-19-gd25ed277fbd4

* Mon Sep 14 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Reenable debugging options.

* Mon Sep 14 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc1.git0.1
- Linux v4.3-rc1
- Disable debugging options.

* Mon Sep 14 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- ARMv7 update for AllWinner devices

* Fri Sep 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git14.1
- Linux v4.2-11169-g64d1def7d338

* Fri Sep 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git13.1
- Linux v4.2-11142-gb0a1ea51bda4

* Fri Sep 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git12.1
- Linux v4.2-10963-g519f526d391b

#* Sun Sep 13 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.1.6-201.hu.1.pf4.fc22
#- Update pf to v4.1-pf4 - https://pf.natalenko.name/forum/index.php?topic=345.0
#- Possible kernel-3.19-bfs-compat-hubbitus.patch will not needed anymore (https://pf.natalenko.name/forum/index.php?topic=332.0).

* Wed Sep 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git11.1
- Linux v4.2-10774-g26d2177e977c

* Wed Sep 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git10.1
- Linux v4.2-10637-ga794b4f32921
- Rework secure boot patchset

* Tue Sep  8 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Config updates for ARMv7/aarch64

* Tue Sep 08 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git9.1
- Linux v4.2-9861-g4e4adb2f4628

* Tue Sep 08 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix oops in blk layer (rhbz 1237136)

* Sun Sep 06 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git8.1
- Linux v4.2-9700-g7d9071a09502

* Fri Sep 04 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix alternatives oops from Thomas Gleixner (rhbz 1258223)

* Fri Sep 04 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git7.1
- Linux v4.2-6663-g807249d3ada1

* Fri Sep 04 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Bump Requiers on linux-firmware for new amdgpu firmware requirements

* Thu Sep 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git6.1
- Linux v4.2-6105-gdd5cdb48edfd
- Networking merge

* Thu Sep 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git5.1
- Linux v4.2-4507-g1e1a4e8f4391

* Wed Sep 02 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git4.1
- Linux v4.2-4282-gae982073095a

* Wed Sep 02 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git3.1
- Linux v4.2-3986-g73b6fa8e49c2

* Tue Sep 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git2.1
- Linux v4.2-2890-g361f7d175734

* Tue Sep 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.3.0-0.rc0.git1.1
- Linux v4.2-2744-g65a99597f044
- Reenable debugging options.

* Mon Aug 31 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-1
- Linux v4.2

* Fri Aug 28 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc8.git3.1
- Linux v4.2-rc8-37-g4941b8f0c2b9

* Thu Aug 27 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix vmware driver issues from Thomas Hellström (rhbz 1227193)

* Thu Aug 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc8.git2.1
- Linux v4.2-rc8-10-gf9ed72dde34e
- Add patch from Hans de Goede to fix nv46 based cards (rhbz 1257534)
- Add patch from Jonathon Jongsma to fix modes in qxl (rhbz 1212201)

* Wed Aug 26 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc8.git1.1
- Linux v4.2-rc8-7-gf5db4b31b315
- Fixes x2apic panic (rhbz 1224764)
- Don't build perf-read-vdsox32 either
- Enable SCHEDSTATS and LATENCYTOP again (rhbz 1013225)

* Mon Aug 24 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Build in GPIO_OMAP to fix BeagleBone boot on mSD (changes in 4.2 upstream)

* Mon Aug 24 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc8.git0.1
- Linux v4.2-rc8

* Fri Aug 21 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Disable EFI_VARS (rhbz 1252137)

* Fri Aug 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc7.git4.1
- Linux v4.2-rc7-100-ge45fc85a2f37

* Fri Aug 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc7.git3.1
- Linux v4.2-rc7-71-g0bad90985d39

* Fri Aug 21 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor config updates for ARMv7

* Thu Aug 20 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix incorrect ext4 freezing behavior on non-journaled fs (rhbz 1250717)

* Wed Aug 19 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc7.git2.1
- Linux v4.2-rc7-24-g1b647a166f07

* Tue Aug 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc7.git1.1
- Linux v4.2-rc7-15-gbf6740281ed5

* Mon Aug 17 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix iscsi issue (rhbz 1253789)

* Mon Aug 17 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc7.git0.1
- Linux v4.2-rc7

* Sat Aug 15 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Patch from Hans de Goede to add yoga 3 rfkill quirk (rhbz 1239050)

* Fri Aug 14 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc6.git1.1
- Linux v4.2-rc6-130-g7ddab73346a1

* Tue Aug 11 2015 Peter Robinson <pbrobinson@fedoraproject.org> - 4.2.0-0.rc6.git0.2
- Drop UACCESS_WITH_MEMCPY on ARMv7 as it's broken (rhbz 1250613)

* Sun Aug 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc6.git0.1
- Linux v4.2-rc6

* Fri Aug 07 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc5.git3.1
- Linux v4.2-rc5-78-g49d7c6559bf2

* Wed Aug 05 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc5.git2.1
- Linux v4.2-rc5-42-g4e6b6ee253ce

* Tue Aug 04 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Patch from Nicholas Kudriavtsev for Acer Switch 12 Fn keys (rhbz 1244511)

* Tue Aug 04 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc5.git1.1
- Linux v4.2-rc5-19-gc2f3ba745d1c

* Tue Aug 04 2015 Hans de Goede <hdegoede@redhat.com>
- Always enable mmiotrace when building x86 kernels

* Tue Aug 04 2015 Hans de Goede <hdegoede@redhat.com>
- Move joydev.ko from kernel-modules-extra to kernel-modules

* Mon Aug 03 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix i386 boot bug correctly (rhbz 1247382)
- CVE-2015-5697 info leak in md driver (rhbz 1249011 1249013)

* Mon Aug 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc5.git0.1
- Linux v4.2-rc5
- Disable debugging options.

* Mon Aug 03 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Revert upstream commit 1c220c69ce to fix i686 booting (rhbz 1247382)

#* Sat Aug 01 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.1.2-200.hu.2.pf1
#- Merge Fedora changes, but stay at 4.1.2 as PF patch is.

* Fri Jul 31 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc4.git4.1
- Linux v4.2-rc4-111-g8400935737bf

* Thu Jul 30 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc4.git3.1
- Linux v4.2-rc4-87-g86ea07ca846a

* Thu Jul 30 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Disable CRYPTO_DEV_VMX_ENCRYPT on PPC for now to fix Power 8 boot (rhbz 1237089)

* Wed Jul 29 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc4.git2.1
- Linux v4.2-rc4-53-g956325bd55bb

* Wed Jul 29 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Drop acpi_brightness_enable revert patch

* Tue Jul 28 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc4.git1.1
- Linux v4.2-rc4-44-g67eb890e5e13
- Reenable debugging options.

* Mon Jul 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc4.git0.1
- Linux v4.2-rc4
- CVE-2015-1333 add_key memory leak (rhbz 1244171)
- Disable debugging options.

* Fri Jul 24 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc3.git4.1
- Linux v4.2-rc3-136-g45b4b782e848

* Thu Jul 23 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc3.git3.1
- Linux v4.2-rc3-115-gc5dfd654d0ec

* Wed Jul 22 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc3.git2.1
- Linux v4.2-rc3-17-gd725e66c06ab

* Tue Jul 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc3.git1.1
- Linux v4.2-rc3-4-g9d634c410b07
- Reenable debugging options.

* Tue Jul 21 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Fix stmmac eth driver (AllWinner, other ARM, and other devices)

* Mon Jul 20 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc3.git0.1
- Linux v4.2-rc3

#* Sat Jul 18 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.1.2-200.hu.1.pf1.fc22
#- Linux 4.1.2
#- Update PF patch to v4.1-pf1

* Fri Jul 17 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc2.git2.1
- Linux v4.2-rc2-190-g21bdb584af8c

* Fri Jul 17 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable DW MMC for generic ARM (hi6220 SoC support)

* Wed Jul 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc2.git1.1
- Linux v4.2-rc2-77-gf760b87f8f12

* Wed Jul 15 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Drop kdbus as it wasn't merged in time for f23

* Tue Jul 14 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Update AMD Seattle a0 eth driver for 4.2

* Mon Jul 13 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc2.git0.1
- Linux v4.2-rc2
- Disable debugging options.

* Fri Jul 10 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc1.git3.1
- Linux v4.2-rc1-62-gc4b5fd3fb205
- Build perf with NO_PERF_READ_VDSO32 on all arches

* Thu Jul 09 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Use git to apply patches

* Wed Jul 08 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc1.git2.1
- Linux v4.2-rc1-33-gd6ac4ffc61ac

* Tue Jul 07 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add kdbus

* Tue Jul 07 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc1.git1.1
- Linux v4.2-rc1-17-gc7e9ad7da219
- Reenable debugging options.

* Mon Jul 06 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc1.git0.1
- Linux v4.2-rc1
- Disable debug options.
- Add patch to fix perf build

* Thu Jul  2 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Move aarch64 relevant AMBA config options to arm-generic
- Minor ARMv7 updates

* Wed Jul 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc0.git4.1
- Linux v4.1-11549-g05a8256c586a

#* Tue Jun 30 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.0.5.hu.2.pf6.fc22
#- Pf still against 4.0.5 v4.0-pf6: https://pf.natalenko.name/forum/index.php?topic=324, so just ne build to incorporate upstream fedora patches.

* Tue Jun 30 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.2.0-0.rc0.git3.1
- Linux v4.1-11355-g6aaf0da8728c
- Add patch to fix KVM sleeping in atomic issue (rhbz 1237143)
- Fix errant with_perf disable that removed perf entirely (rhbz 1237266)

* Tue Jun 30 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor Aarch64 updates and cleanups
- Enable initial support for hi6220

* Mon Jun 29 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git2.1
- Linux v4.1-11235-gc63f887bdae8
- Reenable debugging options.

* Fri Jun 26 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Reorganisation and cleanup of the powerpc configs

* Thu Jun 25 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v4.1-5596-gaefbef10e3ae

* Mon Jun 22 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-1
- Linux v4.1

* Thu Jun 18 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix touchpad issues on Razer machines (rhbz 1227891)

* Tue Jun 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc8.git0.2
- Bump for rebuild to hopefully fix size issues due to elfutils bug

* Tue Jun 16 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Make some of the ARMv7 cpufreq drivers modular

* Mon Jun 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc8.git0.1
- Linux v4.1-rc8

#* Sun Jun 14 2015 Pavel Alexeev <Pahan@Hubbitus.info> - 4.0.4-303.hu.1.pf6.fc22
#- Upgrade to Fedora 22. Start f22-pf branch for kernels. First attempt build. Port changes from f21.
#- 4.0.4-303.hu.1.pf6

* Fri Jun 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc7.git1.1
- Linux v4.1-rc7-72-gdf5f4158415b

* Fri Jun 12 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2015-XXXX kvm: NULL ptr deref in kvm_apic_has_events (rhbz 1230770 1230774)

* Tue Jun 09 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix touchpad for Thinkpad S540 (rhbz 1223051)

* Mon Jun 08 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc7.git0.1
- Linux v4.1-rc7

* Thu Jun 04 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc6.git2.1
- Linux v4.1-rc6-49-g8a7deb362b76

* Thu Jun 04 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to turn of WC mmaps on i915 from airlied (rhbz 1226743)

* Wed Jun 03 2015 Laura Abbott <labbott@fedoraproject.org>
- Drop that blasted firwmare warning until we get a real fix (rhbz 1133378)

* Wed Jun 03 2015 Laura Abbott <labbott@fedoraproject.org>
- Fix auditing of canonical mode (rhbz 1188695)

* Wed Jun 03 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix from Ngo Than for perf build on ppc64le (rhbz 1227260)

* Wed Jun 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc6.git1.1
- Linux v4.1-rc6-44-g8cd9234c64c5

* Tue Jun 02 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix middle button issues on external Lenovo keyboards (rhbz 1225563)

* Mon Jun 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc6.git0.1
- Linux v4.1-rc6

* Thu May 28 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add quirk for Mac Pro backlight (rhbz 1217249)

* Mon May 25 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc5.git0.1
- Linux v4.1-rc5
- Disable debugging options.

* Thu May 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc4.git1.1
- Linux v4.1-rc4-11-g1113cdfe7d2c
- Reenable debugging options.
- Add patch to fix discard on md RAID0 (rhbz 1223332)

* Mon May 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc4.git0.1
- Linux v4.1-rc4
- Disable debugging options.

* Mon May 18 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix incorrect bandwidth on some Chicony webcams
- Fix DVB oops (rhbz 1220118)

* Mon May 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc3.git4.1
- Linux v4.1-rc3-346-gc0655fe9b090
- Enable in-kernel vmmouse driver (rhbz 1214474)

* Fri May 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc3.git3.1
- Linux v4.1-rc3-177-gf0897f4cc0fc

* Thu May 14 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix non-empty dir removal in overlayfs (rhbz 1220915)

* Wed May 13 2015 Laura Abbott <labbott@fedoraproject.org>
- Fix spew from KVM switch (rhbz 1219343)

* Wed May 13 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc3.git2.1
- Linux v4.1-rc3-165-g110bc76729d4

* Tue May 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc3.git1.1
- Linux v4.1-rc3-46-g4cfceaf0c087
- Reenable debugging options.

* Mon May 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc3.git0.1
- Linux v4.1-rc3
- Disable debugging options.
- Use kernel-install to create files in /boot partition (from Harald Hoyer)

* Mon May 11 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM update

* Thu May 07 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc2.git3.1
- Linux v4.1-rc2-79-g0e1dc4274828

* Wed May 06 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc2.git2.1
- Linux v4.1-rc2-37-g5198b44374ad

* Tue May 05 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc2.git1.1
- Linux v4.1-rc2-7-gd9cee5d4f66e
- Reenable debugging options.

* Tue May 05 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Backport patch to blacklist TRIM on all Samsung 8xx series SSDs (rhbz 1218662)

* Mon May 04 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc2.git0.1
- Linux v4.1-rc2
- Disable debugging options.

* Sun May  3 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable ACPI on aarch64
- General ARMv7 updates

* Fri May 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc1.git1.1
- Linux v4.1-rc1-117-g4a152c3913fb
- Reenable debugging options.

* Tue Apr 28 2015 Justin M. Forbes <jforbes@fedoraproject.org>
- Fix up boot times for live images (rhbz 1210857)

* Mon Apr 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc1.git0.1
- Linux v4.1-rc1
- Disable debugging options.

* Fri Apr 24 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git14.1
- Linux v4.0-10976-gd56a669ca59c

* Fri Apr 24 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix iscsi with QNAP devices (rhbz 1208999)

* Thu Apr 23 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git13.1
- Linux v4.0-10710-g27cf3a16b253

* Wed Apr 22 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Update AMD xgbe a0 aarch64 driver for 4.1

* Wed Apr 22 2015 Peter Robinson <pbrobinson@fedoraproject.org> - 4.1.0-0.rc0.git12.1
- Inital ARM updates for 4.1
- Temporarily disable AMD ARM64 xgbe-a0 driver

* Wed Apr 22 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v4.0-9804-gdb4fd9c5d072

* Tue Apr 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git11.1
- Linux v4.0-9362-g1fc149933fd4

* Tue Apr 21 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Enable ECHO driver (rhbz 749884)

* Mon Apr 20 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git10.1
- Linux v4.0-8962-g14aa02449064
- DRM merge

* Mon Apr 20 2015 Dennis Gilmore <dennis@ausil.us>
- enable mvebu for the LPAE kernel

* Mon Apr 20 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git9.1
- Linux v4.0-8158-g09d51602cf84

* Sat Apr 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git8.1
- Linux v4.0-7945-g7505256626b0

* Fri Apr 17 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git7.1
- Linux v4.0-7300-g4fc8adcfec3d
- Patch from Benjamin Tissoires to fix 3 finger tap on synaptics (rhbz 1212230)
- Add patch to support touchpad on Google Pixel 2 (rhbz 1209088)

* Fri Apr 17 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git6.1
- Linux v4.0-7209-g7d69cff26cea

* Thu Apr 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git5.1
- Linux v4.0-7084-g497a5df7bf6f

* Thu Apr 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git4.1
- Linux v4.0-6817-geea3a00264cf

* Wed Apr 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git3.1
- Linux v4.0-5833-g6c373ca89399

* Wed Apr 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git2.1
- Linux v4.0-3843-gbb0fd7ab0986

* Tue Apr 14 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.1.0-0.rc0.git1.1
- Linux v4.0-2620-gb79013b2449c
- Reenable debugging options.

* Sun Apr 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-1
- Linux v4.0

* Fri Apr 10 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc7.git2.1
- Linux v4.0-rc7-42-ge5e02de0665e

* Thu Apr 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc7.git1.1
- Linux v4.0-rc7-30-g20624d17963c

* Thu Apr 02 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc6.git2.1
- Linux v4.0-rc6-101-g0a4812798fae

* Thu Apr 02 2015 Josh Boyer <jwboyer@fedoraproject.org>
- DoS against IPv6 stacks due to improper handling of RA (rhbz 1203712 1208491)

* Wed Apr 01 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc6.git1.1
- Linux v4.0-rc6-31-gd4039314d0b1
- CVE-2015-2150 xen: NMIs triggerable by guests (rhbz 1196266 1200397)

* Tue Mar 31 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Enable MLX4_EN_VXLAN (rhbz 1207728)

* Mon Mar 30 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc6.git0.1
- Linux v4.0-rc6

* Fri Mar 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git4.1
- Linux v4.0-rc5-96-g3c435c1e472b
- Fixes hangs due to i915 issues (rhbz 1204050 1206056)

* Thu Mar 26 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git3.1
- Linux v4.0-rc5-80-g4c4fe4c24782

* Wed Mar 25 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Add aarch64 patches to fix mustang usb, seattle eth, and console settings

* Wed Mar 25 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git2.4
- Add patches to fix a few more i915 hangs/oopses

* Wed Mar 25 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git2.1
- Linux v4.0-rc5-53-gc875f421097a

* Tue Mar 24 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix ALPS v5 and v7 trackpads (rhbz 1203584)

* Tue Mar 24 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git1.3
- Linux v4.0-rc5-25-g90a5a895cc8b
- Add some i915 fixes

* Mon Mar 23 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc5.git0.3
- Enable CONFIG_SND_BEBOB (rhbz 1204342)
- Validate iovec range in sys_sendto/sys_recvfrom
- Revert i915 commit that causes boot hangs on at least some headless machines
- Linux v4.0-rc5

* Fri Mar 20 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc4.git2.1
- Linux v4.0-rc4-199-gb314acaccd7e
- Fix brightness on Lenovo Ideapad Z570 (rhbz 1187004)

* Thu Mar 19 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc4.git1.3
- Linux v4.0-rc4-88-g7b09ac704bac
- Rename arm64-xgbe-a0.patch

* Thu Mar 19 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Drop arm64 non upstream patch

* Thu Mar 19 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix high cpu usage on direct_read kernfs files (rhbz 1202362)

* Wed Mar 18 2015 Jarod Wilson <jwilson@fedoraproject.org>
- Fix kernel-uname-r Requires/Provides variant mismatches

* Tue Mar 17 2015 Kyle McMartin <kmcmarti@redhat.com> - 4.0.0-0.rc4.git0.3
- Update kernel-arm64.patch, move EDAC to arm-generic, add EDAC_XGENE on arm64.
- Add PCI_ECAM on generic, since it'll be selected most places anyway.

* Mon Mar 16 2015 Jarod Wilson <jwilson@fedoraproject.org>
- Fix bad variant usage in kernel dependencies

* Mon Mar 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc4.git0.1
- Linux v4.0-rc4
- Drop arm64 RCU revert patch.  Should be fixed properly upstream now.
- Disable debugging options.

* Sun Mar 15 2015 Jarod Wilson <jwilson@fedoraproject.org>
- Fix kernel-tools sub-packages for variant builds

* Fri Mar 13 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Fix esrt build on aarch64

* Fri Mar 13 2015 Kyle McMartin <kyle@fedoraproject.org>
- arm64-revert-tlb-rcu_table_free.patch: revert 5e5f6dc1 which
  causes lockups on arm64 machines.
- Also revert ESRT on AArch64 for now.

* Fri Mar 13 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc3.git2.1
- Linux v4.0-rc3-148-gc202baf017ae
- Add patch to support clickpads (rhbz 1201532)

* Thu Mar 12 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-8159 infiniband: uverbs: unprotected physical memory access (rhbz 1181166 1200950)

* Wed Mar 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc3.git1.1
- Linux v4.0-rc3-111-gaffb8172de39
- CVE-2015-2150 xen: NMIs triggerable by guests (rhbz 1196266 1200397)
- Patch series to fix Lenovo *40 and Carbon X1 touchpads (rhbz 1200777 1200778)
- Revert commit that added bad rpath to cpupower (rhbz 1199312)
- Reenable debugging options.

* Mon Mar 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc3.git0.1
- Linux v4.0-rc3
- Disable debugging options.

* Sun Mar  8 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- ARMv7: add patches to fix crash on boot for some devices on multiplatform

* Fri Mar 06 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc2.git2.1
- Linux v4.0-rc2-255-g5f237425f352

* Thu Mar 05 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc2.git1.1
- Linux v4.0-rc2-150-g6587457b4b3d
- Reenable debugging options.

* Wed Mar 04 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Enable MLX4_EN on ppc64/aarch64 (rhbz 1198719)

* Tue Mar 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc2.git0.1
- Linux v4.0-rc2
- Enable CONFIG_CM32181 for ALS on Carbon X1
- Disable debugging options.

* Tue Mar 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc1.git3.1
- Linux v4.0-rc1-178-g023a6007a08d

* Mon Mar 02 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix nfsd soft lockup (rhbz 1185519)
- Enable ET131X driver (rhbz 1197842)
- Enable YAMA (rhbz 1196825)

* Sat Feb 28 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- ARMv7 OMAP updates, fix panda boot

* Fri Feb 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc1.git2.1
- Linux v4.0-rc1-36-g4f671fe2f952

* Wed Feb 25 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add support for AR5B195 devices from Alexander Ploumistos (rhbz 1190947)

* Tue Feb 24 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc1.git1.1
- Linux v4.0-rc1-22-gb24e2bdde4af
- Reenable debugging options.

* Tue Feb 24 2015 Richard W.M. Jones <rjones@redhat.com> - 4.0.0-0.rc1.git0.2
- Add patch to fix aarch64 KVM bug with module loading (rhbz 1194366).

* Tue Feb 24 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor ARM config update

* Mon Feb 23 2015 Josh Boyer <jwboyer@fedoraproject.org> - 4.0.0-0.rc1.git0.1
- Add patch for HID i2c from Seth Forshee (rhbz 1188439)

* Mon Feb 23 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v4.0-rc1
- CVE-2015-0275 ext4: fallocate zero range page size > block size BUG (rhbz 1193907 1195178)
- Disable debugging options.

* Fri Feb 20 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git10.1
- Linux v3.19-8975-g3d883483dc0a
- Add patch to fix intermittent hangs in nouveau driver
- Move mtpspi and related mods to kernel-core for VMWare guests (rhbz 1194612)

* Wed Feb 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git9.1
- Linux v3.19-8784-gb2b89ebfc0f0

* Wed Feb 18 2015 Kyle McMartin <kyle@fedoraproject.org> - 3.20.0-0.rc0.git8.2
- kernel-arm64.patch: Revert dropping some of the xgene fixes we carried
  against upstream. (#1193875)
- kernel-arm64-fix-psci-when-pg.patch: make it simpler.
- config-arm64: turn on CONFIG_DEBUG_SECTION_MISMATCH.

* Wed Feb 18 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git8.1
- Linux v3.19-8217-gcc4f9c2a91b7

* Tue Feb 17 2015 Kyle McMartin <kyle@fedoraproject.org> - 3.20.0-0.rc0.git7.3
- kernel-arm64.patch turned on.

* Tue Feb 17 2015 Kyle McMartin <kyle@fedoraproject.org> - 3.20.0-0.rc0.git7.2
- kernel-arm64.patch merge, but leave it off.
- kernel-arm64-fix-psci-when-pg.patch: when -pg (because of ftrace) is enabled
  we must explicitly annotate which registers should be assigned, otherwise
  gcc will do unexpected things behind our backs.

* Tue Feb 17 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git7.1
- Linux v3.19-7478-g796e1c55717e
- DRM merge

* Mon Feb 16 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-XXXX-XXXX potential memory corruption in vhost/scsi driver (rhbz 1189864 1192079)
- CVE-2015-1593 stack ASLR integer overflow (rhbz 1192519 1192520)

* Mon Feb 16 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Minor updates for ARMv7/ARM64

* Mon Feb 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git6.1
- Linux v3.19-6676-g1fa185ebcbce

* Fri Feb 13 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git5.1
- Linux v3.19-5015-gc7d7b9867155

* Thu Feb 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git4.1
- Linux v3.19-4542-g8cc748aa76c9

* Thu Feb 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git3.1
- Linux v3.19-4020-gce01e871a1d4

* Wed Feb 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git2.1
- Linux v3.19-2595-gc5ce28df0e7c

* Wed Feb 11 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.20.0-0.rc0.git1.1
- Linux v3.19-463-g3e8c04eb1174
- Reenable debugging options.
- Temporarily disable aarch64 patches

* Mon Feb 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-1
- Linux v3.19

* Sat Feb 07 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc7.git3.1
- Linux v3.19-rc7-189-g26cdd1f76a88

* Thu Feb  5 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Allwinner A23 (sun8i) SoC
- Move ARM usb platform options to arm-generic

* Thu Feb 05 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc7.git2.1
- Linux v3.19-rc7-32-g5ee0e962603e

* Wed Feb 04 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc7.git1.1
- Linux v3.19-rc7-22-gdc6d6844111d

* Tue Feb 03 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc7.git0.3
- Add patch to fix NFS backtrace (rhbz 1188638)

* Mon Feb 02 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc7.git0.1
- Linux v3.19-rc7
- Disable debugging options.

* Fri Jan 30 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc6.git3.1
- Linux v3.19-rc6-142-g1c999c47a9f1

* Thu Jan 29 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Backport patch from Rob Clark to toggle i915 state machine checks

* Thu Jan 29 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- More ARMv7 updates
- A few more sound config cleanups

* Wed Jan 28 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc6.git2.1
- Linux v3.19-rc6-105-gc59c961ca511

* Tue Jan 27 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Enable SND_SOC and the button array driver on x86 for Baytrail devices

* Tue Jan 27 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc6.git1.1
- Linux v3.19-rc6-21-g4adca1cbc4ce
- Reenable debugging options.

* Mon Jan 26 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc6.git0.1
- Linux v3.19-rc6
- Remove symbolic link hunk from patch-3.19-rc6 (rbhz 1185928)
- Disable debugging options.

* Thu Jan 22 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc5.git2.1
- Linux v3.19-rc5-134-gf8de05ca38b7

* Wed Jan 21 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc5.git1.1
- Linux v3.19-rc5-117-g5eb11d6b3f55
- Reenable debugging options.

* Tue Jan 20 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- More ARM config option cleanups

* Mon Jan 19 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc5.git0.1
- Linux v3.19-rc5
- Disable debugging options.

* Sat Jan 17 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Move Rockchip to ARMv7 generic to support rk32xx on LPAE
- Enable Device Tree Overlays for dynamic DTB
- ARM config updates

* Fri Jan 16 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc4.git4.1
- Linux v3.19-rc4-155-gcb59670870d9

* Thu Jan 15 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Re-enable BUILD_DOCSRC

* Thu Jan 15 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc4.git3.1
- Linux v3.19-rc4-141-gf800c25b7a76

* Wed Jan 14 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc4.git2.1
- Linux v3.19-rc4-46-g188c901941ef
- Enable I40E_VXLAN (rhbz 1182116)

* Tue Jan 13 2015 Peter Robinson <pbrobinson@fedoraproject.org>
- Enable Checkpoint/Restore on ARMv7 (rhbz 1146995)

* Tue Jan 13 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Add installonlypkg(kernel) to kernel-devel subpackages (rhbz 1079906)

* Tue Jan 13 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc4.git1.1
- Linux v3.19-rc4-23-g971780b70194
- Reenable debugging options.

* Mon Jan 12 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc4.git0.1
- Linux v3.19-rc4
- Disable debugging options.

* Mon Jan 12 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Backlight fixes for Samsung and Dell machines (rhbz 1094948 1115713)
- Add various UAS quirks (rhbz 1124119)
- Add patch to fix loop in VDSO (rhbz 1178975)

* Fri Jan 09 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc3.git2.1
- Linux v3.19-rc3-69-g11c8f01b423b

* Wed Jan 07 2015 Kyle McMartin <kyle@fedoraproject.org> - 3.19.0-0.rc3.git1.2
- kernel-arm64.patch: fix up build... no idea if it works.

* Wed Jan 07 2015 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-9529 memory corruption or panic during key gc (rhbz 1179813 1179853)

* Wed Jan 07 2015 Josh Boyer <jwboyer@fedoraproject.org> - 3.19.0-0.rc3.git1.1
- Linux v3.19-rc3-38-gbdec41963890
- Enable POWERCAP and INTEL_RAPL options
- Reenable debugging options.

* Tue Jan 06 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.19-rc3

* Mon Jan 05 2015 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.19-rc2
- Temporarily disable aarch64patches
- Happy New Year

* Sun Dec 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable F2FS (rhbz 972446)

* Thu Dec 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.1-2
- CVE-2014-8989 userns can bypass group restrictions (rhbz 1170684 1170688)
- Fix from Kyle McMartin for target_core_user uapi issue since it's enabled
- Fix dm-cache crash (rhbz 1168434)
- Fix blk-mq crash on CPU hotplug (rhbz 1175261)

* Wed Dec 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.1-1
- Linux v3.18.1
- CVE-2014-XXXX isofs: infinite loop in CE record entries (rhbz 1175235 1175250)
- Enable TCM_USER (rhbz 1174986)
- Enable USBIP in modules-extra from Johnathan Dieter (rhbz 1169478)

* Tue Dec 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-2
- Add patch from Josh Stone to restore var-tracking via Kconfig (rhbz 1126580)

* Mon Dec 15 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix ppc64 boot with smt-enabled=off (rhbz 1173806)
- CVE-2014-8133 x86: espfix(64) bypass via set_thread_area and CLONE_SETTLS (rhbz 1172797 1174374)
- CVE-2014-8559 deadlock due to incorrect usage of rename_lock (rhbz 1159313 1173814)

* Fri Dec 12 2014 Kyle McMartin <kyle@fedoraproject.org>
- build in ahci_platform on aarch64 temporarily.

* Fri Dec 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Remove pointless warning in cfg80211 (rhbz 1172543)

* Thu Dec 11 2014 Kyle McMartin <kyle@fedoraproject.org>
- kernel-arm64.patch: update from git.

* Wed Dec 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix UAS crashes with Seagate and Fresco Logic drives (rhbz 1164945)
- CVE-2014-8134 fix espfix for 32-bit KVM paravirt guests (rhbz 1172765 1172769)

* Tue Dec 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-1
- Linux v3.18

* Fri Dec 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc7.git3.1
- Linux v3.18-rc7-59-g56c67ce187a8

* Thu Dec 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc7.git2.1
- Linux v3.18-rc7-48-g7cc78f8fa02c

* Wed Dec 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc7.git1.1
- Linux v3.18-rc7-3-g3a18ca061311

* Mon Dec 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc7.git0.1
- Linux v3.18-rc7

* Thu Nov 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc6.git1.1
- Linux v3.18-rc6-28-g3314bf6ba2ac
- Gobble Gobble

* Mon Nov 24 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Linux v3.18-rc6
- Add quirk for Laser Mouse 6000 (rhbz 1165206)

* Fri Nov 21 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Move TPM drivers to main kernel package (rhbz 1164937)

* Wed Nov 19 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Disable SERIAL_8250 on s390x (rhbz 1158848)

* Mon Nov 17 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.18.0-0.rc5.git0.2
- Re-merge kernel-arm64.patch

* Mon Nov 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc5.git0.1
- Linux v3.18-rc5
- Disable debugging options.

* Fri Nov 14 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable I40EVF driver (rhbz 1164029)

* Fri Nov 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc4.git2.1
- Linux v3.18-rc4-184-gb23dc5a7cc6e

* Thu Nov 13 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch for MS Surface Pro 3 Type Cover (rhbz 1135338)
- CVE-2014-7843 aarch64: copying from /dev/zero causes local DoS (rhbz 1163744 1163745)

* Thu Nov 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc4.git1.1
- Linux v3.18-rc4-52-g04689e749b7e
- Reenable debugging options.

* Wed Nov 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-7841 sctp: NULL ptr deref on malformed packet (rhbz 1163087 1163095)

* Tue Nov 11 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.18.0-0.rc4.git0.2
- Re-enable kernel-arm64.patch, and fix up merge conflicts with 3.18-rc4

* Mon Nov 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix Samsung pci-e SSD handling on some macbooks (rhbz 1161805)

* Mon Nov 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc4.git0.1
- Linux v3.18-rc4
- Temporarily disable aarch64patches
- Disable debugging options.

* Fri Nov 07 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc3.git4.1
- Linux v3.18-rc3-82-ged78bb846e8b

* Thu Nov 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc3.git3.1
- Linux v3.18-rc3-68-g20f3963d8f48

* Wed Nov 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc3.git2.1
- Linux v3.18-rc3-61-ga1cff6e25e6e

* Tue Nov 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc3.git1.1
- Linux v3.18-rc3-31-g980d0d51b1c9
- Reenable debugging options.

* Mon Nov 03 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CONFIG_KXCJK1013
- Add driver for goodix touchscreen from Bastien Nocera

* Mon Nov 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc3.git0.1
- Linux v3.18-rc3
- Disable debugging options.

* Thu Oct 30 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc2.git3.1
- Linux v3.18-rc2-106-ga7ca10f263d7

* Wed Oct 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc2.git2.1
- Linux v3.18-rc2-53-g9f76628da20f

* Tue Oct 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add quirk for rfkill on Yoga 3 machines (rhbz 1157327)

* Tue Oct 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc2.git1.1
- Linux v3.18-rc2-43-gf7e87a44ef60
- Add two RCU patches to fix a deadlock and a hang
- Reenable debugging options.

* Mon Oct 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc2.git0.1
- Linux v3.18-rc2
- Disable debugging options.

* Sun Oct 26 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Update ARM config options, some minor cleanups

* Sun Oct 26 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git4.1
- Linux v3.18-rc1-422-g2cc91884b6b3

* Fri Oct 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git3.3
- CVE-2014-3610 kvm: noncanonical MSR writes (rhbz 1144883 1156543)
- CVE-2014-3611 kvm: PIT timer race condition (rhbz 1144878 1156537)
- CVE-2014-3646 kvm: vmx: invvpid vm exit not handled (rhbz 1144825 1156534)
- CVE-2014-8369 kvm: excessive pages un-pinning in kvm_iommu_map error path (rhbz 1156518 1156522)
- CVE-2014-8480 CVE-2014-8481 kvm: NULL pointer dereference during rip relative instruction emulation (rhbz 1156615 1156616)

* Fri Oct 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git3.1
- Linux v3.18-rc1-280-g816fb4175c29
- Add touchpad quirk for Fujitsu Lifebook A544/AH544 models (rhbz 1111138)

* Wed Oct 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git2.1
- Linux v3.18-rc1-221-gc3351dfabf5c
- Add patch to fix wifi on X550VB machines (rhbz 1089731)

* Tue Oct 21 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Drop pinctrl qcom revert now that it's dependencies should be merged

* Tue Oct 21 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.18.0-0.rc1.git1.2
- Re-enable kernel-arm64.patch after updating.
- CONFIG_SERIAL_8250_FINTEK moved to generic since it appears on x86-generic
  and arm64 now.
- CONFIG_IMX_THERMAL=n added to config-arm64.
- arm64: disable BPF_JIT temporarily

* Tue Oct 21 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git1.1
- Linux v3.18-rc1-68-gc2661b806092
- Make LOG_BUF_SHIFT on arm64 the same as the rest of the arches (rhbz 1123327)
- Enable RTC PL031 driver on arm64 (rhbz 1123882)
- Reenable debugging options.

* Mon Oct 20 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc1.git0.1
- Linux v3.18-rc1
- Disable debugging options.

* Fri Oct 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git9.4
- CVE-2014-8086 ext4: race condition (rhbz 1151353 1152608)
- Enable B43_PHY_G to fix b43 driver regression (rhbz 1152502)

* Wed Oct 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git9.3
- Revert Btrfs ro snapshot commit that causes filesystem corruption

* Wed Oct 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git9.1
- Linux v3.17-9670-g0429fbc0bdc2

* Tue Oct 14 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patches to fix elantech touchscreens (rhbz 1149509)

* Tue Oct 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git8.1
- Linux v3.17-9283-g2d65a9f48fcd

* Tue Oct 14 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git7.1
- Linux v3.17-8307-gf1d0d14120a8

* Mon Oct 13 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Update armv7/aarch64 config options

* Mon Oct 13 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git6.1
- Linux v3.17-7872-g5ff0b9e1a1da

* Sun Oct 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git5.1
- Linux v3.17-7639-g90eac7eee2f4

* Sun Oct 12 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable CONFIG_I2C_DESIGNWARE_PCI (rhbz 1045821)

* Fri Oct 10 2014 Josh Boyer <jwboyer@fedoraproject.org>
- CVE-2014-7970 VFS: DoS with USER_NS (rhbz 1151095 1151484)

* Fri Oct 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git4.1
- Linux v3.17-6136-gc798360cd143

* Thu Oct 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git3.1
- Linux v3.17-5585-g782d59c5dfc5

* Thu Oct 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git2.1
- Linux v3.17-5503-g35a9ad8af0bb

* Wed Oct 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.18.0-0.rc0.git1.1
- Linux v3.17-2860-gef0625b70dac
- Reenable debugging options.
- Temporarily disable aarch64patches
- Add patch to fix ATA blacklist

* Tue Oct 07 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Add patch to fix GFS2 regression (from Bob Peterson)

* Mon Oct 06 2014 Kyle McMartin <kyle@fedoraproject.org>
- enable 64K pages on arm64... (presently) needed to boot on amd seattle
  platforms due to physical memory being unreachable.

* Mon Oct 06 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-1
- Linux v3.17

* Fri Oct 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc7.git3.1
- Linux v3.17-rc7-76-g58586869599f
- Various ppc64/ppc64le config changes

* Thu Oct 02 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc7.git2.1
- Linux v3.17-rc7-46-g50dddff3cb9a
- Cleanup dead Kconfig symbols in config-* from Paul Bolle

* Wed Oct 01 2014 Kyle McMartin <kyle@fedoraproject.org>
- Update kernel-arm64.patch from git, again... enable AMD_XGBE on arm64.

* Wed Oct 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc7.git1.1
- Linux v3.17-rc7-6-gaad7fb916a10

* Tue Sep 30 2014 Kyle McMartin <kyle@fedoraproject.org> - 3.17.0-0.rc7.git0.2
- Revert some v3.16 changes to mach-highbank which broke L2 cache enablement.
  Will debug upstream separately, but we need F22/21 running there. (#1139762)

* Tue Sep 30 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Don't build Exynos4 on lpae kernel
- Add dts for BananaPi
- Minor ARM updates
- Build 6lowpan modules

* Mon Sep 29 2014 Kyle McMartin <kyle@fedoraproject.org>
- Update kernel-arm64.patch from git.

* Mon Sep 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc7.git0.1
- Linux v3.17-rc7

* Wed Sep 24 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc6.git2.1
- Linux v3.17-rc6-180-g452b6361c4d9

* Tue Sep 23 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix return code when adding keys (rhbz 1145318)
- Add patch to fix XPS 13 touchpad issue (rhbz 1123584)

* Tue Sep 23 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc6.git1.1
- Linux v3.17-rc6-125-gf3670394c29f

* Mon Sep 22 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc6.git0.1
- Linux v3.17-rc6
- Revert EFI GOT fixes as it causes boot failures
- Disable debugging options.

* Fri Sep 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git5.1
- Linux v3.17-rc5-105-g598a0c7d0932

* Fri Sep 19 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Disable NO_HZ_FULL again
- Enable early microcode loading (rhbz 1083716)

* Fri Sep 19 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git4.1
- Linux v3.17-rc5-63-gd9773ceabfaf
- Enable infiniband on s390x

* Thu Sep 18 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git3.1
- Linux v3.17-rc5-25-g8ba4caf1ee15

* Wed Sep 17 2014 Kyle McMartin <kyle@fedoraproject.org>
- I also like to live dangerously. (Re-enable RCU_FAST_NO_HZ which has been off
  since April 2012. Also enable NO_HZ_FULL on x86_64.)
- I added zipped modules ages ago, remove it from TODO.

* Wed Sep 17 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git2.1
- Linux v3.17-rc5-24-g37504a3be90b
- Fix vmwgfx header include (rhbz 1138759)

* Tue Sep 16 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git1.1
- Linux v3.17-rc5-13-g2324067fa9a4
- Reenable debugging options.

* Mon Sep 15 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc5.git0.1
- Linux v3.17-rc5
- Disable debugging options.

* Fri Sep 12 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc4.git4.1
- Linux v3.17-rc4-244-g5874cfed0b04

* Thu Sep 11 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Enable ACPI_I2C_OPREGION

* Thu Sep 11 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc4.git3.1
- Linux v3.17-rc4-168-g7ec62d421bdf
- Add support for touchpad in Asus X450 and X550 (rhbz 1110011)

* Wed Sep 10 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc4.git2.1
- Linux v3.17-rc4-158-ge874a5fe3efa
- Add patch to fix oops on keyring gc (rhbz 1116347)

* Tue Sep 09 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc4.git1.1
- Linux v3.17-rc4-140-g8c68face5548
- Reenable debugging options.

* Mon Sep 08 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Remove ppc32 support

* Mon Sep  8 2014 Peter Robinson <pbrobinson@fedoraproject.org>
- Build tools on ppc64le (rhbz 1138884)
- Some minor ppc64 cleanups

* Mon Sep 08 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc4.git0.1
- Linux v3.17-rc4
- Disable debugging options.

* Fri Sep 05 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc3.git3.1
- Linux v3.17-rc3-94-gb7fece1be8b1

* Thu Sep 04 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc3.git2.1
- Linux v3.17-rc3-63-g44bf091f5089
- Enable kexec bzImage signature verification (from Vivek Goyal)
- Add support for Wacom Cintiq Companion from Benjamin Tissoires (rhbz 1134969)

* Wed Sep 03 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc3.git1.1
- Linux v3.17-rc3-16-g955837d8f50e
- Reenable debugging options.

* Tue Sep 02 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Remove with_extra switch

* Mon Sep 01 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc3.git0.1
- Linux v3.17-rc3
- Disable debugging options.

* Fri Aug 29 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc2.git3.1
- Linux v3.17-rc2-89-g59753a805499

* Thu Aug 28 2014 Josh Boyer <jwboyer@fedoraproject.org>
- Fix NFSv3 ACL regression (rhbz 1132786)

* Thu Aug 28 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc2.git2.1
- Linux v3.17-rc2-42-gf1bd473f95e0
- Don't enable CONFIG_DEBUG_WW_MUTEX_SLOWPATH (rhbz 1114160)

* Wed Aug 27 2014 Josh Boyer <jwboyer@fedoraproject.org> - 3.17.0-0.rc2.git1.1
- Disable streams on via XHCI (rhbz 1132666)
- Linux v3.17-rc2-9-g68e370289c29
- Reenable debugging options.

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
