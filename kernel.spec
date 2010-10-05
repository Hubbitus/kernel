# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 0

# Save original buildid for later if it's defined
%if 0%{?buildid:1}
%global orig_buildid %{buildid}
%undefine buildid
%endif

###################################################################
# Polite request for people who spin their own kernel rpms:
# please modify the "buildid" define in a way that identifies
# that the kernel isn't the stock distribution kernel, for example,
# by setting the define to ".local" or ".bz123456". This will be
# appended to the full kernel version.
#
# (Uncomment the '#' and both spaces below to set the buildid.)
#
# % define buildid .local
###################################################################

# The buildid can also be specified on the rpmbuild command line
# by adding --define="buildid .whatever". If both the specfile and
# the environment define a buildid they will be concatenated together.
%if 0%{?orig_buildid:1}
%if 0%{?buildid:1}
%global srpm_buildid %{buildid}
%define buildid %{srpm_buildid}%{orig_buildid}
%else
%define buildid %{orig_buildid}
%endif
%endif

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
# For non-released -rc kernels, this will be prepended with "0.", so
# for example a 3 here will become 0.3
#
%global baserelease 33
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 2.6.22-rc7-git1 starts with a 2.6.21 base,
# which yields a base_sublevel of 21.
%define base_sublevel 35

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Is it a -stable RC?
%define stable_rc 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev .%{stable_update}
%define stable_base %{stable_update}
%if 0%{?stable_rc}
# stable RCs are incremental patches, so we need the previous stable patch
%define stable_base %(echo $((%{stable_update} - 1)))
%endif
%endif
%define rpmversion 2.6.%{base_sublevel}%{?stablerev}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
%define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
# The rc snapshot level
%define rcrev 6
# The git snapshot level
%define gitrev 3
# Set rpm version accordingly
%define rpmversion 2.6.%{upstream_sublevel}
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
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# kernel-firmware
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
# tools/perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 1}
# Want to build a the vsdo directories installed
%define with_vdso_install %{?_without_vdso_install: 0} %{?!_without_vdso_install: 1}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 1
%if 0%{?rawhide_skip_docs}
%define with_doc 0
%define doc_build_fail true
%endif

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the smp kernel (--with smponly):
%define with_smponly   %{?_with_smponly:      1} %{?!_with_smponly:      0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# should we do C=1 builds with sparse
%define with_sparse	%{?_with_sparse:      1} %{?!_with_sparse:      0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 0

# Want to build a vanilla kernel build without any non-upstream patches?
%define with_vanilla %{?_with_vanilla: 1} %{?!_with_vanilla: 0}

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%if 0%{?stable_rc}
%define stable_rctag .rc%{stable_rc}
%endif
%define pkg_release %{fedora_build}%{?stable_rctag}%{?buildid}%{?dist}

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
%define pkg_release 0.%{fedora_build}%{?rctag}%{?gittag}%{?buildid}%{?dist}

%endif

# The kernel tarball/base version
%define kversion 2.6.%{base_sublevel}

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
%else
%define variant_fedora -fedora
%endif

%define using_upstream_branch 0
%if 0%{?upstream_branch:1}
%define stable_update 0
%define using_upstream_branch 1
%define variant -%{upstream_branch}%{?variant_fedora}
%define pkg_release 0.%{fedora_build}%{upstream_branch_tag}%{?buildid}%{?dist}
%endif

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# kernel-PAE is only built on i686.
%ifarch i686
%define with_pae 1
%else
%define with_pae 0
%endif

# if requested, only build base kernel
%if %{with_baseonly}
%define with_smp 0
%define with_debug 0
%endif

# if requested, only build smp kernel
%if %{with_smponly}
%define with_up 0
%define with_debug 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%if %{debugbuildsenabled}
%define with_up 0
%endif
%define with_smp 0
%define with_pae 0
%define with_perf 0
%endif

%define all_x86 i386 i686

%if %{with_vdso_install}
# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64
%endif

# Overrides for generic default options

# only ppc and alphav56 need separate smp kernels
%ifnarch ppc alphaev56
%define with_smp 0
%endif

# don't do debug builds on anything but i686 and x86_64
%ifnarch i686 x86_64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_up 0
%define with_headers 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%define with_firmware  %{?_with_firmware:     1} %{?!_with_firmware:     0}
%endif

# bootwrapper is only on ppc
%ifnarch ppc ppc64
%define with_bootwrapper 0
%endif

# sparse blows up on ppc64 alpha and sparc64
%ifarch ppc64 ppc alpha sparc64
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch %{all_x86}
%define asmarch x86
%define hdrarch i386
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

%ifarch ppc64
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%endif

%ifarch sparc64
%define asmarch sparc
%define all_arch_configs kernel-%{version}-sparc64*.config
%define make_target image
%define kernel_image arch/sparc/boot/image
%define image_install_path boot
%define with_perf 0
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

%ifarch ia64
%define all_arch_configs kernel-%{version}-ia64*.config
%define image_install_path boot/efi/EFI/redhat
%define make_target compressed
%define kernel_image vmlinux.gz
%endif

%ifarch alpha alphaev56
%define all_arch_configs kernel-%{version}-alpha*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%ifarch %{arm}
%define all_arch_configs kernel-%{version}-arm*.config
%define image_install_path boot
%define hdrarch arm
%define make_target vmlinux
%define kernel_image vmlinux
%endif

%if %{nopatches}
# XXX temporary until last vdso patches are upstream
%define vdso_arches ppc ppc64
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%if %{nopatches}%{using_upstream_branch}
%define listnewconfig_fail 0
%else
%define listnewconfig_fail 1
%endif

# To temporarily exclude an architecture from being built, add it to
# %nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i386 s390 sparc %{arm}

%ifarch %nobuildarches
%define with_up 0
%define with_smp 0
%define with_pae 0
%define with_debuginfo 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

%define with_pae_debug 0
%if %{with_pae}
%define with_pae_debug %{with_debug}
%endif

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2

#
# Then a series of requirements that are distribution specific, either
# because we add patches for something, or the older versions have
# problems with the newer kernel or lack certain things that make
# integration in the distro harder than needed.
#
%define package_conflicts initscripts < 7.23, udev < 063-6, iptables < 1.3.2-1, ipw2200-firmware < 2.4, iwl4965-firmware < 228.57.2, selinux-policy-targeted < 1.25.3-14, squashfs-tools < 4.0, wireless-tools < 29-3

# We moved the drm include files into kernel-headers, make sure there's
# a recent enough libdrm-devel on the system that doesn't have those.
%define kernel_headers_conflicts libdrm-devel < 2.4.0-0.15

#
# Packages that need to be installed before the kernel is, because the %post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools, initscripts >= 8.11.1-1, grubby >= 7.0.10-1
%define initrd_prereq  dracut >= 001-7

#
# This macro does requires, provides, conflicts, obsoletes for a kernel package.
#	%%kernel_reqprovconf <subpackage>
# It uses any kernel_<subpackage>_conflicts and kernel_<subpackage>_obsoletes
# macros defined above.
#
%define kernel_reqprovconf \
Provides: kernel = %{rpmversion}-%{pkg_release}\
Provides: kernel-%{_target_cpu} = %{rpmversion}-%{pkg_release}%{?1:.%{1}}\
Provides: kernel-drm = 4.3.0\
Provides: kernel-drm-nouveau = 16\
Provides: kernel-modeset = 1\
Provides: kernel-uname-r = %{KVERREL}%{?1:.%{1}}\
Requires(pre): %{kernel_prereq}\
Requires(pre): %{initrd_prereq}\
%if %{with_firmware}\
Requires(pre): kernel-firmware >= %{rpmversion}-%{pkg_release}\
%else\
Requires(pre): linux-firmware >= 20100806-2\
%endif\
Requires(post): /sbin/new-kernel-pkg\
Requires(preun): /sbin/new-kernel-pkg\
Conflicts: %{kernel_dot_org_conflicts}\
Conflicts: %{package_conflicts}\
%{expand:%%{?kernel%{?1:_%{1}}_conflicts:Conflicts: %%{kernel%{?1:_%{1}}_conflicts}}}\
%{expand:%%{?kernel%{?1:_%{1}}_obsoletes:Obsoletes: %%{kernel%{?1:_%{1}}_obsoletes}}}\
%{expand:%%{?kernel%{?1:_%{1}}_provides:Provides: %%{kernel%{?1:_%{1}}_provides}}}\
# We can't let RPM do the dependencies automatic because it'll then pick up\
# a correct but undesirable perl dependency from the module headers which\
# isn't required for the kernel proper to function\
AutoReq: no\
AutoProv: yes\
%{nil}

Name: kernel%{?variant}
Group: System Environment/Kernel
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# DO NOT CHANGE THE 'ExclusiveArch' LINE TO TEMPORARILY EXCLUDE AN ARCHITECTURE BUILD.
# SET %%nobuildarches (ABOVE) INSTEAD
ExclusiveArch: noarch %{all_x86} x86_64 ppc ppc64 ia64 sparc sparc64 s390 s390x alpha alphaev56 %{arm}
ExclusiveOS: Linux

%kernel_reqprovconf
%ifarch x86_64 sparc64
Obsoletes: kernel-smp
%endif


#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: bzip2, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config
BuildRequires: net-tools
BuildRequires: xmlto, asciidoc
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed)
%endif
BuildConflicts: rhbuildsys(DiskFree) < 500Mb

%define fancy_debuginfo 0
%if %{with_debuginfo}
%if 0%{?fedora} >= 8 || 0%{?rhel} >= 6
%define fancy_debuginfo 1
%endif
%endif

%if %{fancy_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8.
BuildRequires: rpm-build >= 4.4.2.1-4
%define debuginfo_args --strict-build-id
%endif

Source0: ftp://ftp.kernel.org/pub/linux/kernel/v2.6/linux-%{kversion}.tar.bz2

Source11: genkey
Source14: find-provides
Source15: merge.pl

Source20: Makefile.config
Source21: config-debug
Source22: config-nodebug
Source23: config-generic
Source24: config-rhel-generic

Source30: config-x86-generic
Source31: config-i686-PAE

Source40: config-x86_64-generic

Source50: config-powerpc-generic
Source51: config-powerpc32-generic
Source52: config-powerpc32-smp
Source53: config-powerpc64

Source60: config-ia64-generic

Source70: config-s390x

Source90: config-sparc64-generic

Source100: config-arm

# Here should be only the patches up to the upstream canonical Linus tree.

# For a stable release kernel
%if 0%{?stable_update}
%if 0%{?stable_base}
%define    stable_patch_00  patch-2.6.%{base_sublevel}.%{stable_base}.bz2
Patch00: %{stable_patch_00}
%endif
%if 0%{?stable_rc}
%define    stable_patch_01  patch-2.6.%{base_sublevel}.%{stable_update}-rc%{stable_rc}.bz2
Patch01: %{stable_patch_01}
%endif

# non-released_kernel case
# These are automagically defined by the rcrev and gitrev values set up
# near the top of this spec file.
%else
%if 0%{?rcrev}
Patch00: patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
Patch01: patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
Patch00: patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
%endif
%endif
%endif

%if %{using_upstream_branch}
### BRANCH PATCH ###
%endif

Patch02: git-linus.diff

# we also need compile fixes for -vanilla
Patch04: linux-2.6-compile-fixes.patch

# build tweak for build ID magic, even for -vanilla
Patch05: linux-2.6-makefile-after_link.patch

Patch08: fix-oldnoconfig-to-dtrt.patch

%if !%{nopatches}


# revert upstream patches we get via other methods
Patch09: linux-2.6-upstream-reverts.patch
# Git trees.

# Standalone patches
Patch20: linux-2.6-hotfixes.patch


Patch30: linux-2.6-tracehook.patch
Patch31: linux-2.6-utrace.patch
Patch32: linux-2.6-utrace-ptrace.patch

Patch150: linux-2.6.29-sparc-IOC_TYPECHECK.patch

Patch160: linux-2.6-32bit-mmap-exec-randomization.patch
Patch161: linux-2.6-i386-nx-emulation.patch

Patch200: linux-2.6-debug-sizeof-structs.patch
Patch201: linux-2.6-debug-nmi-timeout.patch
Patch202: linux-2.6-debug-taint-vm.patch
Patch203: linux-2.6-debug-vm-would-have-oomkilled.patch
Patch204: linux-2.6-debug-always-inline-kzalloc.patch

Patch380: linux-2.6-defaults-pci_no_msi.patch
Patch381: linux-2.6-defaults-pci_use_crs.patch
Patch383: linux-2.6-defaults-aspm.patch

Patch390: linux-2.6-defaults-acpi-video.patch
Patch391: linux-2.6-acpi-video-dos.patch
Patch393: acpi-ec-add-delay-before-write.patch
Patch394: linux-2.6-acpi-debug-infinite-loop.patch
Patch395: acpi-update-battery-information-on-notification-0x81.patch

Patch450: linux-2.6-input-kill-stupid-messages.patch
Patch452: linux-2.6.30-no-pcspkr-modalias.patch
Patch454: thinkpad-acpi-fix-backlight.patch

Patch460: linux-2.6-serial-460800.patch

Patch470: die-floppy-die.patch

Patch510: linux-2.6-silence-noise.patch
Patch530: linux-2.6-silence-fbcon-logo.patch
Patch570: linux-2.6-selinux-mprotect-checks.patch
Patch580: linux-2.6-sparc-selinux-mprotect-checks.patch

Patch610: hda_intel-prealloc-4mb-dmabuffer.patch

Patch700: linux-2.6-e1000-ich9-montevina.patch

Patch800: linux-2.6-crash-driver.patch

# crypto/

# virt + ksm patches
Patch1555: fix_xen_guest_on_old_EC2.patch

# DRM
Patch1801: drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
Patch1802: revert-drm-kms-toggle-poll-around-switcheroo.patch
# nouveau + drm fixes
Patch1810: drm-nouveau-updates.patch
Patch1819: drm-intel-big-hammer.patch
# intel drm is all merged upstream
Patch1824: drm-intel-next.patch
# make sure the lvds comes back on lid open
Patch1825: drm-intel-make-lvds-work.patch
Patch1900: linux-2.6-intel-iommu-igfx.patch

# linux1394 git patches
Patch2200: linux-2.6-firewire-git-update.patch
Patch2201: linux-2.6-firewire-git-pending.patch

# Quiet boot fixes
# silence the ACPI blacklist code
Patch2802: linux-2.6-silence-acpi-blacklist.patch

# media patches
Patch2899: linux-2.6-v4l-dvb-fixes.patch
Patch2900: linux-2.6-v4l-dvb-update.patch
Patch2901: linux-2.6-v4l-dvb-experimental.patch
Patch2902: linux-2.6-v4l-dvb-uvcvideo-update.patch

Patch2910: linux-2.6-v4l-dvb-add-lgdt3304-support.patch
Patch2912: linux-2.6-v4l-dvb-ir-core-update.patch

#Patch2916: lirc-staging-2.6.36-fixes.patch
Patch2917: hdpvr-ir-enable.patch

Patch3000: linux-2.6-rcu-sched-warning.patch

# fs fixes

# NFSv4

# patches headed upstream

Patch12010: add-appleir-usb-driver.patch

Patch12016: disable-i8042-check-on-apple-mac.patch

Patch12017: prevent-runtime-conntrack-changes.patch

Patch12018: neuter_intel_microcode_load.patch

Patch12030: tpm-fix-stall-on-boot.patch

# Wacom Bamboo
Patch12100: wacom-01-add-fuzz-parameters-to-features.patch
Patch12105: wacom-02-parse-the-bamboo-device-family.patch
Patch12110: wacom-03-collect-device-quirks-into-single-function.patch
Patch12115: wacom-04-add-support-for-the-bamboo-touch-trackpad.patch
Patch12120: wacom-05-add-a-quirk-for-low-resolution-bamboo-devices.patch
Patch12125: wacom-06-request-tablet-data-for-bamboo-pens.patch
Patch12130: wacom-07-move-bamboo-touch-irq-to-its-own-function.patch
Patch12135: wacom-08-add-support-for-bamboo-pen.patch
Patch12140: wacom-09-disable-bamboo-touchpad-when-pen-is-being-used.patch

# Runtime power management
Patch12200: linux-2.6-bluetooth-autosuspend.patch
Patch12201: linux-2.6-uvc-autosuspend.patch
Patch12202: linux-2.6-qcserial-autosuspend.patch
Patch12203: linux-2.6-usb-pci-autosuspend.patch

# PCI patches to fix problems with _CRS
Patch12221: pci-v2-1-4-resources-ensure-alignment-callback-doesn-t-allocate-below-available-start.patch
Patch12222: pci-v2-2-4-x86-PCI-allocate-space-from-the-end-of-a-region-not-the-beginning.patch
Patch12223: pci-v2-3-4-resources-allocate-space-within-a-region-from-the-top-down.patch
Patch12224: pci-v2-4-4-PCI-allocate-bus-resources-from-the-top-down.patch

Patch12300: btusb-macbookpro-7-1.patch
Patch12301: btusb-macbookpro-6-2.patch

%endif

BuildRoot: %{_tmppath}/kernel-%{KVERREL}-root

%description
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system: memory allocation, process allocation, device
input and output, etc.


%package doc
Summary: Various documentation bits found in the kernel source
Group: Documentation
%description doc
This package contains documentation files from the kernel
source. Various bits of information about the Linux kernel and the
device drivers shipped with it are documented in these files.

You'll want to install this package if you need a reference to the
options that can be passed to Linux kernel modules at load time.


%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: glibc-kernheaders
Provides: glibc-kernheaders = 3.0-46
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package firmware
Summary: Firmware files used by the Linux kernel
Group: Development/System
# This is... complicated.
# Look at the WHENCE file.
License: GPL+ and GPLv2+ and MIT and Redistributable, no modification permitted
%if "x%{?variant}" != "x"
Provides: kernel-firmware = %{rpmversion}-%{pkg_release}
%endif
%description firmware
Kernel-firmware includes firmware files required for some devices to
operate.

%package bootwrapper
Summary: Boot wrapper files for generating combined kernel + initrd images
Group: Development/System
Requires: gzip
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
This package provides the perf tool and the supporting documentation.
%endif


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
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '/.*/%%{KVERREL}%{?1:\.%{1}}/.*|/.*%%{KVERREL}%{?1:\.%{1}}(\.debug)?' -o debuginfo%{?1}.list}\
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
Provides: kernel-devel-%{_target_cpu} = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel = %{version}-%{release}%{?1:.%{1}}\
Provides: kernel-devel-uname-r = %{KVERREL}%{?1:.%{1}}\
AutoReqProv: no\
Requires(pre): /usr/bin/find\
Requires: perl\
%description -n kernel%{?variant}%{?1:-%{1}}-devel\
This package provides kernel headers and makefiles sufficient to build modules\
against the %{?2:%{2} }kernel package.\
%{nil}

#
# This macro creates a kernel-<subpackage> and its -devel and -debuginfo too.
#	%%define variant_summary The Linux kernel compiled for <configuration>
#	%%kernel_variant_package [-n <pretty-name>] <subpackage>
#
%define kernel_variant_package(n:) \
%package %1\
Summary: %{variant_summary}\
Group: System Environment/Kernel\
%kernel_reqprovconf\
%{expand:%%kernel_devel_package %1 %{!?-n:%1}%{?-n:%{-n*}}}\
%{expand:%%kernel_debuginfo_package %1}\
%{nil}


# First the auxiliary packages of the main kernel package.
%kernel_devel_package
%kernel_debuginfo_package


# Now, each variant package.

%define variant_summary The Linux kernel compiled for SMP machines
%kernel_variant_package -n SMP smp
%description smp
This package includes a SMP version of the Linux kernel. It is
required only on machines with two or more CPUs as well as machines with
hyperthreading technology.

Install the kernel-smp package if your machine uses two or more CPUs.


%define variant_summary The Linux kernel compiled for PAE capable machines
%kernel_variant_package PAE
%description PAE
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.


%define variant_summary The Linux kernel compiled with extra debugging enabled for PAE capable machines
%kernel_variant_package PAEdebug
Obsoletes: kernel-PAE-debug
%description PAEdebug
This package includes a version of the Linux kernel with support for up to
64GB of high memory. It requires a CPU with Physical Address Extensions (PAE).
The non-PAE kernel can only address up to 4GB of memory.
Install the kernel-PAE package if your machine has more than 4GB of memory.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


%define variant_summary The Linux kernel compiled with extra debugging enabled
%kernel_variant_package debug
%description debug
The kernel package contains the Linux kernel (vmlinuz), the core of any
Linux operating system.  The kernel handles the basic functions
of the operating system:  memory allocation, process allocation, device
input and output, etc.

This variant of the kernel has numerous debugging options enabled.
It should only be installed when trying to gather additional information
on kernel bugs, as some of these options impact performance noticably.


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
%if !%{using_upstream_branch}
  if ! egrep "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:10}" != "patch-2.6." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
%endif
  case "$patch" in
  *.bz2) bunzip2 < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
  *.gz) gunzip < "$RPM_SOURCE_DIR/$patch" | $patch_command ${1+"$@"} ;;
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

# we don't want a .config file when building firmware: it just confuses the build system
%define build_firmware \
   mv .config .config.firmware_save \
   make INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware firmware_install \
   mv .config.firmware_save .config

# First we unpack the kernel tarball.
# If this isn't the first make prep, we use links to the existing clean tarball
# which speeds things up quite a bit.

# Update to latest upstream.
%if 0%{?released_kernel}
%define vanillaversion 2.6.%{base_sublevel}
# non-released_kernel case
%else
%if 0%{?rcrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}
%if 0%{?gitrev}
%define vanillaversion 2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
%define vanillaversion 2.6.%{base_sublevel}-git%{gitrev}
%else
%define vanillaversion 2.6.%{base_sublevel}
%endif
%endif
%endif

# %{vanillaversion} : the full version name, e.g. 2.6.35-rc6-git3
# %{kversion}       : the base version, e.g. 2.6.34

# Use kernel-%{kversion}%{?dist} as the top-level directory name
# so we can prep different trees within a single git directory.

# Build a list of the other top-level kernel tree directories.
# This will be used to hardlink identical vanilla subdirs.
sharedirs=$(find "$PWD" -maxdepth 1 -type d -name 'kernel-2.6.*' \
            | grep -x -v "$PWD"/kernel-%{kversion}%{?dist}) ||:

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
      cp -rl $sharedir/vanilla-%{kversion} .
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

    cp -rl $sharedir/vanilla-%{vanillaversion} .

  else

    # Need to apply patches to the base vanilla version.
    cp -rl vanilla-%{kversion} vanilla-%{vanillaversion}
    cd vanilla-%{vanillaversion}

# Update vanilla to the latest upstream.
# (non-released_kernel case only)
%if 0%{?rcrev}
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}.bz2
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{upstream_sublevel}-rc%{rcrev}-git%{gitrev}.bz2
%endif
%else
# pre-{base_sublevel+1}-rc1 case
%if 0%{?gitrev}
    ApplyPatch patch-2.6.%{base_sublevel}-git%{gitrev}.bz2
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
if [ -d linux-%{kversion}.%{_target_cpu} ]; then
  # Just in case we ctrl-c'd a prep already
  rm -rf deleteme.%{_target_cpu}
  # Move away the stale away, and delete in background.
  mv linux-%{kversion}.%{_target_cpu} deleteme.%{_target_cpu}
  rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{vanillaversion} linux-%{kversion}.%{_target_cpu}

cd linux-%{kversion}.%{_target_cpu}

# released_kernel with possible stable updates
%if 0%{?stable_base}
ApplyPatch %{stable_patch_00}
%endif
%if 0%{?stable_rc}
ApplyPatch %{stable_patch_01}
%endif

%if %{using_upstream_branch}
### BRANCH APPLY ###
%endif

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/config-* .
cp %{SOURCE15} .

# Dynamically generate kernel .config files from config-* files
make -f %{SOURCE20} VERSION=%{version} configs

#if a rhel kernel, apply the rhel config options
%if 0%{?rhel}
  for i in %{all_arch_configs}
  do
    mv $i $i.tmp
    ./merge.pl config-rhel-generic $i.tmp > $i
    rm $i.tmp
  done
%endif

ApplyOptionalPatch git-linus.diff

ApplyPatch fix-oldnoconfig-to-dtrt.patch
ApplyPatch linux-2.6-makefile-after_link.patch

#
# misc small stuff to make things compile
#
ApplyOptionalPatch linux-2.6-compile-fixes.patch

%if !%{nopatches}

# revert patches from upstream that conflict or that we get via other means
ApplyOptionalPatch linux-2.6-upstream-reverts.patch -R

ApplyPatch linux-2.6-hotfixes.patch

# Roland's utrace ptrace replacement.
ApplyPatch linux-2.6-tracehook.patch
ApplyPatch linux-2.6-utrace.patch
ApplyPatch linux-2.6-utrace-ptrace.patch

# Architecture patches
# x86(-64)

#
# Intel IOMMU
#

#
# PowerPC
#

#
# SPARC64
#
ApplyPatch linux-2.6.29-sparc-IOC_TYPECHECK.patch

#
# Exec shield
#
ApplyPatch linux-2.6-i386-nx-emulation.patch
ApplyPatch linux-2.6-32bit-mmap-exec-randomization.patch

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
ApplyPatch linux-2.6-defaults-acpi-video.patch
ApplyPatch linux-2.6-acpi-video-dos.patch
ApplyPatch acpi-ec-add-delay-before-write.patch
ApplyPatch linux-2.6-acpi-debug-infinite-loop.patch
ApplyPatch acpi-update-battery-information-on-notification-0x81.patch

# Various low-impact patches to aid debugging.
ApplyPatch linux-2.6-debug-sizeof-structs.patch
ApplyPatch linux-2.6-debug-nmi-timeout.patch
ApplyPatch linux-2.6-debug-taint-vm.patch
###FIX###ApplyPatch linux-2.6-debug-vm-would-have-oomkilled.patch
ApplyPatch linux-2.6-debug-always-inline-kzalloc.patch

#
# PCI
#
# make default state of PCI MSI a config option
ApplyPatch linux-2.6-defaults-pci_no_msi.patch
ApplyPatch linux-2.6-defaults-pci_use_crs.patch
# enable ASPM by default on hardware we expect to work
ApplyPatch linux-2.6-defaults-aspm.patch

#
# SCSI Bits.
#

# ACPI

# ALSA
ApplyPatch hda_intel-prealloc-4mb-dmabuffer.patch

# Networking

# Misc fixes
# The input layer spews crap no-one cares about.
ApplyPatch linux-2.6-input-kill-stupid-messages.patch

# stop floppy.ko from autoloading during udev...
ApplyPatch die-floppy-die.patch

ApplyPatch linux-2.6.30-no-pcspkr-modalias.patch

#ApplyPatch thinkpad-acpi-fix-backlight.patch

# Allow to use 480600 baud on 16C950 UARTs
ApplyPatch linux-2.6-serial-460800.patch

# Silence some useless messages that still get printed with 'quiet'
ApplyPatch linux-2.6-silence-noise.patch

# Make fbcon not show the penguins with 'quiet'
ApplyPatch linux-2.6-silence-fbcon-logo.patch

# Fix the SELinux mprotect checks on executable mappings
#ApplyPatch linux-2.6-selinux-mprotect-checks.patch
# Fix SELinux for sparc
# FIXME: Can we drop this now? See updated linux-2.6-selinux-mprotect-checks.patch
#ApplyPatch linux-2.6-sparc-selinux-mprotect-checks.patch

# Changes to upstream defaults.


# /dev/crash driver.
ApplyPatch linux-2.6-crash-driver.patch

# Hack e1000e to work on Montevina SDV
ApplyPatch linux-2.6-e1000-ich9-montevina.patch

# crypto/

# Assorted Virt Fixes
ApplyPatch fix_xen_guest_on_old_EC2.patch

#ApplyPatch drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
#ApplyPatch revert-drm-kms-toggle-poll-around-switcheroo.patch

# Nouveau DRM + drm fixes
#ApplyPatch drm-nouveau-updates.patch
ApplyPatch drm-intel-big-hammer.patch
ApplyOptionalPatch drm-intel-next.patch
ApplyPatch drm-intel-make-lvds-work.patch
ApplyPatch linux-2.6-intel-iommu-igfx.patch

# linux1394 git patches
#ApplyPatch linux-2.6-firewire-git-update.patch
#ApplyOptionalPatch linux-2.6-firewire-git-pending.patch

# silence the ACPI blacklist code
ApplyPatch linux-2.6-silence-acpi-blacklist.patch

# V4L/DVB updates/fixes/experimental drivers
#  apply if non-empty
ApplyOptionalPatch linux-2.6-v4l-dvb-fixes.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-update.patch
ApplyOptionalPatch linux-2.6-v4l-dvb-experimental.patch
#ApplyPatch linux-2.6-v4l-dvb-uvcvideo-update.patch
#ApplyPatch linux-2.6-v4l-dvb-ir-core-update.patch

###FIX###ApplyPatch linux-2.6-v4l-dvb-add-lgdt3304-support.patch

# http://www.lirc.org/
#ApplyOptionalPatch lirc-staging-2.6.36-fixes.patch
# enable IR receiver on Hauppauge HD PVR (v4l-dvb merge pending)
ApplyPatch hdpvr-ir-enable.patch

# silence another rcu_reference warning
ApplyPatch linux-2.6-rcu-sched-warning.patch

# Patches headed upstream
ApplyPatch disable-i8042-check-on-apple-mac.patch

ApplyPatch add-appleir-usb-driver.patch

ApplyPatch neuter_intel_microcode_load.patch

# try to fix stalls during boot (#530393)
ApplyPatch tpm-fix-stall-on-boot.patch

# Wacom Bamboo
ApplyPatch wacom-01-add-fuzz-parameters-to-features.patch
ApplyPatch wacom-02-parse-the-bamboo-device-family.patch
ApplyPatch wacom-03-collect-device-quirks-into-single-function.patch
ApplyPatch wacom-04-add-support-for-the-bamboo-touch-trackpad.patch
ApplyPatch wacom-05-add-a-quirk-for-low-resolution-bamboo-devices.patch
ApplyPatch wacom-06-request-tablet-data-for-bamboo-pens.patch
ApplyPatch wacom-07-move-bamboo-touch-irq-to-its-own-function.patch
ApplyPatch wacom-08-add-support-for-bamboo-pen.patch
ApplyPatch wacom-09-disable-bamboo-touchpad-when-pen-is-being-used.patch

# Runtime PM
ApplyPatch linux-2.6-bluetooth-autosuspend.patch
ApplyPatch linux-2.6-uvc-autosuspend.patch
ApplyPatch linux-2.6-qcserial-autosuspend.patch
ApplyPatch linux-2.6-usb-pci-autosuspend.patch

# PCI patches to fix problems with _CRS
# ( from https://bugzilla.kernel.org/show_bug.cgi?id=16228#c49 )
ApplyPatch pci-v2-1-4-resources-ensure-alignment-callback-doesn-t-allocate-below-available-start.patch
ApplyPatch pci-v2-2-4-x86-PCI-allocate-space-from-the-end-of-a-region-not-the-beginning.patch
ApplyPatch pci-v2-3-4-resources-allocate-space-within-a-region-from-the-top-down.patch
ApplyPatch pci-v2-4-4-PCI-allocate-bus-resources-from-the-top-down.patch

ApplyPatch btusb-macbookpro-7-1.patch
ApplyPatch btusb-macbookpro-6-2.patch

ApplyPatch fix-intel_ips-to-work-properly.patch

# END OF PATCH APPLICATIONS

%endif

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

mkdir configs

# Remove configs not for the buildarch
for cfg in kernel-%{version}-*.config; do
  if [ `echo %{all_arch_configs} | grep -c $cfg` -eq 0 ]; then
    rm -f $cfg
  fi
done

%if !%{debugbuildsenabled}
rm -f kernel-%{version}-*debug.config
%endif

# now run oldconfig over all the config files
for i in *.config
do
  mv $i .config
  Arch=`head -1 .config | cut -b 3-`
  make ARCH=$Arch listnewconfig | egrep '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 0
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

cd ..

###
### build
###
%build

%if %{with_sparse}
%define sparse_mflags	C=1
%endif

%if %{fancy_debuginfo}
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
    InstallName=${4:-vmlinuz}

    # Pick the right config file for the kernel we're building
    Config=kernel-%{version}-%{_target_cpu}${Flavour:+-${Flavour}}.config
    DevelDir=/usr/src/kernels/%{KVERREL}${Flavour:+.${Flavour}}

    # When the bootable image is just the ELF kernel, strip it.
    # We already copy the unstripped file into the debuginfo package.
    if [ "$KernelImage" = vmlinux ]; then
      CopyKernel=cp_vmlinux
    else
      CopyKernel=cp
    fi

    KernelVer=%{version}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}
    echo BUILDING A KERNEL FOR ${Flavour} %{_target_cpu}...

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = %{?stablerev}-%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up SUBLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^SUBLEVEL.*/SUBLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make -s mrproper
    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

    make -s ARCH=$Arch oldnoconfig >/dev/null
    make -s ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}
    make -s ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1

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
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    # Override $(mod-fw) because we don't want it to install any firmware
    # We'll do that ourselves with 'make firmware_install'
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
%ifarch %{vdso_arches}
    make -s ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
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
%ifarch ppc
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/linux/autoconf.h
    # Copy .config to include/config/auto.conf so "make prepare" is unnecessary.
    cp $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/config/auto.conf

%if %{fancy_debuginfo}
    if test -s vmlinux.id; then
      cp vmlinux.id $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/vmlinux.id
    else
      echo >&2 "*** ERROR *** no vmlinux build ID! ***"
      exit 1
    fi
%endif

    #
    # save the vmlinux file for kernel debugging into the kernel-debuginfo rpm
    #
%if %{with_debuginfo}
    mkdir -p $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
    cp vmlinux $RPM_BUILD_ROOT%{debuginfodir}/lib/modules/$KernelVer
%endif

    find $RPM_BUILD_ROOT/lib/modules/$KernelVer -name "*.ko" -type f >modnames

    # mark modules executable so that strip-to-file can strip them
    xargs --no-run-if-empty chmod u+x < modnames

    # Generate a list of modules for block and networking.

    fgrep /drivers/ modnames | xargs --no-run-if-empty nm -upA |
    sed -n 's,^.*/\([^/]*\.ko\):  *U \(.*\)$,\1 \2,p' > drivers.undef

    collect_modules_list()
    {
      sed -r -n -e "s/^([^ ]+) \\.?($2)\$/\\1/p" drivers.undef |
      LC_ALL=C sort -u > $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$1
    }

    collect_modules_list networking \
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler'
    collect_modules_list drm \
    			 'drm_open|drm_init'
    collect_modules_list modesetting \
    			 'drm_crtc_init'

    # detect missing or incorrect license tags
    rm -f modinfo
    while read i
    do
      echo -n "${i#$RPM_BUILD_ROOT/lib/modules/$KernelVer/} " >> modinfo
      /sbin/modinfo -l $i >> modinfo
    done < modnames

    egrep -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
    ln -sf ../../..$DevelDir $RPM_BUILD_ROOT/lib/modules/$KernelVer/build
}

###
# DO it...
###

# prepare directories
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/boot
mkdir -p $RPM_BUILD_ROOT%{_libexecdir}

cd linux-%{kversion}.%{_target_cpu}

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_pae_debug}
BuildKernel %make_target %kernel_image PAEdebug
%endif

%if %{with_pae}
BuildKernel %make_target %kernel_image PAE
%endif

%if %{with_up}
BuildKernel %make_target %kernel_image
%endif

%if %{with_smp}
BuildKernel %make_target %kernel_image smp
%endif

%global perf_make \
  make %{?_smp_mflags} -C tools/perf -s V=1 NO_DEMANGLE=1 prefix=%{_prefix}
%if %{with_perf}
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_doc}
# Make the HTML and man pages.
make %{?_smp_mflags} htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

###
### Special hacks for debuginfo subpackages.
###

# This macro is used by %%install, so we must redefine it before that.
%define debug_package %{nil}

%if %{fancy_debuginfo}
%define __debug_install_post \
  /usr/lib/rpm/find-debuginfo.sh %{debuginfo_args} %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

%if %{with_debuginfo}
%ifnarch noarch
%global __debug_package 1
%files -f debugfiles.list debuginfo-common-%{_target_cpu}
%defattr(-,root,root)
%endif
%endif

###
### install
###

%install

cd linux-%{kversion}.%{_target_cpu}

%if %{with_doc}
docdir=$RPM_BUILD_ROOT%{_datadir}/doc/kernel-doc-%{rpmversion}
man9dir=$RPM_BUILD_ROOT%{_datadir}/man/man9

# copy the source over
mkdir -p $docdir
tar -f - --exclude=man --exclude='.*' -c Documentation | tar xf - -C $docdir

# Install man pages for the kernel API.
mkdir -p $man9dir
find Documentation/DocBook/man -name '*.9.gz' -print0 |
xargs -0 --no-run-if-empty %{__install} -m 444 -t $man9dir $m
ls $man9dir | grep -q '' || > $man9dir/BROKEN
%endif # with_doc

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || %{doc_build_fail}
%endif

%if %{with_headers}
# Install kernel headers
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

# glibc provides scsi headers for itself, for now
rm -rf $RPM_BUILD_ROOT/usr/include/scsi
rm -f $RPM_BUILD_ROOT/usr/include/asm*/atomic.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/io.h
rm -f $RPM_BUILD_ROOT/usr/include/asm*/irq.h
%endif

%if %{with_firmware}
%{build_firmware}
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
    (cd /usr/src/kernels/%{KVERREL}%{?1:.%{1}} &&\
     /usr/bin/find . -type f | while read f; do\
       hardlink -c /usr/src/kernels/*.fc*.*/$f $f\
     done)\
fi\
%{nil}

# This macro defines a %%posttrans script for a kernel package.
#	%%kernel_variant_posttrans [<subpackage>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_posttrans() \
%{expand:%%posttrans %{?1}}\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
/sbin/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

#
# This macro defines a %%post script for a kernel package and its devel package.
#	%%kernel_variant_post [-v <subpackage>] [-r <replace>]
# More text can follow to go at the end of this variant's %%post.
#
%define kernel_variant_post(v:r:) \
%{expand:%%kernel_devel_post %{?-v*}}\
%{expand:%%kernel_variant_posttrans %{?-v*}}\
%{expand:%%post %{?-v*}}\
%{-r:\
if [ `uname -i` == "x86_64" -o `uname -i` == "i386" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
/sbin/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
/sbin/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post -r kernel-smp

%kernel_variant_preun smp
%kernel_variant_post -v smp

%kernel_variant_preun PAE
%kernel_variant_post -v PAE -r (kernel|kernel-smp)

%kernel_variant_preun debug
%kernel_variant_post -v debug

%kernel_variant_post -v PAEdebug -r (kernel|kernel-smp)
%kernel_variant_preun PAEdebug

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

%if %{with_firmware}
%files firmware
%defattr(-,root,root)
/lib/firmware/*
%doc linux-%{kversion}.%{_target_cpu}/firmware/WHENCE
%endif

%if %{with_bootwrapper}
%files bootwrapper
%defattr(-,root,root)
/usr/sbin/*
%{_libdir}/kernel-wrapper
%endif

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/*
%endif

# This is %{image_install_path} on an arch where that includes ELF files,
# or empty otherwise.
%define elf_image_install_path %{?kernel_image_elf:%{image_install_path}}

#
# This macro defines the %%files sections for a kernel package
# and its devel and debuginfo packages.
#	%%kernel_variant_files [-k vmlinux] <condition> <subpackage>
#
%define kernel_variant_files(k:) \
%if %{1}\
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
/boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/config-%{KVERREL}%{?2:.%{2}}\
%dir /lib/modules/%{KVERREL}%{?2:.%{2}}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/kernel\
/lib/modules/%{KVERREL}%{?2:.%{2}}/build\
/lib/modules/%{KVERREL}%{?2:.%{2}}/source\
/lib/modules/%{KVERREL}%{?2:.%{2}}/extra\
/lib/modules/%{KVERREL}%{?2:.%{2}}/updates\
%ifarch %{vdso_arches}\
/lib/modules/%{KVERREL}%{?2:.%{2}}/vdso\
/etc/ld.so.conf.d/kernel-%{KVERREL}%{?2:.%{2}}.conf\
%endif\
/lib/modules/%{KVERREL}%{?2:.%{2}}/modules.*\
%ghost /boot/initramfs-%{KVERREL}%{?2:.%{2}}.img\
%{expand:%%files %{?2:%{2}-}devel}\
%defattr(-,root,root)\
/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%if %{with_debuginfo}\
%ifnarch noarch\
%if %{fancy_debuginfo}\
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%else\
%{expand:%%files %{?2:%{2}-}debuginfo}\
%endif\
%defattr(-,root,root)\
%if !%{fancy_debuginfo}\
%if "%{elf_image_install_path}" != ""\
%{debuginfodir}/%{elf_image_install_path}/*-%{KVERREL}%{?2:.%{2}}.debug\
%endif\
%{debuginfodir}/lib/modules/%{KVERREL}%{?2:.%{2}}\
%{debuginfodir}/usr/src/kernels/%{KVERREL}%{?2:.%{2}}\
%endif\
%endif\
%endif\
%endif\
%{nil}


%kernel_variant_files %{with_up}
%kernel_variant_files %{with_smp} smp
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_pae} PAE
%kernel_variant_files %{with_pae_debug} PAEdebug

# plz don't put in a version string unless you're going to tag
# and build.

#  ___________________________________________________________
# / This branch is for Fedora 15. You probably want to commit \
# \ to the F-14 branch instead, or in addition to this one.   /
#  -----------------------------------------------------------
#         \   ^__^
#          \  (@@)\_______
#             (__)\       )\/\
#                 ||----w |
#                 ||     ||

%changelog
* Tue Oct 05 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.33.rc6.git3
- Linux 2.6.36-rc6-git3
- Drop intel_ips patches merged upstream.

* Sun Oct 03 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.32.rc6.git2
- Enable printk.time by default for more useful logs.

* Sat Oct 02 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.31.rc6.git2
- Linux 2.6.36-rc6-git2

* Thu Sep 30 2010 Dave Jones <davej@redhat.com>
- silence another rcu_reference warning

* Thu Sep 30 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.30.rc6
- Collection of patches to make intel_ips work properly.

* Wed Sep 29 2010 Dave Jones <davej@redhat.com>
- Add back an old hack to make an SDV e1000e variant work.

* Wed Sep 29 2010 Dave Jones <davej@redhat.com>
- Enable IB700 watchdog (used by qemu/kvm). (#637152)

* Tue Sep 28 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.28.rc6
- Linux 2.6.36-rc6

* Fri Sep 24 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.36-0.27.rc5.git6
- Linux 2.6.36-rc5-git6

* Thu Sep 23 2010 Kyle McMartin <kyle@redhat.com>
- Bump x86 NR_CPUS to 64. (Still 512/256 on x86_64.)

* Thu Sep 23 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.36-0.26.rc5.git4
- Linux 2.6.36-rc5-git4
- Drop merged patches:
  fix-icebp-breakpoints.patch
  linux-2.6.35.4-virtio_console-fix-poll.patch
- Add patches to fix problems with PCI _CRS

* Thu Sep 23 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.25.rc5
- Add s390 vdso AFTER_LINK to Roland's linux-2.6-makefile-after_link.patch

* Thu Sep 23 2010 Kyle McMartin <kyle@redhat.com>
- Snipe ACPI patch from mjg59 to fix battery levels on some laptops.

* Tue Sep 21 2010 Kyle McMartin <kyle@redhat.com>
- Add new btusb ids for MacBookPro from wwoods@.

* Mon Sep 20 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.24.rc5
- Linux 2.6.36-rc5

* Sun Sep 19 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.23.rc4.git4
- Linux 2.6.36-rc4-git4
- Drop alsa-fix-substream-proc-status-read.patch, now merged.

* Fri Sep 17 2010 Matthew Garrett <mjg@redhat.com>
- linux-2.6-bluetooth-autosuspend.patch
  linux-2.6-uvc-autosuspend.patch
  linux-2.6-qcserial-autosuspend.patch
  linux-2.6-usb-pci-autosuspend.patch - Get some more devices into USB
  autosuspend by default, and then put unused USB controllers to sleep

* Thu Sep 16 2010 Hans de Goede <hdegoede@redhat.com>
- Small fix to virtio_console poll fix from upstream review

* Wed Sep 15 2010 Hans de Goede <hdegoede@redhat.com>
- virtio_console: Fix poll/select blocking even though there is data to read

* Wed Sep 15 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.22.rc4.git2
- Linux 2.6.36-rc4-git2
- Fix up add-appleir-usb-driver.patch after HID core changes.

* Mon Sep 13 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.21.rc4.git1
- Linux 2.6.36-rc4-git1
- Add preliminary support for Wacom Bamboo pen and touch devices.
- Require python-devel and perl(ExtUtils::Embed) when building perf package (#632942)

* Sat Sep 11 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.20.rc3.git4
- Linux 2.6.36-rc3-git4
- Drop revert-drm-i915-enable-rc6-on-ironlake.patch, now merged

* Fri Sep 10 2010 Bastien Nocera <bnocera@redhat.com> - 2.6.36-0.19.rc3.git1
- Update AppleIR patch to work, and support the enter key on
  newer remotes

* Wed Sep 08 2010 Kyle McMartin <kyle@redhat.com>
- Enable GPIO_SYSFS. (#631958)

* Wed Sep 08 2010 Kyle McMartin <kyle@redhat.com>
- Make pci=use_crs a compile-time config option we can switch the default
  value of easily.

* Wed Sep 08 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.18.rc3.git1
- 2.6.36-rc3-git1
- Set CONFIG_CRYPTO_MANAGER_DISABLE_TESTS for nodebug, and unset for debug.
  Which seems like the sensible thing to do given the Kconfig default is y.

* Tue Sep 07 2010 Dave Jones <davej@redhat.com>
- Disable hung task checker, it only ever causes false positives. (#630777)

* Tue Sep 07 2010 Kyle McMartin <kyle@redhat.com> 2.6.36-0.17.rc3.git0
- Revert ce171780 which breaks my graphics on resume.
  (drm/i915: Enable RC6 on Ironlake.)

* Fri Sep 03 2010 Kyle McMartin <kyle@redhat.com>
- Restore AppleIR USB driver which got lost between F-13 and now.

* Fri Sep 03 2010 Dave Jones <davej@redhat.com> 2.6.36-0.16.rc3.git0
- exec-randomization: brk away from exec rand area (Kees Cook)

* Fri Sep 03 2010 Dave Jones <davej@redhat.com>
- Remove the execshield boot parameter.
  Based on a patch from Kees Cook

* Thu Sep 02 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.15.rc3.git0
- Add patch from ALSA mailing list to try to fix bug #628404
- tpm-fix-stall-on-boot.patch: attempt to fix stalls during boot (#530393)

* Wed Sep 01 2010 Kyle McMartin <kyle@redhat.com> - 2.6.36-0.14.rc3.git0
- Fix icebp breakpoints, patch from Frederic Weisbecker.
  (https://bugzilla.kernel.org/show_bug.cgi?id=16315#c26)

* Wed Sep 01 2010 Kyle McMartin <kyle@redhat.com> - 2.6.36-0.13.rc3.git0
- Swap back to roland's auto-updated utrace patches.

* Mon Aug 30 2010 Kyle McMartin <kyle@redhat.com> - 2.6.36-0.12.rc3.git0
- Linux 2.6.36-rc3

* Sun Aug 29 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.11.rc2.git5
- Linux 2.6.36-rc2-git5

* Wed Aug 25 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.10.rc2.git4
- Linux 2.6.36-rc2-git4

* Tue Aug 24 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.9.rc2.git3
- Linux 2.6.36-rc2-git3

* Mon Aug 23 2010 Roland McGrath <roland@redhat.com> - 2.6.36-0.8.rc2.git0
- utrace update

* Sun Aug 22 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.7.rc2.git0
- Linux 2.6.36-rc2

* Sun Aug 22 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.7.rc1.git4
- Linux 2.6.36-rc1-git4
- Fix context in linux-2.6-i386-nx-emulation.patch

* Sat Aug 21 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.6.rc1.git3
- Drop utrace patch that causes hang on boot.

* Fri Aug 20 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.5.rc1.git3
- Linux 2.6.36-rc1-git3
- Drop x86-cpu-fix-regression-in-amd-errata-checking-code.patch, now merged.

* Thu Aug 19 2010 Kyle McMartin <kmcmartin@redhat.com> - 2.6.36-0.4.rc1.git1
- Run oldnoconfig on the configs during make prep.
- Make the fix oldnoconfig patch a one liner.

* Wed Aug 18 2010 Chuck Ebbert <cebbert@redhat.com> - 2.6.36-0.3.rc1.git1
- Fix hangs on boot with some AMD processors
  (x86-cpu-fix-regression-in-amd-errata-checking-code.patch)
- Drop unused ssb_check_for_sprom.patch

* Wed Aug 18 2010 Dave Jones <davej@redhat.com>
- systemd is dependant upon autofs, so build it in instead of modular.

* Wed Aug 18 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.36-rc1-git1

* Wed Aug 18 2010 Kyle McMartin <kmcmartin@redhat.com> - 2.6.36-0.2.rc1.git0
- Link perf against libnewt for TUI support.

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com> - 2.6.36-0.1.rc1.git0
- Fix 'oldnoconfig' to do what nonint_loose_oldconfig did.

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com>
- explicitly set KERNEL_GZIP

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.36-rc1

* Tue Aug 17 2010 Kyle McMartin <kyle@redhat.com>
- Prevent scripts/setlocalversion from mucking with our version
  numbers.

* Wed Aug 04 2010 Kyle McMartin <kyle@redhat.com>
- Disable %released_kernel.
- This is properly 2.6.36-0.git1, unlike the last commit. Had to make
  a mistake sometime, I'm glad it was early.

* Wed Aug 04 2010 Kyle McMartin <kyle@redhat.com>
- Linux 2.6.35-git1, beginning of rawhide for 2.6.36...

* Sun Aug 01 2010 Dave Jones <davej@redhat.com>
- Linux 2.6.35

* Sun Aug 01 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc6-git6

* Fri Jul 30 2010 Jarod Wilson <jarod@redhat.com>
- lirc staging update
- update kworld patch to one committed upstream
- can't believe how much nicer dist-git is than dist-cvs
- patch memory leaks in mceusb and imon drivers

* Fri Jul 30 2010 Dave Jones <davej@redhat.com>
- Enable PPS (#619392)

* Thu Jul 29 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc6-git5

* Mon Jul 27 2010 Kyle McMartin <kyle@redhat.com>
- Patch from linville to only use the country code to set band limits.
  (Fixes Apple Airport base stations from limiting you from associating
   with other channels.)

* Fri Jul 23 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.35-0.56.rc6.git1
- Linux 2.6.35-rc6-git1

* Thu Jul 22 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc6

* Thu Jul 22 2010 Ben Skeggsb <bskeggs@redhat.com>
- drm-nouveau-updates: bring back, most patches *weren't* upstream yet,
  they're queued for 2.6.36.

* Wed Jul 21 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.35-0.53.rc5.git7
- Linux 2.6.35-rc5-git7

* Wed Jul 21 2010 Dave Jones <davej@redhat.com>
- Remove the %verify (no mtime) on kernel-devel's files.
  If they got modified, they should fail rpm verify.

* Wed Jul 21 2010 Dave Jones <davej@redhat.com>
- Linux 2.6.35-rc5-git6
- Removed drm-nouveau-updates.patch (upstreamed)

* Mon Jul 19 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.35-rc5-git4

* Mon Jul 19 2010 Jarod Wilson <jarod@redhat.com> 2.6.35-0.49.rc5.git2
- Fix from Kyle for input_set_key oops introduced by ir-core patches (#615707)
- Update lirc-staging patches to match what's about to be submitted upstream,
  complete with updated copy_from_user overflow check fixages

* Sun Jul 18 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.35-0.47.rc5.git2
- Linux 2.6.35-rc5-git2

* Sun Jul 18 2010 Chuck Ebbert <cebbert@redhat.com>
- lirc-staging-2.6.36-fixes.patch: Fix up buffer size checking in
  lirc code, found by CONFIG_DEBUG_STRICT_USER_COPY_CHECKS

* Sun Jul 18 2010 Hans de Goede <hdegoede@redhat.com>
- Add support for dynamic menu controls to the uvcvideo driver (#576023)

* Sun Jul 18 2010 Jarod Wilson <jarod@redhat.com> 2.6.35-0.44.rc5.git1
- Oops, minor oversight when moving lirc bits into staging resulted
  in the modules themselves not getting built. Fix that.

* Fri Jul 16 2010 Dave Jones <davej@redhat.com>
- Limit some alsa spew that the nuforce udac makes happen a lot.

* Fri Jul 16 2010 Jarod Wilson <jarod@redhat.com> 2.6.35-0.41.rc5.git1
- Pull in ir-core update from v4l/dvb staging for 2.6.36, which includes
  new in-kernel lirc_dev and ir-core mceusb driver
- Move not-yet-merged/ported lirc bits to drivers/staging/, patch to be
  sent upstream for 2.6.36 staging tree RSN

* Thu Jul 15 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.35-0.40.rc5.git1
- Replace pci-acpi-disable-aspm-if-no-osc.patch with
  updated version from F-13

* Thu Jul 15 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.35-rc5-git1

* Tue Jul 13 2010 Chuck Ebbert <cebbert@redhat.com>
- Linux 2.6.35-rc5

* Tue Jul 13 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: miscellanous fixes

* Mon Jul 12 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc4-git5

* Mon Jul 12 2010 Dave Jones <davej@redhat.com>
- Remove a bunch of x86 options from config files that get set
  automatically, and can't be overridden.

* Fri Jul  9 2010 Roland McGrath <roland@redhat.com>
- Split execshield into two patches.

* Thu Jul 08 2010 Chuck Ebbert <cebbert@redhat.com> 2.6.35-0.31.rc4.git4
- Linux 2.6.35-rc4-git4

* Thu Jul  8 2010 Roland McGrath <roland@redhat.com>
- Remove exec-shield=2 setting, some other cruft from execshield.

* Wed Jul  7 2010 Roland McGrath <roland@redhat.com> 2.6.35-0.29.rc4.git0.fc14
- Revamp perf packaging.

* Wed Jul 07 2010 Chuck Ebbert <cebbert@redhat.com>
- pci-acpi-disable-aspm-if-no-osc.patch, pci-aspm-dont-enable-too-early.patch
  PCI layer fixes for problems with hardware that doesn't support ASPM.

* Wed Jul 07 2010 Ben Skeggs <bskeggs@redhat.com>
- nouveau: bring in nouveau upstream

* Mon Jul 05 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc4

* Fri Jul 02 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc3-git7
  dropped: i915-fix-crt-hotplug-regression.patch (upstream)
  dropped: drm-i915-fix-edp-panels.patch (upstream)

* Fri Jul 02 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc3-git6

* Thu Jul 01 2010 Dave Jones <davej@redhat.com>
- Add a patch to debug an infinite loop warning from acpi.

* Thu Jul 01 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc3-git5

* Thu Jul 01 2010 Chuck Ebbert <cebbert@redhat.com>
- Copy fix for BZ#220892 from F-13.

* Wed Jun 30 2010 Kyle McMartin <kyle@redhat.com> 2.6.35-0.19.rc3.git4
- 2.6.35-rc3-git4

* Tue Jun 29 2010 Chuck Ebbert <cebbert@redhat.com>
- Disable Intel Moorestown support -- it breaks PC keyboard controllers.

* Tue Jun 29 2010 Dave Jones <davej@redhat.com>
- Building external modules requires perl. (#608525)

* Tue Jun 29 2010 Kyle McMartin <kyle@redhat.com> 2.6.35-0.15.rc3.git3
- 2.6.35-rc3-git3
- i915-fix-crt-hotplug-regression.patch: attempt to solve the gm45 hotplug
  irq storm.

* Mon Jun 28 2010 Chuck Ebbert <cebbert@redhat.com>
- ppc64: enable active memory sharing and DLPAR memory remove (#607175)

* Mon Jun 28 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc3-git2

* Mon Jun 28 2010 Dave Jones <davej@redhat.com>
- 2.6.35-rc3-git1

* Mon Jun 28 2010 Dave Airlie <airlied@redhat.com>
- drm-i915-fix-edp-panels.patch: update to newer version

* Fri Jun 25 2010 Kyle McMartin <kyle@redhat.com>
- drm-i915-fix-edp-panels.patch: copy from rawhide.

* Wed Jun 23 2010 Eric Sandeen <sandeen@redhat.com>
- Fix ext4 freeze deadlock (#607245)

* Wed Jun 23 2010 Kyle McMartin <kyle@redhat.com>
- Override generic's CONFIG_HZ_1000 on s390.

* Tue Jun 22 2010 Dave Jones <davej@redhat.com>
- Fix localhost networking.

* Tue Jun 22 2010 Kyle McMartin <kyle@redhat.com> 2.6.35-0.1.rc3.git0
- Putting the raw back into rawhide... Yeehaw.
- 2.6.35-rc3
- Drop a tonne of patches that were merged upstream, or were backports.
- Rebase execshield, utrace.
- Fix up a bunch of rejects, build failures.
- Fix up lirc to build with strict copy_from_user checking.

* Mon Jun 21 2010 Dave Jones <davej@redhat.com>
- Disable workaround for obscure SMP pentium pro errata.
  I miss the 1990s too, but it's time to move on.
  If anyone actually needs this it would be better done using
  the apply_alternatives infrastructure.

* Mon Jun 21 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-45
- drm-revert-drm-fbdev-rework-output-polling-to-be-back-in-core.patch
  Revert eb1f8e4f, bisected by Nicolas Kaiser. Thanks! (rhbz#599190)
  (If this works, will try to root-cause.)
- rebase previous patch on top of above reversion

* Mon Jun 21 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-44
- revert-drm-kms-toggle-poll-around-switcheroo.patch (rhbz#599190)

* Thu Jun 17 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-43
- Suck in patch from Dave Miller in 2.6.35 to add async hash testing,
  hopefully fixes error from previous commit. (But making it modular
  is still a good idea.)

* Thu Jun 17 2010 Kyle McMartin <kyle@redhat.com>
- make ghash-clmulni modular to get rid of early boot noise (rhbz#586954)
  (not a /fix/ but it should at least quiet boot down a bit if you have
   the cpu support)

* Wed Jun 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-40
- Snag some more DRM commits into drm-next.patch that I missed the first
  time.
- Fix up radeon_pm toggle to work with the upstream code.

* Tue Jun 15 2010 Prarit Bhargava <prarit@redhat.com>
- Turn off CONFIG_I2O on x86.
  It is broken on 64-bit address spaces (i686/PAE, x86_64), and frankly, I'm
  having trouble finding anyone who actually uses it.

* Tue Jun 15 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-38
- Fix build by nuking superfluous "%{expand" which was missing a
  trailing '}'. You may now reward me with an array of alcoholic
  beverages, I so richly deserve for spending roughly a full
  day staring at the diff of the spec.

* Mon Jun 14 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-37
- btrfs ACL fixes from CVE-2010-2071.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-36
- remunge and reapply hdpvr-ir-enable

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-35
- mac80211/iwlwifi fix connections to some APs (rhbz#558002)
  patches from sgruszka@.

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-34
- Provide a knob to enable radeon_pm to allow users to test
  that functionality. Add radeon.pm=1 to your kernel cmdline
  in order to enable it. (It still defaults to off though.)

* Sun Jun 13 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-33
- Update drm-next to include fixes since 2.6.35-rc1.

* Fri Jun 11 2010 Justin M. Forbes <jforbes@redhat.com>
- Disable xsave for so that kernel will boot on ancient EC2 hosts.

* Wed Jun 09 2010 John W. Linville <linville@redhat.com>
- Disable rt20xx and rt35xx chipset support in rt2800 drivers (#570869)

* Wed Jun 09 2010 David Woodhouse <David.Woodhouse@intel.com>
- Include PHY modules in modules.networking (#602155)

* Tue Jun 08 2010 Dave Jones <davej@redhat.com>
- Remove useless -kdump kernel support

* Tue Jun 08 2010 Dave Jones <davej@redhat.com>
- Remove ia64 ata quirk which had no explanation, and still
  isn't upstream. No-one cares.

* Tue Jun 08 2010 Dave Jones <davej@redhat.com>
- Drop linux-2.6-vio-modalias.patch
  Two years should have been long enough to get upstream if this is important.

* Tue Jun 08 2010 Dave Jones <davej@redhat.com>
- Remove crufty Xen remnants from specfile.

* Tue Jun 08 2010 Dave Jones <davej@redhat.com>
- Remove mkinitrd ifdefs. Dracut or GTFO.

* Thu Jun 03 2010 Kyle McMartin <kyle@redhat.com>
- Build kernel headers on s390.

* Wed Jun 02 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-20
- Disable doc_build_fail because xmlto et al. are crud.

* Wed Jun 02 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-19
- Enable -debug flavour builds, until we branch for 2.6.35-rcX.

* Wed Jun 02 2010 Kyle McMartin <kyle@redhat.com>
- revert writeback fixes for now, there appear to be dragons
  lurking there still.

* Tue Jun 01 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-18
- fix mismerge in i915_gem.c, drm_gem_object_alloc is now
  i915_gem_alloc_object.
- add a hunk to rcu_read{,un}lock in sched_fair too.

* Tue Jun 01 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-17
- backport writeback fixes from Jens until stable@ picks them up.

* Tue Jun 01 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-16
- quiet-prove_RCU-in-cgroups.patch: shut RCU lockdep up
  as in 8b08ca52f5942c21564bbb90ccfb61053f2c26a1.

* Tue Jun 01 2010 Kyle McMartin <kyle@redhat.com>
- disable radeon_pm for now.

* Mon May 31 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-14
- re-add drm-next.patch, should be in sync with 2.6.35 and what
  was backported to Fedora 13.
- drop patches merged in drm-next to 2.6.35
- rebase relevant iwl fixes on top of 2.6.34 from the ones committed
  to F-13 by linville.

* Wed May 26 2010 Adam Jackson <ajax@redhat.com>
- config-generic: Stop building i830.ko

* Wed May 26 2010 Kyle McMartin <kyle@redhat.com>
- iwlwifi-recover_from_tx_stall.patch: copy from F-13.

* Fri May 21 2010 Roland McGrath <roland@redhat.com> 2.6.34-11
- utrace update

* Fri May 21 2010 Dave Jones <davej@redhat.com>
- Update the SELinux mprotect patch with a newer version from Stephen

* Fri May 21 2010 Roland McGrath <roland@redhat.com>
- perf requires libdw now, not libdwarf

* Fri May 21 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-6
- Fixups for virt_console from Amit Shah, thanks!

* Thu May 20 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-5
- disable intel sdvo fixes until dependent code is backported.

* Thu May 20 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-4
- resync a lot of stuff with F-13...
- linux-2.6-acpi-video-export-edid.patch: rebase & copy from F-13
- acpi-ec-add-delay-before-write.patch: copy from F-13
- ... and a whole lot more that I can't be bothered typing.

* Mon May 17 2010 Matthew Garrett <mjg@redhat.com>
- thinkpad-acpi-fix-backlight.patch: Fix backlight support on some recent
   Thinkpads

* Sun May 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-2
- Disable strict copy_from_user checking until lirc is fixed.

* Sun May 16 2010 Kyle McMartin <kyle@redhat.com> 2.6.34-1
- Linux 2.6.34

* Sun May 16 2010 Kyle McMartin <kyle@redhat.com>
- Trimmed changelog, see CVS.

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
