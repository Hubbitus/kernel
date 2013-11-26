# We have to override the new %%install behavior because, well... the kernel is special.
%global __spec_install_pre %{___build_pre}

Summary: The Linux kernel

# % define buildid .local

# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 1

%define rpmversion 3.10.0
%define pkgrelease 54.0.1.el7

%define pkg_release %{pkgrelease}%{?buildid}

# The kernel tarball/base version
%define rheltarball %{rpmversion}-%{pkgrelease}

# What parts do we want to build?  We must build at least one kernel.
# These are the kernels that are built IF the architecture allows it.
# All should default to 1 (enabled) and be flipped to 0 (disabled)
# by later arch-specific checks.

# The following build options are enabled by default.
# Use either --without <opt> in your rpmbuild command or force values
# to 0 in here to disable them.
#
# kernel
%define with_default   %{?_without_default:   0} %{?!_without_default:   1}
# kernel-debug
%define with_debug     %{?_without_debug:     0} %{?!_without_debug:     1}
# kernel-doc
%define with_doc       %{?_without_doc:       0} %{?!_without_doc:       1}
# kernel-headers
%define with_headers   %{?_without_headers:   0} %{?!_without_headers:   1}
# perf
%define with_perf      %{?_without_perf:      0} %{?!_without_perf:      1}
# tools
%define with_tools     %{?_without_tools:     0} %{?!_without_tools:     1}
# kernel-debuginfo
%define with_debuginfo %{?_without_debuginfo: 0} %{?!_without_debuginfo: 1}
# kernel-kdump (only for s390x)
%define with_kdump     %{?_without_kdump:     0} %{?!_without_kdump:     0}
# kernel-bootwrapper (for creating zImages from kernel + initrd)
%define with_bootwrapper %{?_without_bootwrapper: 0} %{?!_without_bootwrapper: 0}
# kernel-abi-whitelists
%define with_kernel_abi_whitelists %{?_with_kernel_abi_whitelists: 0} %{?!_with_kernel_abi_whitelists: 1}

# Build the kernel-doc package, but don't fail the build if it botches.
# Here "true" means "continue" and "false" means "fail the build".
%if 0%{?released_kernel}
%define doc_build_fail false
%else
%define doc_build_fail true
%endif

%define rawhide_skip_docs 0
%if 0%{?rawhide_skip_docs}
%define with_doc 0
%define doc_build_fail true
%endif

# Additional options for user-friendly one-off kernel building:
#
# Only build the base kernel (--with baseonly):
%define with_baseonly  %{?_with_baseonly:     1} %{?!_with_baseonly:     0}
# Only build the debug kernel (--with dbgonly):
%define with_dbgonly   %{?_with_dbgonly:      1} %{?!_with_dbgonly:      0}

# Control whether we perform a compat. check against published ABI.
%define with_kabichk   %{?_without_kabichk:   0} %{?!_without_kabichk:   1}

# should we do C=1 builds with sparse
%define with_sparse    %{?_with_sparse:       1} %{?!_with_sparse:       0}

# Cross compile requested?
%define with_cross    %{?_with_cross:         1} %{?!_with_cross:        0}

# Set debugbuildsenabled to 1 for production (build separate debug kernels)
#  and 0 for rawhide (all kernels are debug kernels).
# See also 'make debug' and 'make release'.
%define debugbuildsenabled 1

%define make_target bzImage

%define KVERREL %{version}-%{release}.%{_target_cpu}
%define hdrarch %_target_cpu
%define asmarch %_target_cpu

%if !%{debugbuildsenabled}
%define with_debug 0
%endif

%if !%{with_debuginfo}
%define _enable_debug_packages 0
%endif
%define debuginfodir /usr/lib/debug

# if requested, only build base kernel
%if %{with_baseonly}
%define with_debug 0
%define with_kdump 0
%endif

# if requested, only build debug kernel
%if %{with_dbgonly}
%define with_default 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%endif

# These arches install vdso/ directories.
%define vdso_arches %{all_x86} x86_64 ppc ppc64 s390 s390x

# Overrides for generic default options

# only build kernel-debug on x86_64, s390x, ppc64
%ifnarch x86_64 s390x ppc64
%define with_debug 0
%endif

# only package docs noarch
%ifnarch noarch
%define with_doc 0
%define with_kernel_abi_whitelists 0
%endif

# don't build noarch kernels or headers (duh)
%ifarch noarch
%define with_default 0
%define with_headers 0
%define with_tools 0
%define with_perf 0
%define all_arch_configs kernel-%{version}-*.config
%endif

# sparse blows up on ppc64
%ifarch ppc64 ppc
%define with_sparse 0
%endif

# Per-arch tweaks

%ifarch i686
%define asmarch x86
%define hdrarch i386
%endif

%ifarch x86_64
%define asmarch x86
%define all_arch_configs kernel-%{version}-x86_64*.config
%define image_install_path boot
%define kernel_image arch/x86/boot/bzImage
%endif

%ifarch ppc
%define asmarch powerpc
%define hdrarch powerpc
%endif

%ifarch ppc64
%define asmarch powerpc
%define hdrarch powerpc
%define all_arch_configs kernel-%{version}-ppc64*.config
%define image_install_path boot
%define make_target vmlinux
%define kernel_image vmlinux
%define kernel_image_elf 1
%define with_bootwrapper 1
%endif

%ifarch s390x
%define asmarch s390
%define hdrarch s390
%define all_arch_configs kernel-%{version}-s390x*.config
%define image_install_path boot
%define make_target image
%define kernel_image arch/s390/boot/image
%define with_tools 0
%define with_kdump 1
%endif

# Should make listnewconfig fail if there's config options
# printed out?
%define listnewconfig_fail 1

# To temporarily exclude an architecture from being built, add it to
# %%nobuildarches. Do _NOT_ use the ExclusiveArch: line, because if we
# don't build kernel-headers then the new build system will no longer let
# us use the previous build of that package -- it'll just be completely AWOL.
# Which is a BadThing(tm).

# We only build kernel-headers on the following...
%define nobuildarches i686 s390 ppc

%ifarch %nobuildarches
%define with_default 0
%define with_debuginfo 0
%define with_kdump 0
%define with_tools 0
%define with_perf 0
%define _enable_debug_packages 0
%endif

# Architectures we build tools/cpupower on
%define cpupowerarchs x86_64 ppc64

#
# Three sets of minimum package version requirements in the form of Conflicts:
# to versions below the minimum
#

#
# First the general kernel 2.6 required versions as per
# Documentation/Changes
#
%define kernel_dot_org_conflicts  ppp < 2.4.3-3, isdn4k-utils < 3.2-32, nfs-utils < 1.0.7-12, e2fsprogs < 1.37-4, util-linux < 2.12, jfsutils < 1.1.7-2, reiserfs-utils < 3.6.19-2, xfsprogs < 2.6.13-4, procps < 3.2.5-6.3, oprofile < 0.9.1-2, device-mapper-libs < 1.02.63-2, mdadm < 3.2.1-5

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
# Packages that need to be installed before the kernel is, because the %%post
# scripts use them.
#
%define kernel_prereq  fileutils, module-init-tools >= 3.16-2, initscripts >= 8.11.1-1, grubby >= 8.28-2
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
Requires(pre): linux-firmware >= 20100806-2\
Requires(post): %{_sbindir}/new-kernel-pkg\
Requires(preun): %{_sbindir}/new-kernel-pkg\
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
ExclusiveArch: noarch i686 x86_64 ppc ppc64 s390 s390x
ExclusiveOS: Linux

%kernel_reqprovconf

#
# List the packages used during the kernel build
#
BuildRequires: module-init-tools, patch >= 2.5.4, bash >= 2.03, sh-utils, tar
BuildRequires: xz, findutils, gzip, m4, perl, make >= 3.78, diffutils, gawk
BuildRequires: gcc >= 3.4.2, binutils >= 2.12, redhat-rpm-config >= 9.1.0-55
BuildRequires: hostname, net-tools, bc
BuildRequires: xmlto, asciidoc
BuildRequires: openssl
BuildRequires: hmaccalc
%ifarch x86_64
BuildRequires: pesign >= 0.109-4
%endif
%if %{with_sparse}
BuildRequires: sparse >= 0.4.1
%endif
%if %{with_perf}
BuildRequires: elfutils-devel zlib-devel binutils-devel newt-devel python-devel perl(ExtUtils::Embed) bison
BuildRequires: audit-libs-devel
%endif
%if %{with_tools}
BuildRequires: pciutils-devel gettext
%endif
%if %{with_debuginfo}
# Fancy new debuginfo generation introduced in Fedora 8/RHEL 6.
# The -r flag to find-debuginfo.sh invokes eu-strip --reloc-debug-sections
# which reduces the number of relocations in kernel module .ko.debug files and
# was introduced with rpm 4.9 and elfutils 0.153.
BuildRequires: rpm-build >= 4.9.0-1, elfutils >= elfutils-0.153-1
%define debuginfo_args --strict-build-id -r
%endif
%ifarch s390x
# required for zfcpdump
BuildRequires: glibc-static
%endif

#cross compile make
%if %{with_cross}

%if "%{_target_cpu}" == "s390x"
%define cross_opts CROSS_COMPILE=s390x-linux-gnu-
%endif
%if "%{_target_cpu}" == "ppc64"
%define cross_opts CROSS_COMPILE=powerpc64-linux-gnu-
%endif

%endif

Source0: linux-%{rpmversion}-%{pkgrelease}.tar.xz

Source1: Makefile.common

Source10: sign-modules
%define modsign_cmd %{SOURCE10}
Source11: x509.genkey
Source12: extra_certificates
Source13: redhatsecurebootca2.cer
Source14: redhatsecureboot003.cer

%if %{with_kabichk}
Source18: check-kabi

Source20: Module.kabi_x86_64
Source21: Module.kabi_ppc64
Source22: Module.kabi_s390x

Source23: kabi_whitelist_ppc64
Source24: kabi_whitelist_s390x
Source25: kabi_whitelist_x86_64
%endif

Source50: kernel-%{version}-x86_64.config
Source51: kernel-%{version}-x86_64-debug.config

Source60: kernel-%{version}-ppc64.config
Source61: kernel-%{version}-ppc64-debug.config

Source70: kernel-%{version}-s390x.config
Source71: kernel-%{version}-s390x-debug.config
Source72: kernel-%{version}-s390x-kdump.config

# Sources for kernel-tools
Source2000: cpupower.service
Source2001: cpupower.config

# empty final patch to facilitate testing of kernel patches
Patch999999: linux-kernel-test.patch

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
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/perf(\.debug)?|.*%%{_libexecdir}/perf-core/.*|XXX' -o perf-debuginfo.list}

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
%{expand:%%global debuginfo_args %{?debuginfo_args} -p '.*%%{_bindir}/centrino-decode(\.debug)?|.*%%{_bindir}/powernow-k8-decode(\.debug)?|.*%%{_bindir}/cpupower(\.debug)?|.*%%{_libdir}/libcpupower.*|.*%%{_libdir}/libcpupower.*|.*%%{_bindir}/turbostat(\.debug)?|.*%%{_bindir}/x86_energy_perf_policy(\.debug)?|XXX' -o kernel-tools-debuginfo.list}

%endif # with_tools

%package -n kernel-abi-whitelists
Summary: The Red Hat Enterprise Linux kernel ABI symbol whitelists
Group: System Environment/Kernel
AutoReqProv: no
%description -n kernel-abi-whitelists
The kABI package contains information pertaining to the Red Hat Enterprise
Linux kernel ABI, including lists of kernel symbols that are needed by
external Linux kernel modules, and a yum plugin to aid enforcement.

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

%define variant_summary A minimal Linux kernel compiled for crash dumps
%kernel_variant_package kdump
%description kdump
This package includes a kdump version of the Linux kernel. It is
required only on machines which will use the kexec-based kernel crash dump
mechanism.

%prep
# do a few sanity-checks for --with *only builds
%if %{with_baseonly}
%if !%{with_default}
echo "Cannot build --with baseonly, default kernel build is disabled"
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
  if ! grep -E "^Patch[0-9]+: $patch\$" %{_specdir}/${RPM_PACKAGE_NAME%%%%%{?variant}}.spec ; then
    if [ "${patch:0:8}" != "patch-3." ] ; then
      echo "ERROR: Patch  $patch  not listed as a source patch in specfile"
      exit 1
    fi
  fi 2>/dev/null
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

if [ ! -d kernel-%{rheltarball}/vanilla-%{rheltarball}/ ]; then
	rm -f pax_global_header;
%setup -q -n kernel-%{rheltarball} -c
	mv linux-%{rheltarball} vanilla-%{rheltarball};
else
	cd kernel-%{rheltarball}/;
fi

if [ -d linux-%{KVERREL} ]; then
	# Just in case we ctrl-c'd a prep already
	rm -rf deleteme.%{_target_cpu}
	# Move away the stale away, and delete in background.
	mv linux-%{KVERREL} deleteme.%{_target_cpu}
	rm -rf deleteme.%{_target_cpu} &
fi

cp -rl vanilla-%{rheltarball} linux-%{KVERREL}
cd linux-%{KVERREL}

# Drop some necessary files from the source dir into the buildroot
cp $RPM_SOURCE_DIR/kernel-*.config .

ApplyOptionalPatch linux-kernel-test.patch

# Any further pre-build tree manipulations happen here.

chmod +x scripts/checkpatch.pl

# This Prevents scripts/setlocalversion from mucking with our version numbers.
touch .scmversion

# only deal with configs if we are going to build for the arch
%ifnarch %nobuildarches

if [ -L configs ]; then
	rm -f configs
	mkdir configs
fi

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
  make %{?cross_opts} ARCH=$Arch listnewconfig | grep -E '^CONFIG_' >.newoptions || true
%if %{listnewconfig_fail}
  if [ -s .newoptions ]; then
    cat .newoptions
    exit 1
  fi
%endif
  rm -f .newoptions
  make %{?cross_opts} ARCH=$Arch oldnoconfig
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

    %if 0%{?stable_update}
    # make sure SUBLEVEL is incremented on a stable release.  Sigh 3.x.
    perl -p -i -e "s/^SUBLEVEL.*/SUBLEVEL = %{?stablerev}/" Makefile
    %endif

    # make sure EXTRAVERSION says what we want it to say
    perl -p -i -e "s/^EXTRAVERSION.*/EXTRAVERSION = -%{release}.%{_target_cpu}${Flavour:+.${Flavour}}/" Makefile

    # if pre-rc1 devel kernel, must fix up PATCHLEVEL for our versioning scheme
    %if !0%{?rcrev}
    %if 0%{?gitrev}
    perl -p -i -e 's/^PATCHLEVEL.*/PATCHLEVEL = %{upstream_sublevel}/' Makefile
    %endif
    %endif

    # and now to start the build process

    make %{?cross_opts} -s mrproper

    cp %{SOURCE11} .	# x509.genkey
    cp %{SOURCE12} .	# extra_certificates

    cp configs/$Config .config

    Arch=`head -1 .config | cut -b 3-`
    echo USING ARCH=$Arch

%ifarch s390x
    if [ "$Flavour" == "kdump" ]; then
        pushd arch/s390/boot
        gcc -static -o zfcpdump zfcpdump.c
        popd
    fi
%endif

    make -s %{?cross_opts} ARCH=$Arch oldnoconfig >/dev/null
    make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} $MakeTarget %{?sparse_mflags}

    if [ "$Flavour" != "kdump" ]; then
        make -s %{?cross_opts} ARCH=$Arch V=1 %{?_smp_mflags} modules %{?sparse_mflags} || exit 1
    fi

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
# EFI SecureBoot signing, x86_64-only
%ifarch x86_64
    %pesign -s -i $KernelImage -o $KernelImage.signed -a %{SOURCE13} -c %{SOURCE14} -n redhatsecureboot003
    mv $KernelImage.signed $KernelImage
%endif
    $CopyKernel $KernelImage \
    		$RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    chmod 755 $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer

    # hmac sign the kernel for FIPS
    echo "Creating hmac file: $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac"
    ls -l $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer
    sha512hmac $RPM_BUILD_ROOT/%{image_install_path}/$InstallName-$KernelVer | sed -e "s,$RPM_BUILD_ROOT,," > $RPM_BUILD_ROOT/%{image_install_path}/.vmlinuz-$KernelVer.hmac;

    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer
    mkdir -p $RPM_BUILD_ROOT/lib/modules/$KernelVer/kernel
    if [ "$Flavour" != "kdump" ]; then
        # Override $(mod-fw) because we don't want it to install any firmware
        # we'll get it from the linux-firmware package and we don't want conflicts
        make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT modules_install KERNELRELEASE=$KernelVer mod-fw=
    fi
%ifarch %{vdso_arches}
    make -s %{?cross_opts} ARCH=$Arch INSTALL_MOD_PATH=$RPM_BUILD_ROOT vdso_install KERNELRELEASE=$KernelVer
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

%if %{with_kabichk}
    # create the kABI metadata for use in packaging
    # NOTENOTE: the name symvers is used by the rpm backend
    # NOTENOTE: to discover and run the /usr/lib/rpm/fileattrs/kabi.attr
    # NOTENOTE: script which dynamically adds exported kernel symbol
    # NOTENOTE: checksums to the rpm metadata provides list.
    # NOTENOTE: if you change the symvers name, update the backend too
    echo "**** GENERATING kernel ABI metadata ****"
    gzip -c9 < Module.symvers > $RPM_BUILD_ROOT/boot/symvers-$KernelVer.gz

    echo "**** kABI checking is enabled in kernel SPEC file. ****"
    chmod 0755 $RPM_SOURCE_DIR/check-kabi
    if [ -e $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour ]; then
        cp $RPM_SOURCE_DIR/Module.kabi_%{_target_cpu}$Flavour $RPM_BUILD_ROOT/Module.kabi
        $RPM_SOURCE_DIR/check-kabi -k $RPM_BUILD_ROOT/Module.kabi -s Module.symvers || exit 1
        rm $RPM_BUILD_ROOT/Module.kabi # for now, don't keep it around.
    else
        echo "**** NOTE: Cannot find reference Module.kabi file. ****"
    fi
%endif %{with_kabichk}

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
%ifarch ppc64
    cp -a --parents arch/powerpc/lib/crtsavres.[So] $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
%endif
    if [ -d arch/%{asmarch}/include ]; then
      cp -a --parents arch/%{asmarch}/include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/
    fi
    cp -a include $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include

    # Make sure the Makefile and version.h have a matching timestamp so that
    # external modules can be built
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/Makefile $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/uapi/linux/version.h
    touch -r $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/.config $RPM_BUILD_ROOT/lib/modules/$KernelVer/build/include/generated/autoconf.h
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
    			 'register_netdev|ieee80211_register_hw|usbnet_probe|phy_driver_register|rt2x00(pci|usb)_probe|register_netdevice'
    collect_modules_list block \
    			 'ata_scsi_ioctl|scsi_add_host|scsi_add_host_with_dma|blk_alloc_queue|blk_init_queue|register_mtd_blktrans|scsi_esp_register|scsi_register_device_handler|blk_queue_physical_block_size' 'pktcdvd.ko|dm-mod.ko'
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

    grep -E -v \
    	  'GPL( v2)?$|Dual BSD/GPL$|Dual MPL/GPL$|GPL and additional rights$' \
	  modinfo && exit 1

    rm -f modinfo modnames

    # Save off the .tmp_versions/ directory.  We'll use it in the
    # __debug_install_post macro below to sign the right things
    # Also save the signing keys so we actually sign the modules with the
    # right key.
    cp -r .tmp_versions .tmp_versions.sign${Flavour:+.${Flavour}}
    cp signing_key.priv signing_key.priv.sign${Flavour:+.${Flavour}}
    cp signing_key.x509 signing_key.x509.sign${Flavour:+.${Flavour}}

    # remove files that will be auto generated by depmod at rpm -i time
    for i in alias alias.bin builtin.bin ccwmap dep dep.bin ieee1394map inputmap isapnpmap ofmap pcimap seriomap symbols symbols.bin usbmap
    do
      rm -f $RPM_BUILD_ROOT/lib/modules/$KernelVer/modules.$i
    done

    # Move the devel headers out of the root file system
    mkdir -p $RPM_BUILD_ROOT/usr/src/kernels
    mv $RPM_BUILD_ROOT/lib/modules/$KernelVer/build $RPM_BUILD_ROOT/$DevelDir
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

%if %{with_default}
BuildKernel %make_target %kernel_image
%endif

%if %{with_debug}
BuildKernel %make_target %kernel_image debug
%endif

%if %{with_kdump}
BuildKernel %make_target %kernel_image kdump
%endif

%global perf_make \
  make %{?_smp_mflags} -C tools/perf -s V=1 WERROR=0 NO_LIBUNWIND=1 HAVE_CPLUS_DEMANGLE=1 NO_GTK2=1 NO_LIBNUMA=1 NO_STRLCPY=1 prefix=%{_prefix}
%if %{with_perf}
# perf
%{perf_make} all
%{perf_make} man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
# cpupower
# make sure version-gen.sh is executable.
chmod +x tools/power/cpupower/utils/version-gen.sh
make %{?cross_opts} %{?_smp_mflags} -C tools/power/cpupower CPUFREQ_BENCH=false
%ifarch x86_64
    pushd tools/power/cpupower/debug/x86_64
    make %{?_smp_mflags} centrino-decode powernow-k8-decode
    popd
%endif
%ifarch x86_64
   pushd tools/power/x86/x86_energy_perf_policy/
   make
   popd
   pushd tools/power/x86/turbostat
   make
   popd
%endif #turbostat/x86_energy_perf_policy
%endif
%endif

%if %{with_doc}
# Make the HTML and man pages.
make htmldocs mandocs || %{doc_build_fail}

# sometimes non-world-readable files sneak into the kernel source tree
chmod -R a=rX Documentation
find Documentation -type d | xargs chmod u+w
%endif

# In the modsign case, we do 3 things.  1) We check the "flavour" and hard
# code the value in the following invocations.  This is somewhat sub-optimal
# but we're doing this inside of an RPM macro and it isn't as easy as it
# could be because of that.  2) We restore the .tmp_versions/ directory from
# the one we saved off in BuildKernel above.  This is to make sure we're
# signing the modules we actually built/installed in that flavour.  3) We
# grab the arch and invoke 'make modules_sign' and the mod-extra-sign.sh
# commands to actually sign the modules.
#
# We have to do all of those things _after_ find-debuginfo runs, otherwise
# that will strip the signature off of the modules.
#
# Finally, pick a module at random and check that it's signed and fail the build
# if it isn't.

%define __modsign_install_post \
  if [ "%{with_debug}" -ne "0" ]; then \
    Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}-debug.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign.debug .tmp_versions \
    mv signing_key.priv.sign.debug signing_key.priv \
    mv signing_key.x509.sign.debug signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVERREL}.debug || exit 1 \
  fi \
    if [ "%{with_default}" -ne "0" ]; then \
    Arch=`head -1 configs/kernel-%{version}-%{_target_cpu}.config | cut -b 3-` \
    rm -rf .tmp_versions \
    mv .tmp_versions.sign .tmp_versions \
    mv signing_key.priv.sign signing_key.priv \
    mv signing_key.x509.sign signing_key.x509 \
    %{modsign_cmd} $RPM_BUILD_ROOT/lib/modules/%{KVERREL} || exit 1 \
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

# We have to do the headers install before the tools install because the
# kernel headers_install will remove any header files in /usr/include that
# it doesn't install itself.

%if %{with_headers}
# Install kernel headers
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_install

# Do headers_check but don't die if it fails.
make %{?cross_opts} ARCH=%{hdrarch} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr headers_check \
     > hdrwarnings.txt || :
if grep -q exist hdrwarnings.txt; then
   sed s:^$RPM_BUILD_ROOT/usr/include/:: hdrwarnings.txt
   # Temporarily cause a build failure if header inconsistencies.
   # exit 1
fi

find $RPM_BUILD_ROOT/usr/include \
     \( -name .install -o -name .check -o \
     	-name ..install.cmd -o -name ..check.cmd \) | xargs rm -f

%endif

%if %{with_kernel_abi_whitelists}
# kabi directory
INSTALL_KABI_PATH=$RPM_BUILD_ROOT/lib/modules/kabi-rhel70
mkdir -p $INSTALL_KABI_PATH

# install kabi whitelists
cp %{SOURCE23} %{SOURCE24} %{SOURCE25} $INSTALL_KABI_PATH
%endif  # with_kernel_abi_whitelists

%if %{with_perf}
# perf tool binary and supporting scripts/binaries
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install

# perf-python extension
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-python_ext

# perf man pages (note: implicit rpm magic compresses them later)
%{perf_make} DESTDIR=$RPM_BUILD_ROOT install-man || %{doc_build_fail}
%endif

%if %{with_tools}
%ifarch %{cpupowerarchs}
make -C tools/power/cpupower DESTDIR=$RPM_BUILD_ROOT libdir=%{_libdir} mandir=%{_mandir} CPUFREQ_BENCH=false install
rm -f %{buildroot}%{_libdir}/*.{a,la}
%find_lang cpupower
mv cpupower.lang ../
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
%ifarch %{ix86} x86_64
   mkdir -p %{buildroot}%{_mandir}/man8
   pushd tools/power/x86/x86_energy_perf_policy
   make DESTDIR=%{buildroot} install
   popd
   pushd tools/power/x86/turbostat
   make DESTDIR=%{buildroot} install
   popd
%endif #turbostat/x86_energy_perf_policy
%endif

%endif

%if %{with_bootwrapper}
make %{?cross_opts} DESTDIR=$RPM_BUILD_ROOT bootwrapper_install WRAPPER_OBJDIR=%{_libdir}/kernel-wrapper WRAPPER_DTSDIR=%{_libdir}/kernel-wrapper/dts
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
%{_sbindir}/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --mkinitrd --dracut --depmod --update %{KVERREL}%{?-v:.%{-v*}} || exit $?\
%{_sbindir}/new-kernel-pkg --package kernel%{?1:-%{1}} --rpmposttrans %{KVERREL}%{?1:.%{1}} || exit $?\
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
if [ `uname -i` == "x86_64" ] &&\
   [ -f /etc/sysconfig/kernel ]; then\
  /bin/sed -r -i -e 's/^DEFAULTKERNEL=%{-r*}$/DEFAULTKERNEL=kernel%{?-v:-%{-v*}}/' /etc/sysconfig/kernel || exit $?\
fi}\
%{expand:\
%{_sbindir}/new-kernel-pkg --package kernel%{?-v:-%{-v*}} --install %{KVERREL}%{?-v:.%{-v*}} || exit $?\
}\
%{nil}

#
# This macro defines a %%preun script for a kernel package.
#	%%kernel_variant_preun <subpackage>
#
%define kernel_variant_preun() \
%{expand:%%preun %{?1}}\
%{_sbindir}/new-kernel-pkg --rminitrd --rmmoddep --remove %{KVERREL}%{?1:.%{1}} || exit $?\
%{nil}

%kernel_variant_preun
%kernel_variant_post 

%kernel_variant_preun debug
%kernel_variant_post -v debug

%ifarch s390x
%postun kdump
    # Create softlink to latest remaining kdump kernel.
    # If no more kdump kernel is available, remove softlink.
    if [ "$(readlink /boot/zfcpdump)" == "/boot/vmlinuz-%{KVERREL}.kdump" ]
    then
        vmlinuz_next=$(ls /boot/vmlinuz-*.kdump 2> /dev/null | sort | tail -n1)
        if [ $vmlinuz_next ]
        then
            ln -sf $vmlinuz_next /boot/zfcpdump
        else
            rm -f /boot/zfcpdump
        fi
    fi

%post kdump
    ln -sf /boot/vmlinuz-%{KVERREL}.kdump /boot/zfcpdump
%endif # s390x

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

# only some architecture builds need kernel-doc
%if %{with_doc}
%files doc
%defattr(-,root,root)
%{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation/*
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}/Documentation
%dir %{_datadir}/doc/kernel-doc-%{rpmversion}
%{_datadir}/man/man9/*
%endif

%if %{with_kernel_abi_whitelists}
%files -n kernel-abi-whitelists
%defattr(-,root,root,-)
/lib/modules/kabi-*
%endif

%if %{with_perf}
%files -n perf
%defattr(-,root,root)
%{_bindir}/perf
%dir %{_libexecdir}/perf-core
%{_libexecdir}/perf-core/*
%{_mandir}/man[1-8]/perf*
%{_sysconfdir}/bash_completion.d/perf

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
%ifarch x86_64
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
%endif

%if %{with_debuginfo}
%files -f kernel-tools-debuginfo.list -n kernel-tools-debuginfo
%defattr(-,root,root)
%endif

%ifarch %{cpupowerarchs}
%files -n kernel-tools-libs
%defattr(-,root,root)
%{_libdir}/libcpupower.so.0
%{_libdir}/libcpupower.so.0.0.0

%files -n kernel-tools-libs-devel
%defattr(-,root,root)
%{_libdir}/libcpupower.so
%{_includedir}/cpufreq.h
%endif

%endif # with_tools

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
%{expand:%%files %{?2}}\
%defattr(-,root,root)\
/%{image_install_path}/%{?-k:%{-k*}}%{!?-k:vmlinuz}-%{KVERREL}%{?2:.%{2}}\
/%{image_install_path}/.vmlinuz-%{KVERREL}%{?2:.%{2}}.hmac \
%attr(600,root,root) /boot/System.map-%{KVERREL}%{?2:.%{2}}\
/boot/symvers-%{KVERREL}%{?2:.%{2}}.gz\
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
%{expand:%%files -f debuginfo%{?2}.list %{?2:%{2}-}debuginfo}\
%defattr(-,root,root)\
%endif\
%endif\
%endif\
%{nil}

%kernel_variant_files %{with_default}
%kernel_variant_files %{with_debug} debug
%kernel_variant_files %{with_kdump} kdump

%changelog
* Tue Nov 26 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-54.0.1.el7]
- [acpi] Correct faulty check of Secure Level in acpi_os_get_root_pointer() (Lenny Szubowicz) [1034598]

* Thu Nov 21 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-54.el7]
- [fs] gfs2: Fix ref count bug relating to atomic_open (Robert S Peterson) [1032800]

* Mon Nov 18 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-53.el7]
- [ethernet] mlx4: Fix pages never dma unmapped on rx (Steve Best) [1030192]
- [kernel] Add method for displaying affection for Red Hat (Prarit Bhargava) [1025450]
- [powerpc] Fix fatal SLB miss when restoring PPR (Steve Best) [1027633]
- [fs] gfs2: Implement a "rgrp has no extents longer than X" scheme (Robert S Peterson) [1019462]
- [fs] gfs2: Drop inadequate rgrps from the reservation tree (Robert S Peterson) [1019462]
- [fs] gfs2: If requested is too large, use the largest extent in the rgrp (Robert S Peterson) [1019462]
- [fs] gfs2: Add allocation parameters structure (Robert S Peterson) [1019462]
- [security] keys: Fix error handling in big_key instantiation (David Howells) [1029877]
- [kernel] move get_online_cpus/put_online_cpus locking out (Rik van Riel) [1027267]
- [kernel] sched/numa: Cure update_numa_stats() vs. hotplug (Rik van Riel) [1027267]
- [kernel] sched/numa: Fix NULL pointer dereference in task_numa_migrate() (Rik van Riel) [1028100]
- [scsi] hpsa: remove P822se PCI ID (Tomas Henzl) [1029009]
- [scsi] hpsa: correct gen9 PCI IDs (Tomas Henzl) [1029009]
- [scsi] scsi_dh_alua: ALUA handler attach should succeed while TPG is transitioning (Ewan Milne) [1020355]
- [scsi] scsi_dh_alua: ALUA check sense should retry device internal reset unit attention (Ewan Milne) [1020355]
- [scsi] scsi_debug: fix endianness bug in sdebug_build_parts() (Maurizio Lombardi) [1017128]
- [block] blk-mq: don't disallow request merges for req->special being set (Mike Snitzer) [1016109]
- [block] blk-mq: mq plug list breakage (Mike Snitzer) [1016109]
- [block] blk-mq: fix for flush deadlock (Mike Snitzer) [1016109]
- [block] blk-mq: add blk_mq_stop_hw_queues (Mike Snitzer) [1016109]
- [block] blk-mq: fix permissions for ipi_redirect sysfs attribute (Mike Snitzer) [1016109]
- [block] blk-mq: zero out ctx_map during initialization (Mike Snitzer) [1016109]
- [block] blk-mq: cache rq->q (Mike Snitzer) [1016109]
- [block] blk-mq: use a separate plug list for blk-mq requests (Mike Snitzer) [1016109]
- [block] blk-mq: switch to percpu-ida for tag management (Mike Snitzer) [1016109]
- [lib] percpu_ida: add an API to return free tags (Mike Snitzer) [1016109]
- [lib] percpu_ida: add percpu_ida_for_each_free (Mike Snitzer) [1016109]
- [lib] percpu_ida: make percpu_ida percpu size/batch configurable (Mike Snitzer) [1016109]
- [lib] idr: Percpu ida (Mike Snitzer) [1016109]
- [block] blk-mq: call exit_hctx on hw queue teardown (Mike Snitzer) [1016109]
- [lib] percpu_counter: __this_cpu_write() doesn't need to be protected by spinlock (Mike Snitzer) [1016109]
- [block] blk-mq: fix blk_mq_start_stopped_hw_queues from irq context (Mike Snitzer) [1016109]
- [block] blk-mq: cleanup blk_mq_bio_to_request (Mike Snitzer) [1016109]
- [block] blk-mq: kill blk_mq_finish_request (Mike Snitzer) [1016109]
- [block] blk-mq: always complete bios in blk_mq_complete_request (Mike Snitzer) [1016109]
- [block] blk-mq: dont call blk_mq_free_request from blk_mq_finish_request (Mike Snitzer) [1016109]
- [block] blk-mq: more careful bio completion (Mike Snitzer) [1016109]
- [block] use blk-exec.c infrastructure for blk-mq (Mike Snitzer) [1016109]
- [block] make blk_get_put_request work for blk-mq drivers (Mike Snitzer) [1016109]
- [block] remove request ref_count (Mike Snitzer) [1016109]
- [block] blk-mq: Lower minimum queue depth from 4 to 1 (Mike Snitzer) [1016109]
- [block] blk-mq: Do not fail blk_mq_reg::queue_depth value of zero (Mike Snitzer) [1016109]
- [block] blk-mq: Do not allocate more cache entries than used (Mike Snitzer) [1016109]
- [block] blk-mq: Check queue depth is valid (Mike Snitzer) [1016109]
- [block] blk-mq: Sanity check reserved tags (Mike Snitzer) [1016109]

* Fri Nov 15 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-52.el7]
- [x86] trace: Change user|kernel_page_fault to page_fault_user|kernel (Seiji Aguchi) [726853]
- [x86] trace: Add page fault tracepoints (Seiji Aguchi) [726853]
- [x86] trace: Delete __trace_alloc_intr_gate() (Seiji Aguchi) [726853]
- [x86] trace: Register exception handler to trace IDT (Seiji Aguchi) [726853]
- [x86] trace: Remove __alloc_intr_gate() (Seiji Aguchi) [726853]
- [kernel] audit: call audit_bprm() only once to add AUDIT_EXECVE information (Richard Guy Briggs) [1010367]
- [kernel] audit: move audit_aux_data_execve contents into audit_context union (Richard Guy Briggs) [1010367]
- [kernel] audit: remove unused envc member of audit_aux_data_execve (Richard Guy Briggs) [1010367]
- [kernel] audit: Kill the unused struct audit_aux_data_capset (Richard Guy Briggs) [1010367]
- [fs] gfs2: fix dentry leaks (Abhijith Das) [1010350]
- [fs] gfs2: d_splice_alias() can't return error (Abhijith Das) [1010350]
- [fs] atomic_open: take care of EEXIST in no-open case with O_CREAT|O_EXCL in fs/namei.c (Abhijith Das) [1010350]
- [fs] vfs: don't set FILE_CREATED before calling ->atomic_open() (Abhijith Das) [1010350]
- [fs] nfs: set FILE_CREATED (Abhijith Das) [1010350]
- [fs] gfs2: set FILE_CREATED (Abhijith Das) [1010350]
- [fs] vfs: improve i_op->atomic_open() documentation (Abhijith Das) [1010350]
- [net] svcrpc: set cr_gss_mech from gss-proxy as well as legacy upcall (J. Bruce Fields) [1026643]
- [mm] zbud: fix condition check on allocation size (Jerome Marchand) [1009496]
- [kernel] sched: Optimize task_sched_runtime() (Larry Woodman) [986058]
- [x86] setup: add a customer friendly message for single cpu systems (Prarit Bhargava) [1009066]
- [x86] efi: Disable secure boot if shim is in insecure mode (Lenny Szubowicz) [1004888]
- [kernel] modsign: Support not importing certs from db (Lenny Szubowicz) [1004888]
- [kernel] modsign: Import certificates from UEFI Secure Boot (Lenny Szubowicz) [1004888]
- [kernel] keys: Add a system blacklist keyring (Lenny Szubowicz) [1004888]
- [crypto] asymmetric_keys: Add an EFI signature blob parser and key loader (Lenny Szubowicz) [1004888]
- [kernel] efi: Add EFI signature data types (Lenny Szubowicz) [1004888]
- [kernel] hibernate: Disable if securelevel above zero (Lenny Szubowicz) [903815]
- [x86] efi: Add EFI_SECURE_BOOT bit (Lenny Szubowicz) [903815]
- [x86] Add option to automatically set securelevel when in Secure Boot mode (Lenny Szubowicz) [903815]
- [platform] asus-wmi: Restrict debugfs interface when securelevel is set (Lenny Szubowicz) [903815]
- [x86] Restrict MSR access when securelevel is set (Lenny Szubowicz) [903815]
- [kernel] uswsusp: Disable when securelevel is set (Lenny Szubowicz) [903815]
- [kernel] kexec: Disable at runtime if securelevel has been set (Lenny Szubowicz) [903815]
- [acpi] Ignore acpi_rsdp kernel parameter when securelevel is set (Lenny Szubowicz) [903815]
- [acpi] Limit access to custom_method if securelevel is set (Lenny Szubowicz) [903815]
- [char] mem: Restrict /dev/mem and /dev/kmem when securelevel is set (Lenny Szubowicz) [903815]
- [x86] Lock down IO port access when securelevel is enabled (Lenny Szubowicz) [903815]
- [pci] Lock down BAR access when securelevel is enabled (Lenny Szubowicz) [903815]
- [x86] Enforce module signatures when securelevel is greater than 0 (Lenny Szubowicz) [903815]
- [kernel] Add BSD-style securelevel support (Lenny Szubowicz) [903815]

* Thu Nov 14 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-51.el7]
- [net] nfnetlink: do not ack malformed messages (Jiri Benc) [1023123]
- [net] netfilter: nft_compat: use _safe version of list_for_each (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: remove duplicated include from nf_tables_ipv4.c (Jiri Benc) [1023123]
- [net] netfilter: bridge: nf_tables: add filter chain type (Jiri Benc) [1023123]
- [net] netfilter: nft_nat: Fix endianness issue reported by sparse (Jiri Benc) [1023123]
- [net] netfilter: bridge: fix nf_tables bridge dependencies with main core (Jiri Benc) [1023123]
- [net] nf_tables: mark as Tech Preview (Jiri Benc) [1023123]
- [net] nf_tables: stuff structures to preserve kABI in the future (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add ARP filtering support (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add trace support (Jiri Benc) [1023123]
- [net] netfilter: nfnetlink: add batch support and use it from nf_tables (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add insert operation (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: complete net namespace support (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: Add support for IPv6 NAT (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add support for dormant tables (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: nft_payload: fix transport header base (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add compatibility layer for x_tables (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: convert built-in tables/chains to chain types (Jiri Benc) [1023123]
- [net] netfilter: nft_payload: add optimized payload implementation for small loads (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add optimized data comparison for small values (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: expression ops overloading (Jiri Benc) [1023123]
- [net] netfilter: nf_tables: add netlink set API (Jiri Benc) [1023123]
- [net] netfilter: add nftables (Jiri Benc) [1023123]
- [net] netfilter: nf_nat: move alloc_null_binding to nf_nat_core.c (Jiri Benc) [1023123]
- [net] netfilter: pass hook ops to hookfn (Jiri Benc) [1023123]
- [net] netlink: fix splat in skb_clone with large messages (Jiri Benc) [1023123]
- [net] netlink: allow large data transfers from user-space (Jiri Benc) [1023123]

* Wed Nov 13 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-50.el7]
- [virt] hyperv/vmbus: Fix a bug in channel rescind code (Jason Wang) [1017564]
- [virt] hyperv: Fix wrong check for synic_event_page (Jason Wang) [1017564]
- [virt] hyperv/vmbus: fix vmbus_recvpacket_raw() return code (Jason Wang) [1017564]
- [virt] hyperv/input: add a driver to support Hyper-V synthetic keyboard (Jason Wang) [1017564]
- [virt] hyperv: Correctly guard the local APIC calibration code (Jason Wang) [1017564]
- [virt] hyperv: Get the local APIC timer frequency from the hypervisor (Jason Wang) [1017564]
- [kernel] stop_machine: fix race between stop_two_cpus and stop_cpus (Rik van Riel) [1023627]
- [video] fb: make fp_get_options name argument const (Rob Clark) [1018414]
- [drm] nouveau/device: recognise GK208 (Rob Clark) [1018414]
- [drm] nouveau/graph: fix a number of missing explicit array terminators (Rob Clark) [1018414]
- [drm] nouveau/disp: semi-complete link training sequence even if display disappears (Rob Clark) [1018414]
- [drm] nouveau/bios: some older boards have shorter displayport tables (Rob Clark) [1018414]
- [drm] nouveau/fbcon: bracket entrypoints with a per-device enabled check (Rob Clark) [1018414]
- [drm] nouveau/disp: reorder writes to lane current control regs (Rob Clark) [1018414]
- [drm] nouveau/disp: reorder writes to lane current control regs (Rob Clark) [1018414]
- [drm] nouveau/disp: log if DP link training fails (Rob Clark) [1018414]
- [drm] nouveau/disp: disable display underflow reporting at init (Rob Clark) [1018414]
- [drm] nouveau/clock: fix accidental limiting of pll coefficients (Rob Clark) [1018414]
- [drm] nouveau/device: use an additional bit from NV_PMC_BOOT_0 to identify chipset (Rob Clark) [1018414]
- [drm] nouveau/bios/init: return failure condition on invalid opcodes (Rob Clark) [1018414]
- [drm] nouveau/therm: ack any pending IRQ at init (Rob Clark) [1018414]
- [drm] nouveau/therm: kill some over-zealous debugging (Rob Clark) [1018414]
- [drm] radeon: don't use PACKET2 on CIK (Rob Clark) [1018414]
- [drm] nouveau: split lock into list+exec and enable refcount locks (Rob Clark) [1018414]
- [drm] nouveau: convert event handler apis to split create/enable semantics (Rob Clark) [1018414]
- [drm] nouveau: share engine/channel constructor between implementations (Rob Clark) [1018414]
- [drm] nouveau: prepare for the sharing of constructors between implementations (Rob Clark) [1018414]
- [drm] nouveau: make vblank tracking data private to the implementations (Rob Clark) [1018414]
- [drm] nouveau: share engine/channel struct definitions between implementations (Rob Clark) [1018414]
- [drm] nouveau: Allow asymmetric nouveau_event_get/_put (Rob Clark) [1018414]
- [drm] nouveau: Move event index check from critical section (Rob Clark) [1018414]
- [drm] nouveau: Add priv field for event handlers (Rob Clark) [1018414]
- [drm] nouveau: off by one in nouveau_drm_vblank_enable() (Rob Clark) [1018414]
- [drm] backport to Linux 3.12-rc7 (Rob Clark) [1018414]
- [firmware] dmi: add support for exact DMI matches in addition to substring matching (Rob Clark) [1025360]
- [vga] vga_switcheroo: add driver control power feature (Rob Clark) [1025360]
- [mm] vmscan: new shrinker API (Rob Clark) [1025360]
- [kernel] Add arch_phys_wc_{add, del} to manipulate WC MTRRs if needed (Rob Clark) [1025360]
- [kernel] mutex: Move ww_mutex definitions to ww_mutex.h (Rob Clark) [1025360]
- [kernel] reservation: cross-device reservation support (Rob Clark) [1025360]
- [kernel] locking-selftests: Handle unexpected failures more strictly (Rob Clark) [1025360]
- [kernel] mutex: Add more w/w tests to test EDEADLK path handling (Rob Clark) [1025360]
- [kernel] mutex: Add more tests to lib/locking-selftest.c (Rob Clark) [1025360]
- [kernel] mutex: Add w/w tests to lib/locking-selftest.c (Rob Clark) [1025360]
- [kernel] mutex: Add w/w mutex slowpath debugging (Rob Clark) [1025360]
- [kernel] mutex: Add support for wound/wait style locks (Rob Clark) [1025360]
- [kernel] mutex: Make __mutex_fastpath_lock_retval return whether fastpath succeeded or not (Rob Clark) [1025360]

* Tue Nov 12 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-49.el7]
- [usb] misc/usb3503: Fix compile error due to incorrect regmap depedency (Don Zickus) [895641]
- [usb] storage: add quirk for mandatory READ_CAPACITY_16 (Don Zickus) [895641]
- [usb] serial/option: blacklist Olivetti Olicard200 (Don Zickus) [895641]
- [usb] quirks: add touchscreen that is dazzeled by remote wakeup (Don Zickus) [895641]
- [usb] quirks: add one device that cannot deal with suspension (Don Zickus) [895641]
- [usb] serial/option: add support for Inovia SEW858 device (Don Zickus) [895641]
- [usb] serial/ti_usb_3410_5052: add Abbott strip port ID to combined table as well (Don Zickus) [895641]
- [usb] support new huawei devices in option.c (Don Zickus) [895641]
- [usb] xhci: Fix spurious wakeups after S5 on Haswell (Don Zickus) [895641]
- [usb] xhci: fix write to USB3_PSSEN and XUSB2PRM pci config registers (Don Zickus) [895641]
- [usb] xhci: quirk for extra long delay for S4 (Don Zickus) [895641]
- [usb] xhci: Don't enable/disable RWE on bus suspend/resume (Don Zickus) [895641]
- [net] usbnet: fix handling padding packet (Don Zickus) [895641]
- [usb] imx21: accept very late isochronous URBs (Don Zickus) [895641]
- [usb] core: check usb device's state before sending a Set SEL control transfer (Don Zickus) [895641]
- [usb] xhci: Fix xHCI host issues on remote wakeup (Don Zickus) [1016889]
- [usb] serial/pl2303: distinguish between original and cloned HX chips (Don Zickus) [895641]
- [usb] fix typo in usb serial simple driver Kconfig (Don Zickus) [895641]
- [usb] core: fix incorrect type in assignment in descriptors_changed() (Don Zickus) [895641]
- [usb] core: compare and release one bos descriptor in usb_reset_and_verify_device() (Don Zickus) [895641]
- [usb] ehci: remove debugging statement with ehci statistics in ehci_stop() (Don Zickus) [895641]
- [usb] ehci: remove duplicate debug_async_open() prototype in ehci-dbg.c (Don Zickus) [895641]
- [usb] ehci: enable debugging code when CONFIG_DYNAMIC_DEBUG is set (Don Zickus) [895641]
- [usb] ehci: remove ehci_vdbg() verbose debugging statements (Don Zickus) [895641]
- [usb] xhci: Fix warning introduced by disabling runtime PM (Don Zickus) [1016889]
- [usb] storage: audit sysfs attribute permissions (Don Zickus) [895641]
- [usb] xhci: prevent "callbacks suppressed" when debug is not enabled (Don Zickus) [1016889]
- [usb] xhci: fix port BESL LPM capability checking (Don Zickus) [1016889]
- [usb] ohci: fix build error related to ohci_suspend/resume (Don Zickus) [895641]
- [usb] serial: clean up attribute permissions (Don Zickus) [895641]
- [usb] usbtmc: fix up attribute permissions (Don Zickus) [895641]
- [usb] core: be specific about attribute permissions (Don Zickus) [895641]
- [usb] core: use DRIVER_ATTR_RW() (Don Zickus) [895641]
- [usb] don't use bNbrPorts after initialization (Don Zickus) [895641]
- [usb] fail on usb_hub_create_port_device() errors (Don Zickus) [895641]
- [usb] fix cleanup after failure in hub_configure() (Don Zickus) [895641]
- [usb] ohci: add missing PCI PM callbacks to ohci-pci.c (Don Zickus) [895641]
- [usb] serial: fix stringify operator in usb-serial-simple (Don Zickus) [895641]
- [usb] wusbcore: Use usb_init_urb instead of creating the URB manually (Don Zickus) [895641]
- [usb] wusbcore: fix leak of urb in wa_xfer_destroy (Don Zickus) [895641]
- [usb] wusbcore: fix resource cleanup in error path in __wa_xfer_setup_segs (Don Zickus) [895641]
- [usb] wusbcore: clear RPIPE stall for control endpoints (Don Zickus) [895641]
- [usb] uss720: fix DMA-buffer allocation (Don Zickus) [895641]
- [usb] quatech2: fix port DMA-buffer allocations (Don Zickus) [895641]
- [usb] quatech2: fix serial DMA-buffer allocations (Don Zickus) [895641]
- [usb] keyspan: fix port DMA-buffer allocations (Don Zickus) [895641]
- [usb] keyspan: fix serial DMA-buffer allocations (Don Zickus) [895641]
- [usb] rh_call_control tbuf overflow fix (Don Zickus) [895641]
- [usb] host: add Kconfig option for EHSET (Don Zickus) [895641]
- [usb] serial/pl2303: improve the chip type detection/distinction (Don Zickus) [895641]
- [usb] serial/pl2303: improve the chip type information output on startup (Don Zickus) [895641]
- [usb] serial/pl2303: simplify the else-if contruct for type_1 chips in pl2303_startup() (Don Zickus) [895641]
- [usb] xhci: fix dma mask setup in xhci.c (Don Zickus) [1016889]
- [usb] xhci: trace debug statements related to ring expansion (Don Zickus) [1016889]
- [usb] xhci: trace debug messages related to driver initialization and unload (Don Zickus) [1016889]
- [usb] xhci: trace debug statements for urb cancellation (Don Zickus) [1016889]
- [usb] xhci: add xhci_cmd_completion trace event (Don Zickus) [1016889]
- [usb] xhci: add xhci_address_ctx trace event (Don Zickus) [1016889]
- [usb] xhci: add trace for debug messages related to endpoint reset (Don Zickus) [1016889]
- [usb] xhci: add trace for debug messages related to quirks (Don Zickus) [1016889]
- [usb] xhci: add trace for debug messages related to changing contexts (Don Zickus) [1016889]
- [usb] xhci: add traces for debug messages in xhci_address_device() (Don Zickus) [1016889]
- [usb] xhci: remove CONFIG_USB_XHCI_HCD_DEBUGGING and unused code (Don Zickus) [1016889]
- [usb] xhci: replace printk(KERN_DEBUG ...) (Don Zickus) [1016889]
- [usb] xhci: replace xhci_info() with xhci_dbg() (Don Zickus) [1016889]
- [usb] xhci: Add Device Tree support to XHCI Platform driver (Don Zickus) [1016889]
- [usb] serial/pl2303: add two comments concerning the supported baud rates with HX chips (Don Zickus) [895641]
- [usb] serial/pl2303: also use the divisor based baud rate encoding method for baud rates < 115200 with HX chips (Don Zickus) [895641]
- [usb] serial/pl2303: increase the allowed baud rate range for the divisor based encoding method (Don Zickus) [895641]
- [usb] serial/pl2303: move the two baud rate encoding methods to separate functions (Don Zickus) [895641]
- [usb] serial/pl2303: remove 500000 baud from the list of standard baud rates (Don Zickus) [895641]
- [usb] serial/pl2303: do not round to the next nearest standard baud rate for the divisor based baud rate encoding method (Don Zickus) [895641]
- [usb] serial/pl2303: fix the upper baud rate limit check for type_0/1 chips (Don Zickus) [895641]
- [usb] serial/pl2303: fix+improve the divsor based baud rate encoding method (Don Zickus) [895641]
- [usb] hwa: avoid constant suspend and resume on the root hub (Don Zickus) [895641]
- [usb] adutux: fix big-endian device-type reporting (Don Zickus) [895641]
- [usb] usbtmc: fix big-endian probe of Rigol devices (Don Zickus) [895641]
- [usb] wusbcore: clean up list locking in urb enqueue (Don Zickus) [895641]
- [usb] wusbcore: fix root hub hub_status_data to only return > 0 if status has actually changed (Don Zickus) [895641]
- [usb] ehci: Add support for SINGLE_STEP_SET_FEATURE test of EHSET (Don Zickus) [895641]
- [usb] hcd: Log error code if reset() fails (Don Zickus) [895641]
- [usb] misc/usb3503: Support operation with no I2C control (Don Zickus) [895641]
- [usb] misc/usb3503: Add USB3503A to the compatible list (Don Zickus) [895641]
- [usb] misc/usb3503: Default to hub mode (Don Zickus) [895641]
- [usb] misc/usb3503: Fix typos in error messages (Don Zickus) [895641]
- [usb] misc/usb3503: Factor out I2C probe (Don Zickus) [895641]
- [usb] misc/usb3503: Convert to regmap (Don Zickus) [895641]
- [usb] misc/usb3503: Actively manage Hub Connect GPIO (Don Zickus) [895641]
- [usb] misc/usb3503: Use gpio_set_value_cansleep() (Don Zickus) [895641]
- [usb] Move definition of USB_EHCI_BIG_ENDIAN_MMIO et al. out side of the ifs (Don Zickus) [895641]
- [usb] misc/usb3503: Convert to devm_ APIs (Don Zickus) [895641]
- [usb] serial: move the "simple" drivers into usb-serial-simple.c (Don Zickus) [895641]
- [net] usbnet: support DMA SG (Don Zickus) [895641]
- [usb] xhci: mark no_sg_constraint (Don Zickus) [1016889]
- [usb] introduce usb_device_no_sg_constraint() helper (Don Zickus) [895641]
- [usb] ehci: support running URB giveback in tasklet context (Don Zickus) [895641]
- [usb] ehci: improve interrupt qh unlink (Don Zickus) [895641]
- [usb] ehci: improve ehci_endpoint_disable (Don Zickus) [895641]
- [usb] hcd: support giveback of URB in tasklet context (Don Zickus) [895641]
- [usb] fix some scripts/kernel-doc warnings (Don Zickus) [895641]
- [usb] ehci: don't depend on hardware for tracking port resets and resumes (Don Zickus) [895641]
- [usb] ehci: keep better track of resuming ports (Don Zickus) [895641]
- [usb] pl2303: restrict the divisor based baud rate encoding method to the "HX" chip type (Don Zickus) [895641]
- [usb] refactor code for enabling/disabling remote wakeup (Don Zickus) [895641]
- [usb] simplify the interface of usb_get_status() (Don Zickus) [895641]
- [usb] xhci: add missing dma-mapping.h includes (Don Zickus) [895641]
- [net] usbnet: centralize computing of max rx/tx qlen (Don Zickus) [895641]
- [usb] serial: add driver for Suunto ANT+ USB device (Don Zickus) [895641]
- [usb] ohci_usb warn "irq nobody cared" on shutdown (Don Zickus) [895641]
- [usb] ohci-ep93xx: tidy up driver (*probe) and (*remove) (Don Zickus) [895641]
- [usb] ohci-ep93xx: use devm_clk_get() (Don Zickus) [895641]
- [usb] ohci-ep93xx: use platform_get_irq() (Don Zickus) [895641]
- [usb] ohci-ep93xx: use devm_ioremap_resource() (Don Zickus) [895641]
- [usb] usb-skeleton: add retry for nonblocking read (Don Zickus) [895641]
- [usb] usbtmc: convert to devm_kzalloc (Don Zickus) [895641]
- [usb] usbtmc: remove redundant braces (Don Zickus) [895641]
- [usb] usbtmc: call pr_err instead of plain printk (Don Zickus) [895641]
- [usb] usbtmc: remove trailing spaces (Don Zickus) [895641]
- [usb] usbfs: Allow printer class 'get_device_id' without needing to claim the intf (Don Zickus) [895641]
- [usb] remove redundant "#if" (Don Zickus) [895641]
- [usb] misc: EHSET Test Fixture device driver for host compliance (Don Zickus) [895641]
- [usb] clamp bInterval to allowed range (Don Zickus) [895641]
- [usb] atm/speedtch: be careful with bInterval (Don Zickus) [895641]
- [usb] cdc-acm: be careful with bInterval (Don Zickus) [895641]
- [usb] fix build warning in pci-quirks.h when CONFIG_PCI is not enabled (Don Zickus) [895641]
- [usb] xhci: Mark two functions __maybe_unused (Don Zickus) [895641]
- [usb] check sg buffer size in usb_submit_urb (Don Zickus) [895641]
- [usb] isp1362: move debug files from proc to debugfs (Don Zickus) [895641]
- [usb] sl811: move debug files from proc to debugfs (Don Zickus) [895641]
- [usb] remove unneeded idr.h include (Don Zickus) [895641]
- [usb] sl811: remove CONFIG_USB_DEBUG dependency (Don Zickus) [895641]
- [usb] isp116x: remove dependency on CONFIG_USB_DEBUG (Don Zickus) [895641]
- [usb] isp1362: remove CONFIG_USB_DEBUG dependency (Don Zickus) [895641]
- [usb] isp1362: remove _DBG() usage (Don Zickus) [895641]
- [usb] isp1362: remove unused _WARN_ON() calls (Don Zickus) [895641]
- [usb] isp1362: remove unused _BUG_ON() calls (Don Zickus) [895641]
- [usb] usbatm: remove CONFIG_USB_DEBUG dependancy (Don Zickus) [895641]
- [usb] usbatm: move the atm_dbg() call to use dynamic debug (Don Zickus) [895641]
- [usb] usbatm: don't rely on CONFIG_USB_DEBUG (Don Zickus) [895641]
- [usb] usbatm: remove unneeded trace printk calls (Don Zickus) [895641]
- [usb] usbatm: remove unused UDSL_ASSERT macro (Don Zickus) [895641]
- [usb] ti_usb_3410_5052: remove vendor/product module parameters (Don Zickus) [895641]
- [usb] ti_usb_3410_5052: remove unused wait queue (Don Zickus) [895641]
- [usb] ti_usb_3410_5052: kill private fifo (Don Zickus) [895641]
- [usb] safe_serial: remove vendor/product module parameters (Don Zickus) [895641]
- [usb] mos7840: remove broken chase implementation (Don Zickus) [895641]
- [usb] io_ti: move port initialisation to probe (Don Zickus) [895641]
- [usb] io_ti: kill private fifo (Don Zickus) [895641]
- [usb] io_edgeport: remove unused defines (Don Zickus) [895641]
- [usb] ftdi_sio: remove unused defines (Don Zickus) [895641]
- [usb] ftdi_sio: remove vendor/product module parameters (Don Zickus) [895641]
- [usb] ftdi_sio: remove redundant raise of DTR/RTS at open (Don Zickus) [895641]
- [usb] ftdi_sio: clean up device initialisation (Don Zickus) [895641]
- [usb] oti6858: do not call set_termios with uninitialised data (Don Zickus) [895641]
- [usb] pl2303: remove debugging noise (Don Zickus) [895641]
- [usb] pl2303: clean up set_termios (Don Zickus) [895641]
- [usb] pl2303: clean up baud-rate handling (Don Zickus) [895641]
- [usb] pl2303: refactor baud-rate handling (Don Zickus) [895641]
- [usb] console: remove unnecessary operations test (Don Zickus) [895641]
- [usb] console: use dev_dbg (Don Zickus) [895641]
- [usb] serial: set drain delay at port probe (Don Zickus) [895641]
- [usb] serial: clean up dtr_rts (Don Zickus) [895641]
- [usb] serial: remove hupping check from tiocmiwait (Don Zickus) [895641]
- [usb] serial: remove defensive test from set_termios (Don Zickus) [895641]
- [usb] misc: remove CONFIG_USB_DEBUG from Makefile (Don Zickus) [895641]
- [usb] adutux: remove direct calls to printk() (Don Zickus) [895641]
- [usb] adutux: remove custom debug macro and module parameter (Don Zickus) [895641]
- [usb] adutux: remove custom debug macro (Don Zickus) [895641]
- [usb] adutux: remove unneeded tracing macros (Don Zickus) [895641]
- [usb] legotower: remove direct calls to printk() (Don Zickus) [895641]
- [usb] legotower: remove custom debug macro and module parameter (Don Zickus) [895641]
- [usb] legousbtower: remove custom debug macro (Don Zickus) [895641]
- [usb] legotower: remove unneeded tracing macros (Don Zickus) [895641]
- [usb] ldusb: remove custom dbg_info() macro (Don Zickus) [895641]
- [usb] xhci: Correct misplaced newlines (Don Zickus) [1016889]
- [usb] xhci: refactor EHCI/xHCI port switching (Don Zickus) [1016889 970717]
- [usb] xhci: Report USB 2.1 link status for L1 (Don Zickus) [1016889]
- [usb] xhci: Refactor port status into a new function (Don Zickus) [1016889]
- [usb] xhci: add the suspend/resume functionality (Don Zickus) [1016889]
- [usb] move the definition of USB_MAXCHILDREN (Don Zickus) [895641]
- [usb] atm: avoid parsing names as kthread_run() format strings (Don Zickus) [895641]
- [usb] xhci: Add missing unlocks on error paths (Don Zickus) [895641]
- [usb] ehci-atmel: prepare clk before calling enable (Don Zickus) [895641]
- [usb] hwa: fix device probe failure (Don Zickus) [895641]
- [usb] wusbcore: add sysfs attribute for retry count (Don Zickus) [895641]
- [usb] wusbcore: add sysfs attribute for DNTS count and interval (Don Zickus) [895641]
- [usb] check usb_hub_to_struct_hub() return value (Don Zickus) [895641]
- [usb] ehci: Remove double assignment of .start in ehci_msp_hc_driver (Don Zickus) [895641]
- [usb] ehci: export ehci_handshake for ehci-hcd sub-drivers (Don Zickus) [895641]
- [usb] wusbcore: add scatter gather support (Don Zickus) [895641]
- [usb] cdc-acm: remove unneeded spin_lock_irqsave/restore on write path (Don Zickus) [895641]
- [usb] serial: increase the number of devices we support (Don Zickus) [895641]
- [usb] serial: make minor allocation dynamic (Don Zickus) [895641]
- [usb] xhci: remove BUG() in xhci_get_endpoint_type() (Don Zickus) [895641]
- [usb] xhci: Remove BUG in xhci_setup_addressable_virt_dev (Don Zickus) [895641]
- [usb] xhci: Remove BUG_ON in xhci_get_input_control_ctx (Don Zickus) [895641]
- [usb] xhci: Remove BUG_ON() in xhci_alloc_container_ctx (Don Zickus) [895641]
- [usb] ehci-platform: add pre_setup() method to platform data (Don Zickus) [895641]
- [usb] serial: add minor and port number (Don Zickus) [895641]
- [usb] wusbcore: ignore HWA_NOTIF_BPST_ADJ notifications (Don Zickus) [895641]
- [usb] wusbcore: add HWA-specific fields to usb_rpipe_descriptor (Don Zickus) [895641]
- [usb] wusbhc: disable suspend and resume on the root hub (Don Zickus) [895641]
- [usb] fix PTR_ERR translation in init_usb_class() (Don Zickus) [895641]
- [usb] wusbcore: reduce keepalive threshold from timeout/2 to timeout/3 (Don Zickus) [895641]
- [usb] host: make USB_ARCH_HAS_?HCI obsolete (Don Zickus) [895641]
- [usb] ohci: remove bogus #error (Don Zickus) [895641]
- [usb] add usb2 Link PM variables to sysfs and usb_device (Don Zickus) [895641]
- [usb] xhci: add USB2 Link power management BESL support (Don Zickus) [895641]
- [usb] xhci: define port register names and use them instead of magic numbers (Don Zickus) [895641]
- [usb] xhci: check usb2 port capabilities before adding hw link PM support (Don Zickus) [895641]
- [usb] xhci: unify parameter of xhci_msi_irq (Don Zickus) [895641]
- [usb] xhci-dbg: Display endpoint number and direction in context dump (Don Zickus) [895641]
- [usb] serial: pl2303 works at 500kbps (Don Zickus) [895641]
- [usb] ohci: add a name for the platform-private field (Don Zickus) [895641]
- [usb] ohci: make ohci-platform a separate driver (Don Zickus) [895641]
- [usb] misc/usb3503: Remove 100ms sleep on reset, conform to data sheet (Don Zickus) [895641]
- [usb] misc/usb3503: Fix up whitespace (Don Zickus) [895641]
- [usb] Allow the USB HCD to create Wireless USB root hubs (Don Zickus) [895641]
- [usb] serial: add support Infineon modem USB flashloader driver (Don Zickus) [895641]
- [usb] ohci: make ohci-pci a separate driver (Don Zickus) [895641]
- [usb] ohci: Generic changes to make ohci-pci a separate driver (Don Zickus) [895641]
- [usb] ohci: prepare to make ohci-hcd a library module (Don Zickus) [895641]
- [usb] fhci: upgrade the isochronous API (Don Zickus) [895641]
- [usb] imx21: upgrade the isochronous API (Don Zickus) [895641]
- [usb] serial: dump small buffers with help of *ph (Don Zickus) [895641]
- [usb] host: remove leftover release_mem_region (Don Zickus) [895641]
- [usb] misc/usb3503: Adding device tree entry 'disabled-ports' (Don Zickus) [895641]
- [usb] misc/usb3503: Add to select the ports to disable (Don Zickus) [895641]
- [usb] ehci: Only sleep for post-resume handover if devices use persist (Don Zickus) [895641]
- [usb] message: Fixed parenthesis error in sizeof function (Don Zickus) [895641]
- [usb] message: fixed error 'no space before bracket' (Don Zickus) [895641]
- [usb] devio: fixed error 'do not use assignment in if condition' (Don Zickus) [895641]
- [usb] devio: Fixed macro parenthesis error (Don Zickus) [895641]
- [usb] devio: fixed warning 'use <linux/uacces.h> instead <asm/uacces.h>' (Don Zickus) [895641]
- [usb] usbtmc: Change magic number to constant (Don Zickus) [895641]
- [usb] usbtmc: usbtmc_read sends multiple TMC header based on rigol_quirk (Don Zickus) [895641]
- [usb] usbtmc: Set rigol_quirk if device is listed (Don Zickus) [895641]
- [usb] usbtmc: TMC request code segregated from usbtmc_read (Don Zickus) [895641]
- [usb] usbtmc: Add flag rigol_quirk to usbtmc_device_data (Don Zickus) [895641]
- [usb] storage/alauda: initialize variables directly (Don Zickus) [895641]
- [usb] storage/sddr09: initialize variables directly (Don Zickus) [895641]
- [usb] fsl: add missing platform_driver owner (Don Zickus) [895641]
- [usb] quatech2: Staticize local symbol (Don Zickus) [895641]
- [usb] misc: Fixed assignment error in if statement (Don Zickus) [895641]
- [usb] misc: Added space after closing brace in adutux.c (Don Zickus) [895641]
- [usb] misc: Added space after comma in adutux.c (Don Zickus) [895641]
- [usb] misc: Reformatted pointer variables in adutux.c (Don Zickus) [895641]
- [usb] misc: Removed space before tabs in adutux.c (Don Zickus) [895641]
- [usb] misc: Replaced deprecated preprocessor in adutux.c (Don Zickus) [895641]
- [fs] nfsd: fix discarded security labels on setattr (J. Bruce Fields) [1025832]
- [fs] nfs: fix inverted test for delegation in nfs4_reclaim_open_state (Jeff Layton) [1025457]
- [x86] kdump: crashkernel=X try to reserve below 896M first, then try below 4G, then MAXMEM (Chao WANG) [994685]
- [kernel] audit: format user messages to size of MAX_AUDIT_MESSAGE_LENGTH (Richard Guy Briggs) [1019913]
- [kernel] audit_alloc: clear TIF_SYSCALL_AUDIT if !audit_context (Richard Guy Briggs) [1026043]

* Fri Nov 08 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-48.el7]
- [ethernet] qlcnic: Update version to 5.3.48 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Implement ndo_get_phys_port_id for 82xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enable diagnostic test for multiple Tx queues (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enable Tx queue changes using ethtool for 82xx Series adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Multi Tx queue support for 82xx Series adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update version to 5.3.47 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Add support for 84xx adapters to load firmware from file (Chad Dupuis) [725018]
- [ethernet] qlcnic: Loopback Inter Driver Communication AEN handler (Chad Dupuis) [725018]
- [ethernet] qlcnic: Add PVID support for 84xx adapters (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enable support for 844X adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update version to 5.2.46 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Dump mailbox command data when a command times out (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix driver initialization for 83xx adapters (Chad Dupuis) [725018]
- [ethernet] qlcnic: Flush mailbox command list when mailbox is not available (Chad Dupuis) [725018]
- [ethernet] qlcnic: Reinitialize mailbox data structures after firmware reset (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix diagnostic interrupt test for 83xx adapters (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix beacon state return status handling (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix set driver version command (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix for flash update failure on 83xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix link speed and duplex display for 83xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix link speed display for 82xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix external loopback test (Chad Dupuis) [725018]
- [ethernet] qlcnic: Removed adapter series name from warning messages (Chad Dupuis) [725018]
- [ethernet] qlcnic: Free up memory in error path (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix ingress MAC learning (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix MAC address filter issue on 82xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update version to 5.2.45 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enable mailbox interface in poll mode when interrupts are not available (Chad Dupuis) [725018]
- [ethernet] qlcnic: Replace poll mode mailbox interface with interrupt based mailbox interface (Chad Dupuis) [725018]
- [ethernet] qlcnic: Interrupt based driver firmware mailbox mechanism (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enhance diagnostic loopback error codes (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix diagnostic interrupt test for 83xx adapters (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix setting Guest VLAN (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix operation type and command type (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix initialization of work function (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix guest VLAN (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix releasing of Tx frag which was never mapped (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix dump template version mask (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix ethtool display for 83xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix panic while setting VF's MAC address (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix multicast packet handling for PF and VF (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix NULL pointer dereference in VF probe path (Chad Dupuis) [725018]
- [ethernet] qlcnic: Set __QLCNIC_DEV_UP in adapter state before enabling interrupts (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix invalid register offset calculation (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update version to 5.2.44 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Add support for 83xx suspend and resume (Chad Dupuis) [725018]
- [ethernet] qlcnic: Add support for 'set driver version' in 83XX (Chad Dupuis) [725018]
- [ethernet] qlcnic: Cleanup of structure qlcnic_hardware_context (Chad Dupuis) [725018]
- [ethernet] qlcnic: Add support for PEX DMA method to read memory section of adapter dump (Chad Dupuis) [725018]
- [ethernet] qlcnic: Minimize sleep duration within loopback diagnostic test (Chad Dupuis) [725018]
- [ethernet] qlcnic: Secondary unicast MAC address support (Chad Dupuis) [725018]
- [ethernet] qlcnic: Handle qlcnic_alloc_mbx_args() failure (Chad Dupuis) [725018]
- [ethernet] qlcnic: replace strict_strtoul() with kstrtoul() (Chad Dupuis) [725018]
- [ethernet] qlcnic: remove redundant D0 power state set (Chad Dupuis) [725018]
- [ethernet] qlcnic: Fix typo in printk (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update version to 5.2.43 (Chad Dupuis) [725018]
- [ethernet] qlcnic: Enhance virtual NIC logging (Chad Dupuis) [725018]
- [ethernet] qlcnic: qlcnic_get_board_name() function cleanup (Chad Dupuis) [725018]
- [ethernet] qlcnic: Implement GET_LED_STATUS command for 82xx adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: modify reset recovery path in diag mode (Chad Dupuis) [725018]
- [ethernet] qlcnic: diagnostics routine changes (Chad Dupuis) [725018]
- [ethernet] qlcnic: Convert nested if-else to switch-case (Chad Dupuis) [725018]
- [ethernet] qlcnic: Initialize trans_work and idc_aen_work at VF probe (Chad Dupuis) [725018]
- [ethernet] qlcnic: Remove qlcnic_config_npars module parameter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Update IRQ name for 8200 and 8300 Series adapter (Chad Dupuis) [725018]
- [ethernet] qlcnic: Disable INT-x interrupt for 83xx on driver unload (Chad Dupuis) [725018]
- [ethernet] qlcnic: Support spoof check config (Chad Dupuis) [725018]
- [x86] Fix x86 invalid cpu boot failure message (Prarit Bhargava) [1024731]
- [virt] virtio-net: refill only when device is up during setting queues (Jason Wang) [1016469]
- [crypto] crc-t10dif: add MODULE_SOFTDEP (Kyle McMartin) [968869]
- [crypto] crct10dif: Add fallback for broken initrds (Kyle McMartin) [968869]
- [crypto] crct10dif: Use PTR_RET (Kyle McMartin) [968869]
- [crypto] crct10dif: Simple correctness and speed test for CRCT10DIF hash (Kyle McMartin) [968869]
- [crypto] crct10dif: Glue code to cast accelerated CRCT10DIF assembly as a crypto transform (Kyle McMartin) [968869]
- [crypto] crct10dif: Accelerated CRC T10 DIF computation with PCLMULQDQ instruction (Kyle McMartin) [968869]
- [crypto] crct10dif: Wrap crc_t10dif function all to use crypto transform framework (Kyle McMartin) [968869]
- [kernel] modules: add support for soft module dependencies (Kyle McMartin) [968869]
- [misc] mei: don't get stuck in select during reset (Prarit Bhargava) [1025420]
- [misc] mei/bus: do not overflow the device name buffer (Prarit Bhargava) [1025420]
- [misc] mei: wake also writers on reset (Prarit Bhargava) [1025420]
- [misc] mei/hbm: fix typo in error message (Prarit Bhargava) [1025420]
- [misc] mei: check whether hw start has succeeded (Prarit Bhargava) [1025420]
- [misc] mei: check if the hardware reset succeeded (Prarit Bhargava) [1025420]
- [misc] mei: mei_cl_connect, don't multiply the timeout twice (Prarit Bhargava) [1025420]
- [misc] mei: do not override a client writing state when buffering (Prarit Bhargava) [1025420]
- [misc] mei: move mei_cl_irq_write_complete to client.c (Prarit Bhargava) [1025420]
- [misc] mei: support HBM versioning (Prarit Bhargava) [1025420]
- [nfc] mei_phy: Clean up file (Prarit Bhargava) [1025420]
- [misc] mei: move mei_cl_complete to client.c (Prarit Bhargava) [1025420]
- [misc] mei: revamp interrupt thread handlers (Prarit Bhargava) [1025420]
- [virt] virtio-net: correctly handle cpu hotplug notifier during resuming (Jason Wang) [1016996]
- [virt] virtio-net: don't respond to cpu hotplug notifier if we're not ready (Jason Wang) [1016996]
- [fs] nfs: fix handling of invalid mount options in nfs_remount (Jeff Layton) [1021538]
- [fs] nfs: reject version and minorversion changes on remount attempts (Jeff Layton) [1021538]
- [drm] qxl: avoid an oops in the deferred io code (Dave Airlie) [1003728 1026182]
- [drm] qxl: fix disabling extra monitors from client (Dave Airlie) [1026182]
- [drm] qxl: remove unnecessary check (Dave Airlie) [1026182]
- [drm] qxl: prefer the monitor config resolution (Dave Airlie) [1026182]
- [drm] copy mode type in drm_mode_connector_list_update() (Dave Airlie) [1026182]
- [drm] qxl: notify that the monitor config changed (Dave Airlie) [1026182]
- [drm] return if changed in drm_helper_hpd_irq_event() (Dave Airlie) [1026182]
- [block] rsxx: Fix possible kernel panic with invalid config (Steve Best) [1024550]
- [block] rsxx: Disallow discards from being unmapped (Steve Best) [1024550]
- [virt] hid-hyperv: convert alloc+memcpy to memdup (Jason Wang) [1026618]
- [virt] hyperv/storvsc: Increase the value of STORVSC_MAX_IO_REQUESTS (Jason Wang) [1026618]
- [virt] hyperv/storvsc: Support FC devices (Jason Wang) [1026618]
- [virt] hyperv: Add the GUID fot synthetic fibre channel device (Jason Wang) [1026618]
- [virt] hyperv/storvsc: Implement multi-channel support (Jason Wang) [1026618]
- [virt] hyperv/storvsc: Update the storage protocol to win8 level (Jason Wang) [1026618]
- [virt] hyperv/storvsc: Increase the value of scsi timeout for storvsc devices (Jason Wang) [1026618]
- [virt] hyperv/vmbus: Terminate vmbus version negotiation on timeout (Jason Wang) [1026618]
- [virt] hv_util: Correctly support ws2008R2 and earlier (Jason Wang) [1026618]
- [virt] hyperv/vmbus: Do not attempt to negoatiate a new version prematurely (Jason Wang) [1026618]
- [virt] hyperv/vmbus: Fix a bug in the handling of channel offers (Jason Wang) [1026618]
- [virt] hyperv: remove HV_DRV_VERSION (Jason Wang) [1026618]
- [virt] hv_balloon: Initialize the transaction ID just before sending the packet (Jason Wang) [1026618]
- [virt] hv_util: Fix a bug in version negotiation code for util services (Jason Wang) [1026618]
- [virt] hyperv/vmbus: incorrect device name is printed when child device is unregistered (Jason Wang) [1026618]
- [virt] hyperv: allocate synic structures before hv_synic_init() (Jason Wang) [1026618]
- [virt] hyperv: check interrupt mask before read_index (Jason Wang) [1026618]
- [virt] hyperv/vmbus: Implement multi-channel support (Jason Wang) [1026618]

* Thu Nov 07 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-47.el7]
- [net] bridge: pass correct vlan id to multicast code (Vlad Yasevich) [912737]
- [net] bridge: Fix updating FDB entries when the PVID is applied (Vlad Yasevich) [912737]
- [net] bridge: Fix the way the PVID is referenced (Vlad Yasevich) [912737]
- [net] bridge: Apply the PVID to priority-tagged frames (Vlad Yasevich) [912737]
- [net] bridge: Don't use VID 0 and 4095 in vlan filtering (Vlad Yasevich) [912737]
- [net] bridge: Correctly clamp MAX forward_delay when enabling STP (Vlad Yasevich) [997814]
- [net] bridge: Clamp forward_delay when enabling STP (Vlad Yasevich) [997814]
- [net] ipv6: mld: introduce mld_{gq, ifc, dad}_stop_timer functions (Daniel Borkmann) [1023947]
- [net] ipv6: mld: refactor query processing into v1/v2 functions (Daniel Borkmann) [1023947]
- [net] ipv6: mld: similarly to MLDv2 have min max_delay of 1 (Daniel Borkmann) [1023947]
- [net] ipv6: mld: implement RFC3810 MLDv2 mode only (Daniel Borkmann) [1023947]
- [net] ipv6: mld: get rid of MLDV2_MRC and simplify calculation (Daniel Borkmann) [1023947]
- [net] ipv6: mld: clean up MLD_V1_SEEN macro (Daniel Borkmann) [1023947]
- [net] ipv6: mld: fix v1/v2 switchback timeout to rfc3810, 9.12. (Daniel Borkmann) [1023947]
- [net] ipv6: mcast: use defines for rfc3810/8.1 lengths (Daniel Borkmann) [1023947]
- [net] ipv6: *_start_timer: rather use unsigned long (Daniel Borkmann) [1023947]
- [net] ipv6: igmp6_event_query: use msecs_to_jiffies (Daniel Borkmann) [1023947]
- [net] ipv6: make unsolicited report intervals configurable for mld (Daniel Borkmann) [1023947]
- [net] ipv4, ipv6: send igmpv3/mld packets with TC_PRIO_CONTROL (Daniel Borkmann) [1023947]
- [net] bridge: disable snooping if there is no querier (Vlad Yasevich) [1019950]
- [net] unix: inherit SOCK_PASS{CRED, SEC} flags from socket to fix race (Daniel Borkmann) [1023964]

* Thu Nov 07 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-46.el7]
- [scsi] aacraid: missing capable() check in compat ioctl (Rich Bono) [1025840]
- [scsi] scsi_dh_rdac: Add new IBM 1813 product id to rdac devlist (Rob Evers) [1020969]
- [scsi] aic94xx: remove driver (Rich Bono) [978980]
- [scsi] qla4xxx: Populate local CHAP credentials for flash target sessions (Chad Dupuis) [1006158]
- [scsi] qla4xxx: Support setting of local CHAP index for flash target entry (Chad Dupuis) [1006158]
- [scsi] qla4xxx: Correct the check for local CHAP entry type (Chad Dupuis) [1006158]
- [scsi] qla4xxx: correctly update session discovery_parent_idx (Chad Dupuis) [1020197]
- [scsi] aacraid: avoid parsing names as kthread_run() format strings (Rich Bono) [752081]
- [scsi] hpsa: return 0 from driver probe function on success, not 1 (Tomas Henzl) [862713]
- [scsi] hpsa: remove unused Smart Array ID (Tomas Henzl) [862713]
- [scsi] hpsa: bump driver version to reflect changes (Tomas Henzl) [862713]
- [scsi] hpsa: housekeeping patch for device_id and product arrays (Tomas Henzl) [862713]
- [scsi] hpsa: add HP Smart Array Gen8 names (Tomas Henzl) [862713]
- [scsi] hpsa: add HP Smart Array Gen9 PCI ID's (Tomas Henzl) [862713]
- [treewide] Convert retrun typos to return (Tomas Henzl) [862713]
- [scsi] hpsa: fix warning with smp_processor_id() in preemptible (Tomas Henzl) [862713]
- [scsi] hpsa: remove unneeded variable (Tomas Henzl) [862713]
- [scsi] hpsa: fix a race in cmd_free/scsi_done (Tomas Henzl) [862713]

* Thu Nov 07 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-45.el7]
- [ethernet] tg3: remove unnecessary pci_set_drvdata() (Ivan Vecera) [1024060]
- [ethernet] tg3: Miscellaneous conversions to ETH_ALEN (Ivan Vecera) [1024060]
- [ethernet] tg3: use phylib when robo switch is in use (Ivan Vecera) [1024060]
- [netdrv] ssb: provide phy address for Gigabit Ethernet driver (Ivan Vecera) [1024060]
- [ethernet] tg3: add support a phy at an address different than 01 (Ivan Vecera) [1024060]
- [ethernet] tg3: Update version to 3.134 (Ivan Vecera) [1024060]
- [ethernet] tg3: Remove unnecessary spinlock (Ivan Vecera) [1024060]
- [ethernet] tg3: Appropriately classify interrupts during request_irq (Ivan Vecera) [1024060]
- [ethernet] tg3: Remove redundant if check (Ivan Vecera) [1024060]
- [ethernet] tg3: Remove if 0'd code (Ivan Vecera) [1024060]
- [ethernet] tg3: LED in shared mode does not blink during traffic (Ivan Vecera) [1024060]
- [ethernet] tg3: Add support for new 577xx device ids (Ivan Vecera) [1024060]
- [ethernet] tg3: Add function tg3_phy_shdw_write() (Ivan Vecera) [1024060]
- [ethernet] tg3: Use pci_dev pm_cap (Ivan Vecera) [1024060]
- [ethernet] tg3: Expand led off fix to include 5720 (Ivan Vecera) [1024060]
- [s390] cio: Introduce on-close CHSC IOCTLs (Hendrik Brueckner) [1022446]
- [s390] cio: Make /dev/chsc a single-open device (Hendrik Brueckner) [1022442]
- [s390] cio: Introduce generic synchronous CHSC IOCTL (Hendrik Brueckner) [1022441]
- [s390] sclp: Add SCLP character device driver (Hendrik Brueckner) [1022425]
- [virt] kvm: Create non-coherent DMA registeration (Alex Williamson) [1025470]
- [virt] kvm: Convert iommu_flags to iommu_noncoherent (Alex Williamson) [1025470]
- [virt] kvm: Add VFIO device (Alex Williamson) [1025470]
- [vfio] vfio_iommu_type1: fix bug caused by break in nested loop (Alex Williamson) [1025468]
- [vfio] fix documentation more (Alex Williamson) [1025468]
- [vfio] vfio-pci: PCI hot reset interface (Alex Williamson) [1025468]
- [vfio] vfio-pci: Test for extended config space (Alex Williamson) [1025468]
- [vfio] vfio-pci: Use fdget() rather than eventfd_fget() (Alex Williamson) [1025468]
- [vfio] Add O_CLOEXEC flag to vfio device fd (Alex Williamson) [1025468]
- [vfio] use get_unused_fd_flags(0) instead of get_unused_fd() (Alex Williamson) [1025468]
- [vfio] add external user support (Alex Williamson) [1025468]
- [vfio] fix documentation (Alex Williamson) [1025468]
- [block] blk-throttle: Enable hierarchy even when sane mount flag is not specified (Vivek Goyal) [1015648]
- [block] blk-throttle: implement proper hierarchy support (Vivek Goyal) [1015648]
- [block] blk-throttle: implement throtl_grp->has_rules[] (Vivek Goyal) [1015648]
- [block] blk-throttle: Account for child group's start time in parent while bio climbs up (Vivek Goyal) [1015648]
- [block] blk-throttle: add throtl_qnode for dispatch fairness (Vivek Goyal) [1015648]
- [block] blk-throttle: make throtl_pending_timer_fn() ready for hierarchy (Vivek Goyal) [1015648]
- [block] blk-throttle: make tg_dispatch_one_bio() ready for hierarchy (Vivek Goyal) [1015648]
- [block] blk-throttle: make blk_throtl_bio() ready for hierarchy (Vivek Goyal) [1015648]
- [block] blk-throttle: make blk_throtl_drain() ready for hierarchy (Vivek Goyal) [1015648]
- [block] blk-throttle: dispatch from throtl_pending_timer_fn() (Vivek Goyal) [1015648]
- [block] blk-throttle: implement dispatch looping (Vivek Goyal) [1015648]
- [block] blk-throttle: separate out throtl_service_queue->pending_timer from throtl_data->dispatch_work (Vivek Goyal) [1015648]
- [block] blk-throttle: set REQ_THROTTLED from throtl_charge_bio() and gate stats update with it (Vivek Goyal) [1015648]
- [block] blk-throttle: move bio_lists[], implement sq_to_tg(), sq_to_td() and throtl_log() (Vivek Goyal) [1015648]
- [block] blk-throttle: add throtl_service_queue->parent_sq (Vivek Goyal) [1015648]
- [block] blk-throttle: generalize update_disptime optimization in blk_throtl_bio() (Vivek Goyal) [1015648]
- [block] blk-throttle: move bio_lists[] blk-throttle: dispatch to throtl_data->service_queue.bio_lists[] (Vivek Goyal) [1015648]
- [block] blk-throttle: move bio_lists[] and friends to throtl_service_queue (Vivek Goyal) [1015648]
- [block] blk-throttle: add throtl_grp->service_queue (Vivek Goyal) [1015648]
- [block] blk-throttle: reorganize throtl_service_queue passed around as argument (Vivek Goyal) [1015648]
- [block] blk-throttle: pass around throtl_service_queue instead of throtl_data (Vivek Goyal) [1015648]
- [block] blk-throttle: add backlink pointer from throtl_grp to throtl_data (Vivek Goyal) [1015648]
- [block] blk-throttle: simplify throtl_grp flag handling (Vivek Goyal) [1015648]
- [block] blk-throttle: rename throtl_rb_root to throtl_service_queue (Vivek Goyal) [1015648]
- [block] blk-throttle: remove pointless throtl_nr_queued() optimizations (Vivek Goyal) [1015648]
- [block] blk-throttle: relocate throtl_schedule_delayed_work() (Vivek Goyal) [1015648]
- [block] blk-throttle: collapse throtl_dispatch() into the work function (Vivek Goyal) [1015648]
- [block] blk-throttle: remove deferred config application mechanism (Vivek Goyal) [1015648]
- [block] blk-throttle: remove spurious throtl_enqueue_tg() call from throtl_select_dispatch() (Vivek Goyal) [1015648]
- [block] blkcg: move bulk of blkcg_gq release operations to the RCU callback (Vivek Goyal) [1015648]
- [block] blkcg: invoke blkcg_policy->pd_init() after parent is linked (Vivek Goyal) [1015648]
- [block] blkcg: implement blkg_for_each_descendant_post() (Vivek Goyal) [1015648]
- [block] blkcg: move blkg_for_each_descendant_pre() to block/blk-cgroup.h (Vivek Goyal) [1015648]
- [block] blkcg: fix error return path in blkg_create() (Vivek Goyal) [1015648]
- [char] ipmi: Add MODULE_ALIAS for autoloading ipmi driver on ACPI systems (Shyam Iyer) [844867]

* Wed Nov 06 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-44.el7]
- [security] keys: Fix UID check in keyctl_get_persistent() (David Howells) [991110]
- [security] keys: fix error return code in big_key_instantiate() (David Howells) [991110]
- [powerpc] tm: Switch out userspace PPR and DSCR sooner (Steve Best) [1016823]
- [virt] kvm: fix KVM_SET_XCRS loop (Paolo Bonzini) [1007897]
- [virt] kvm: fix KVM_SET_XCRS for CPUs that do not support XSAVE (Paolo Bonzini) [1007897]
- [virt] kvm: only copy XSAVE state for the supported features (Paolo Bonzini) [1007897]
- [virt] kvm: prevent setting unsupported XSAVE states (Paolo Bonzini) [1007897]
- [virt] kvm: mask unsupported XSAVE entries from leaf 0Dh index 0 (Paolo Bonzini) [1007897]
- [ethernet] bnx2x: remove unnecessary pci_set_drvdata() (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Add ndo_get_phys_port_id support (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Change variable type to bool (Michal Schmidt) [1022068]
- [ethernet] bnx2x: skb_is_gso_v6() requires skb_is_gso() (Michal Schmidt) [1022068]
- [ethernet] bnx2x: use pcie_get_minimum_link() (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Add support for EXTPHY2 LED mode (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Change function prototype (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Don't disable/enable SR-IOV when loading (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Correct VF driver info (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Test nvram when interface is down (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Staticize local symbols (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Disable VF access on PF removal (Michal Schmidt) [1022068]
- [ethernet] bnx2x: prevent FW assert on low mem during unload (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Set NETIF_F_HIGHDMA unconditionally (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Don't pretend during register dump (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Lock DMAE when used by statistic flow (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Prevent null pointer dereference on error flow (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix config when SR-IOV and iSCSI are enabled (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix Coalescing configuration (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Unlock VF-PF channel on MAC/VLAN config error (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Prevent an illegal pointer dereference during panic (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix Maximum CoS estimation for VFs (Michal Schmidt) [1022068]
- [ethernet] bnx2x: record rx queue for LRO packets (Michal Schmidt) [1022068]
- [ethernet] bnx2x: handle known but unsupported VF messages (Michal Schmidt) [1022068]
- [ethernet] bnx2x: prevent masked MCP parities from appearing (Michal Schmidt) [1022068]
- [ethernet] bnx2x: prevent masking error from cnic (Michal Schmidt) [1022068]
- [ethernet] bnx2x: add missing VF resource allocation during init (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix support for VFs on some PFs (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Prevent mistaken hangup between driver & FW (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix 848xx duplex settings (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Specific Active-DAC is not detected on 57810 (Michal Schmidt) [1022068]
- [ethernet] bnx2x: 57840 non-external loopback test fail on 1G (Michal Schmidt) [1022068]
- [ethernet] bnx2x: KR2 disablement fix (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Generalize KR work-around (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix bnx2i and bnx2fc regressions (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Use pci_dev pm_cap (Michal Schmidt) [1022068]
- [ethernet] bnx2x: avoid atomic allocations during initialization (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Fix configuration of doorbell block (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Restore a call to config_init (Michal Schmidt) [1022068]
- [ethernet] bnx2x: fix broken compilation with CONFIG_BNX2X_SRIOV is not set (Michal Schmidt) [1022068]
- [ethernet] bnx2x: Add missing braces in bnx2x:bnx2x_link_initialize (Michal Schmidt) [1022068]
- [ethernet] bnx2x: VF RSS support - VF side (Michal Schmidt) [1022068]
- [ethernet] bnx2x: VF RSS support - PF side (Michal Schmidt) [1022068]
- [virt] hyperv-fb: add pci stub (Gerd Hoffmann) [1019185]
- [ethernet] ixgbevf: move API neg to reset path (Andy Gospodarek) [1023107]
- [ethernet] bna: firmware update to 3.2.1.1 (Ivan Vecera) [1007080]
- [fs] nfs: Fix a missing initialisation when reading the SELinux label (Jeff Layton) [1019591]
- [fs] nfs: fix oops when trying to set SELinux label (Jeff Layton) [1019591]
- [ethernet] r8169: remove unnecessary pci_set_drvdata() (Ivan Vecera) [1025463]
- [ethernet] r8169: fix invalid register dump (Ivan Vecera) [1025463]
- [ethernet] r8169: remember WOL preferences on driver load (Ivan Vecera) [1025463]
- [ethernet] r8169, sis190: remove unnecessary length check (Ivan Vecera) [1025463]
- [ethernet] r8169: remove "PHY reset until link up" log spam (Ivan Vecera) [1025463]
- [ethernet] r8169: fix lockdep warning when removing interface (Ivan Vecera) [1025463]
- [ethernet] r8169: add a new chip for RTL8411 (Ivan Vecera) [1025463]
- [ethernet] be2net: Make lancer_wait_ready() static (Ivan Vecera) [1025412]
- [ethernet] be2net: Remove interface type (Ivan Vecera) [1025412]
- [ethernet] be2net: add support for ndo_busy_poll (Ivan Vecera) [1025412]
- [ethernet] be2net: Warn users of possible broken functionality on BE2 cards with very old FW versions with latest driver (Ivan Vecera) [1025412]
- [ethernet] be2net: remove unnecessary pci_set_drvdata() (Ivan Vecera) [1025412]
- [ethernet] be2net: Rework PCIe error report log messaging (Ivan Vecera) [1025412]
- [ethernet] be2net: change the driver version number to 4.9.224.0 (Ivan Vecera) [1025412]
- [ethernet] be2net: Display RoCE specific counters in ethtool -S (Ivan Vecera) [1025412]
- [ethernet] be2net: Call version 2 of GET_STATS ioctl for Skyhawk-R (Ivan Vecera) [1025412]
- [ethernet] be2net: add a counter for pkts dropped in xmit path (Ivan Vecera) [1025412]
- [ethernet] be2net: fix adaptive interrupt coalescing (Ivan Vecera) [1025412]
- [ethernet] be2net: call ENABLE_VF cmd for Skyhawk-R too (Ivan Vecera) [1025412]
- [ethernet] be2net: Create single TXQ on BE3-R 1G ports (Ivan Vecera) [1025412]
- [ethernet] be2net: pass if_id for v1 and V2 versions of TX_CREATE cmd (Ivan Vecera) [1025412]
- [ethernet] be2net: Call be_vf_setup() even when VFs are enbaled from previous load (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix to display the VLAN priority for a VF (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix to configure VLAN priority for a VF interface (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix to allow VLAN configuration on VF interfaces (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix number of VLANs supported in UMC mode for BE3-R (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix VLAN promiscuous mode programming (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix the size of be_nic_res_desc structure (Ivan Vecera) [1025412]
- [ethernet] be2net: Fix to prevent Tx stall on SH-R when packet size < 32 (Ivan Vecera) [1025412]
- [ethernet] be2net: Remove extern from function prototypes (Ivan Vecera) [1025412]
- [ethernet] be2net: missing variable initialization (Ivan Vecera) [1025412]
- [drm] cirrus: do not attempt to acquire a reservation while in an interrupt handler (Gerd Hoffmann) [1017433]
- [drm] cirrus: Invalidate page tables when pinning a BO (Gerd Hoffmann) [1017433]
- [virt] kvm: introduce guest count uevent (Paolo Bonzini) [1004799]
- [ata] libahci: fix turning on LEDs in ahci_start_port() (David Milburn) [1024388]
- [kernel] audit: do not reject all AUDIT_INODE filter types (Richard Guy Briggs) [985971]
- [fs] fuse: drop dentry on failed revalidate (Brian Foster) [1006514]
- [fs] fuse: clean up return in fuse_dentry_revalidate() (Brian Foster) [1006514]
- [fs] fuse: use d_materialise_unique() (Brian Foster) [1006514]
- [fs] sysfs: use check_submounts_and_drop() (Brian Foster) [1006514]
- [fs] nfs: use check_submounts_and_drop() (Brian Foster) [1006514]
- [fs] gfs2: use check_submounts_and_drop() (Brian Foster) [1006514]
- [fs] vfs: check unlinked ancestors before mount (Brian Foster) [1006514]
- [fs] vfs: check submounts and drop atomically (Brian Foster) [1006514]
- [fs] vfs: add d_walk() (Brian Foster) [1006514]
- [fs] vfs: restructure d_genocide() (Brian Foster) [1006514]
- [powerpc] Only save/restore SDR1 if in hypervisor mode (Steve Best) [1018639]
- [wireless] brcmsmac: Further reduce log spam from tx phy messages (John Green) [974223]
- [wireless] brcmsmac: Reduce log spam in heavy tx, make err print in debug (John Green) [974223]

* Wed Nov 06 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-43.el7]
- [misc] synchronize with upstream linux-3.10.y stable branch up to 3.10.17 (Veaceslav Falico) [1006938]

* Tue Nov 05 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-42.el7]
- [kernel] keys: align system_certificate_list (Jan Stancek) [985961]
- [security] keys: Fix keyring quota misaccounting on key replacement and unlink (David Howells) [1017806 991110]
- [security] keys: Fix a race between negating a key and reading the error set (David Howells) [991110]
- [security] keys: Make BIG_KEYS boolean (David Howells) [991110]
- [crypto] x.509: remove possible code fragility, enumeration values not handled (David Howells) [985961]
- [crypto] x.509: add module description and license (David Howells) [985961]
- [lib] mpi: add module description and license (David Howells) [985961]
- [security] keys: initialize root uid and session keyrings early (David Howells) [985961]
- [crypto] keys: verify a certificate is signed by a 'trusted' key (David Howells) [985961]
- [kernel] keys: Make the system 'trusted' keyring viewable by userspace (David Howells) [985961]
- [crypto] keys: Set the asymmetric-key type default search method (David Howells) [985961]
- [security] keys: Add a 'trusted' flag and a 'trusted only' flag (David Howells) [985961]
- [kernel] keys: Separate the kernel signature checking keyring from module signing (David Howells) [985961]
- [kernel] keys: Have make canonicalise the paths of the X.509 certs better to deduplicate (David Howells) [985961]
- [kernel] modsign: Load *.x509 files into kernel keyring (David Howells) [985961]
- [crypto] x.509: Remove certificate date checks (David Howells) [985961]
- [crypto] x.509: Handle certificates that lack an authorityKeyIdentifier field (David Howells) [985961]
- [crypto] x.509: Check the algorithm IDs obtained from parsing an X.509 certificate (David Howells) [985961]
- [crypto] x.509: Embed public_key_signature struct and create filler function (David Howells) [985961]
- [crypto] x.509: struct x509_certificate needs struct tm declaring (David Howells) [985961]
- [crypto] keys: Store public key algo ID in public_key_signature struct (David Howells) [985961]
- [crypto] keys: Split public_key_verify_signature() and make available (David Howells) [985961]
- [crypto] keys: Store public key algo ID in public_key struct (David Howells) [985961]
- [crypto] keys: Move the algorithm pointer array from x509 to public_key.c (David Howells) [985961]
- [crypto] keys: Rename public key parameter name arrays (David Howells) [985961]
- [security] keys: Add per-user_namespace registers for persistent per-UID kerberos caches (David Howells) [991110]
- [security] keys: Implement a big key type that can save to tmpfs (David Howells) [991110]
- [security] keys: Expand the capacity of a keyring (David Howells) [1014573 985961]
- [lib] assoc_array: Add a generic associative array implementation (David Howells) [1014573 985961]
- [security] keys: Drop the permissions argument from __keyring_search_one() (David Howells) [1014573 985961]
- [security] keys: Define a __key_get() wrapper to use rather than atomic_inc() (David Howells) [1014573 985961]
- [security] keys: Search for auth-key by name rather than target key ID (David Howells) [1014573 985961]
- [security] keys: Introduce a search context structure (David Howells) [1014573 985961]
- [security] keys: Consolidate the concept of an 'index key' for key access (David Howells) [1014573 985961]
- [security] keys: key_is_dead() should take a const key pointer argument (David Howells) [1014573 985961]
- [security] keys: Use bool in make_key_ref() and is_key_possessed() (David Howells) [1014573 985961]
- [security] keys: Skip key state checks when checking for possession (David Howells) [1014573 985961 991110]

* Fri Nov 01 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-41.el7]
- [net] bonding: ensure that TLB mode's active slave has correct mac filter (Veaceslav Falico) [1017573]
- [net] netfilter: synproxy: fix BUG_ON triggered by corrupt TCP packets (Jesper Brouer) [1015035]
- [net] proc_fs: print UIDs as unsigned int (Francesco Fusco) [996122]
- [net] ipv6: Unify {raw,udp}6_sock_seq_show (Francesco Fusco) [996122]
- [scsi] qla4xxx: Fix memory leak in func qla4_84xx_config_acb() (Chad Dupuis) [998557]
- [scsi] qla4xxx: 5.04.00.00.07.00-k0 (Chad Dupuis) [998557]
- [scsi] qla4xxx: Update driver version to 5.04.00-k1 (Chad Dupuis) [998557]
- [scsi] qla4xxx: Return error if minidump data collection fails (Chad Dupuis) [998557]
- [scsi] qla4xxx: Fix the minidump data collection check in for loop (Chad Dupuis) [998557]
- [scsi] qla4xxx: Add pex-dma support for capturing minidump (Chad Dupuis) [998557]
- [scsi] qla4xxx: Update driver version to 5.04.00-k0 (Chad Dupuis) [998557]
- [scsi] qla4xxx: Update Copyright header (Chad Dupuis) [998557]
- [scsi] qla4xxx: Implementation of ACB configuration during Loopback for ISP8042 (Chad Dupuis) [998557]
- [scsi] qla4xxx: Added support for ISP8042 (Chad Dupuis) [998557]
- [scsi] qla4xxx: Update driver version to 5.03.00-k11 (Chad Dupuis) [948123]
- [scsi] qla4xxx: Export more firmware info in sysfs (Chad Dupuis) [948123]
- [scsi] qla4xxx: Only BIOS boot target entries should be at index 0 and 1 (Chad Dupuis) [948123]
- [scsi] qla4xxx: discovery_parent_idx can be shown without any check (Chad Dupuis) [948123]
- [scsi] qla4xxx: Set IPv6 traffic class if device type is IPv6 (Chad Dupuis) [948123]
- [scsi] qla4xxx: Use discovery_parent_idx instead of discovery_parent_type (Chad Dupuis) [948123]
- [scsi] qla4xxx: Allow removal of failed session using logout (Chad Dupuis) [948123]
- [scsi] qla4xxx: Update driver version to 5.03.00-k10 (Chad Dupuis) [948118]
- [scsi] qla4xxx: Exporting new attrs for iscsi session and connection in sysfs (Chad Dupuis) [948118]
- [scsi] libiscsi: Add missing prints for session and connection sysfs attrs (Chad Dupuis) [948118]
- [scsi] libiscsi: Added new boot entries in the session sysfs (Chad Dupuis) [948118]
- [fs] nfs: inform the VM about pages being committed or unstable (Jerome Marchand) [1009508]
- [mm] vmscan: take page buffers dirty and locked state into account (Jerome Marchand) [1009508]
- [mm] vmscan: treat pages marked for immediate reclaim as zone congestion (Jerome Marchand) [1009508]
- [mm] vmscan: move direct reclaim wait_iff_congested into shrink_list (Jerome Marchand) [1009508]
- [mm] vmscan: set zone flags before blocking (Jerome Marchand) [1009508]
- [mm] vmscan: stall page reclaim after a list of pages have been processed (Jerome Marchand) [1009508]
- [mm] vmscan: stall page reclaim and writeback pages based on dirty/writepage pages encountered (Jerome Marchand) [1009508]
- [mm] vmscan: move logic from balance_pgdat() to kswapd_shrink_zone() (Jerome Marchand) [1009508]
- [mm] vmscan: check if kswapd should writepage once per pgdat scan (Jerome Marchand) [1009508]
- [mm] vmscan: block kswapd if it is encountering pages under writeback (Jerome Marchand) [1009508]
- [mm] vmscan: have kswapd writeback pages based on dirty pages encountered, not priority (Jerome Marchand) [1009508]
- [mm] vmscan: do not allow kswapd to scan at maximum priority (Jerome Marchand) [1009508]
- [mm] vmscan: decide whether to compact the pgdat based on reclaim progress (Jerome Marchand) [1009508]
- [mm] vmscan: flatten kswapd priority loop (Jerome Marchand) [1009508]
- [mm] vmscan: obey proportional scanning requirements for kswapd (Jerome Marchand) [1009508]
- [mm] vmscan: limit the number of pages kswapd reclaims at each priority (Jerome Marchand) [1009508]
- [iommu] Remove stack trace from broken irq remapping warning (Neil Horman) [1012860]
- [kernel] audit: remove newline accidentally added during session id helper refactor (Richard Guy Briggs) [1010438]
- [security] audit: suppress stock memalloc failure warnings since already managed (Richard Guy Briggs) [1016852]
- [kernel] ntp: Make periodic RTC update more reliable (Prarit Bhargava) [1010351]

* Wed Oct 30 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-40.el7]
- [virt] kvm/ppc/Book3S: Fix compile error in XICS emulation (Veaceslav Falico) [1006938]
- [block] rsxx: fix Kernel Panic caused by mapping Discards (Steve Best) [1013995]
- [block] rsxx: Moving pci_map_page to prevent overflow (Steve Best) [1011024]
- [block] rsxx: Handling failed pci_map_page on PowerPC and double free (Steve Best) [1011024]
- [block] rsxx: Adding in debugfs entries (Steve Best) [1002025]
- [block] rsxx: Fixes incorrect stats calculation (Steve Best) [1002025]
- [block] rsxx: Adding EEH check inside cregs timeout (Steve Best) [1002025]
- [block] rsxx: Adapter address space sanity check (Steve Best) [1002025]
- [block] rsxx: Fixes DLPAR add kernel panic if partition still mounted (Steve Best) [1002025]
- [block] rsxx: Changing the adapter name to the official name (Steve Best) [1002025]
- [block] rsxx: Adding in sync_start module paramenter (Steve Best) [1002025]
- [block] rsxx: Allow block size to be determined by configuration (Steve Best) [1002025]
- [block] rsxx: Fixes soft-lockup issues during DMAs (Steve Best) [1002025]
- [block] rsxx: Restructured DMA cancel scheme (Steve Best) [1002025]
- [block] rsxx: Individual workqueues for interruptible events (Steve Best) [1002025]
- [md] Fix skipping recovery for read-only arrays (Jes Sorensen) [1016694]
- [kernel] nohz: Include local CPU in full dynticks global kick (Jarod Wilson) [988015]
- [kernel] nohz: Optimize full dynticks's sched hooks with static keys (Jarod Wilson) [988015]
- [kernel] nohz: Optimize full dynticks state checks with static keys (Jarod Wilson) [988015]
- [kernel] nohz: Rename a few state variables (Jarod Wilson) [988015]
- [kernel] vtime: Always debug check snapshot source _before_ updating it (Jarod Wilson) [988015]
- [kernel] vtime: Always scale generic vtime accounting results (Jarod Wilson) [988015]
- [kernel] vtime: Optimize full dynticks accounting off case with static keys (Jarod Wilson) [988015]
- [kernel] vtime: Describe overriden functions in dedicated arch headers (Jarod Wilson) [988015]
- [kernel] hardirq: Split preempt count mask definitions (Jarod Wilson) [988015]
- [kernel] context_tracking: Split low level state headers (Jarod Wilson) [988015]
- [kernel] vtime: Fix racy cputime delta update (Jarod Wilson) [988015]
- [kernel] vtime: Remove a few unneeded generic vtime state checks (Jarod Wilson) [988015]
- [kernel] context_tracking: User/kernel broundary cross trace events (Jarod Wilson) [988015]
- [kernel] context_tracking: Optimize context switch off case with static keys (Jarod Wilson) [988015]
- [kernel] context_tracking: Optimize guest APIs off case with static key (Jarod Wilson) [988015]
- [kernel] context_tracking: Optimize main APIs off case with static key (Jarod Wilson) [988015]
- [kernel] context_tracking: Ground setup for static key use (Jarod Wilson) [988015]
- [kernel] context_tracking: Remove full dynticks' hacky dependency on wide context tracking (Jarod Wilson) [988015]
- [kernel] nohz: Only enable context tracking on full dynticks CPUs (Jarod Wilson) [988015]
- [kernel] context_tracking: Fix runtime CPU off-case (Jarod Wilson) [988015]
- [kernel] vtime: Update a few comments (Jarod Wilson) [988015]
- [kernel] context_tracking: Fix guest accounting with native vtime (Jarod Wilson) [988015]
- [kernel] sched: Consolidate open coded preemptible() checks (Jarod Wilson) [988015]
- [kernel] nohz: fix compile warning in tick_nohz_init() (Jarod Wilson) [988015]
- [kernel] nohz: Do not warn about unstable tsc unless user uses nohz_full (Jarod Wilson) [988015]
- [kernel] nohz: Remove obsolete check for full dynticks CPUs to be RCU nocbs (Jarod Wilson) [988015]
- [kernel] nohz: Warn if the machine can not perform nohz_full (Jarod Wilson) [988015]
- [md] raid5: avoid finding "discard" stripe (Jes Sorensen) [1023485]
- [md] raid5: set bio bi_vcnt 0 for discard request (Jes Sorensen) [1023485]
- [powerpc] make lorax work again (Steve Best) [1022797]

* Tue Oct 29 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-39.el7]
- [netdrv] cnic: Fix crash in cnic_bnx2x_service_kcq() (Maurizio Lombardi) [1011203]
- [scsi] bnx2fc: Bump version from 1.0.14 to 2.4.1 (Maurizio Lombardi) [1011211]
- [scsi] bnx2fc: hung task timeout warning observed when rmmod bnx2x with active FCoE targets (Maurizio Lombardi) [1011211]
- [scsi] bnx2fc: Fixed a SCSI CMD cmpl race condition between ABTS and CLEANUP (Maurizio Lombardi) [1011211]
- [scsi] Allow error handling timeout to be specified (Ewan Milne) [1020944]
- [scsi] be2iscsi: Bump driver version (Rob Evers) [726165]
- [scsi] be2iscsi: Fix SGL posting for unaligned ICD values (Rob Evers) [726165]
- [scsi] be2iscsi: Fix AER handling in driver (Rob Evers) [726165]
- [scsi] be2iscsi: Invalidate WRB in Abort/Reset Path (Rob Evers) [726165]
- [scsi] be2iscsi: Fix Insufficient Buffer Error returned in MBX Completion (Rob Evers) [726165]
- [scsi] be2iscsi: Fix log level for protocol specific logs (Rob Evers) [726165]
- [scsi] be2iscsi: Fix MSIx creation for SKH-R adapter (Rob Evers) [726165]
- [scsi] be2iscsi: Display Port Identifier for each iSCSI function (Rob Evers) [726165]
- [scsi] be2iscsi: Dispaly CID available for connection offload (Rob Evers) [726165]
- [scsi] be2iscsi: Fix chute cleanup during drivers unload (Rob Evers) [726165]
- [scsi] be2iscsi: Fix connection offload to support Dual Chute (Rob Evers) [726165]
- [scsi] be2iscsi: Fix CID allocation/freeing to support Dual chute mode (Rob Evers) [726165]
- [scsi] be2iscsi: Fix WRB_Q posting to support Dual Chute mode (Rob Evers) [726165]
- [scsi] be2iscsi: Fix SGL Initilization and posting Pages for Dual Chute (Rob Evers) [726165]
- [scsi] be2iscsi: Fix Template HDR support for Dual Chute mode (Rob Evers) [726165]
- [scsi] be2iscsi: Fix changes in ASYNC Path for SKH-R adapter (Rob Evers) [726165]
- [scsi] be2iscsi: Config parameters update for Dual Chute Support (Rob Evers) [726165]
- [scsi] be2iscsi: Fix soft lock up issue during UE or if FW taking time to respond (Rob Evers) [726165]
- [scsi] be2iscsi: Fix locking mechanism in Unsol Path (Rob Evers) [726165]
- [scsi] be2iscsi: Fix negotiated parameters upload to FW (Rob Evers) [726165]
- [scsi] be2iscsi: Fix repeated issue of MAC ADDR get IOCTL (Rob Evers) [726165]
- [scsi] be2iscsi: Fix the MCCQ count leakage (Rob Evers) [726165]
- [scsi] be2iscsi: Fix Template HDR IOCTL (Rob Evers) [726165]
- [scsi] lpfc: Update lpfc version for 8.3.7.31.1p driver release (Rob Evers) [726157]
- [scsi] lpfc: Fixed issue of task management commands having a fixed timeout (Rob Evers) [726157]
- [scsi] lpfc: Fixed inconsistent spin lock usage (Rob Evers) [726157]
- [scsi] lpfc: Fix driver's abort loop functionality to skip IOs already getting aborted (Rob Evers) [726157]
- [scsi] lpfc: Fixed failure to allocate SCSI buffer on PPC64 platform for SLI4 devices (Rob Evers) [726157]
- [scsi] lpfc: Fix WARN_ON when driver unloads (Rob Evers) [726157]
- [scsi] lpfc: Avoided making pci bar ioremap call during dual-chute WQ/RQ pci bar selection (Rob Evers) [726157]
- [scsi] lpfc: Fixed driver iocbq structure's iocb_flag field running out of space (Rob Evers) [726157]
- [scsi] lpfc: Fix crash on driver load due to cpu affinity logic (Rob Evers) [726157]
- [scsi] lpfc: Fixed logging format of setting driver sysfs attributes hard to interpret (Rob Evers) [726157]
- [scsi] lpfc: Fixed back to back RSCNs discovery failure (Rob Evers) [726157]
- [scsi] lpfc: Fixed race condition between BSG I/O dispatch and timeout handling (Rob Evers) [726157]
- [scsi] lpfc: Fixed function mode field defined too small for not recognizing dual-chute mode (Rob Evers) [726157]
- [scsi] lpfc: Back out data count, (residual fcfi_parm) fix for bad target (Rob Evers) [726157]
- [scsi] lpfc: Fixed mailbox memory leak (Rob Evers) [726157]
- [scsi] lpfc: Fix random errors using first burst (Rob Evers) [726157]
- [scsi] lpfc: Fixed not able to log informational messages at early stage of driver init time (Rob Evers) [726157]
- [scsi] lpfc: Fixed using unsafe linked list macro for walking and deleting linked list (Rob Evers) [726157]
- [scsi] lpfc: Removed obsolete fcp_eq_count and fcp_wq_count driver attributes (Rob Evers) [726157]
- [scsi] lpfc: Update copyrights for 8.3.41 modifications (Rob Evers) [726157]
- [scsi] lpfc: Fixed the format of some log message fields (Rob Evers) [726157]
- [scsi] lpfc: Add first burst support to driver (Rob Evers) [726157]
- [scsi] lpfc: Fixed not able to perform PCI function reset when board was not in online mode (Rob Evers) [726157]
- [scsi] lpfc: Fixed failure in setting SLI3 board mode (Rob Evers) [726157]
- [scsi] lpfc: Fixed SLI3 failing FCP write on check-condition no-sense with residual zero (Rob Evers) [726157]
- [scsi] lpfc: Fixed support for 128 byte WQEs (Rob Evers) [726157]
- [scsi] lpfc: Ensure driver properly zeros unused fields in SLI4 mailbox commands (Rob Evers) [726157]
- [scsi] lpfc: Fixed max value of lpfc_lun_queue_depth (Rob Evers) [726157]
- [scsi] lpfc: Fixed Receive Queue varied frame size handling (Rob Evers) [726157]
- [scsi] lpfc: Fix mailbox byteswap issue on PPC (Rob Evers) [726157]
- [scsi] lpfc: Fixed freeing of iocb when internal loopback times out (Rob Evers) [726157]
- [scsi] lpfc: Update Copyrights to 2013 for 8.3.38, 8.3.39, and 8.3.40 modifications (Rob Evers) [726157]
- [scsi] lpfc: Fixed a race condition between SLI host and port failed FCF rediscovery (Rob Evers) [726157]
- [scsi] lpfc: Fixed issue mailbox wait routine failed to issue dump memory mbox command (Rob Evers) [726157]
- [scsi] lpfc: Fixed system panic due to unsafe walking and deleting linked list (Rob Evers) [726157]
- [scsi] lpfc: Fixed FCoE connection list vlan identifier and add FCF list debug (Rob Evers) [726157]
- [scsi] lpfc: Clarified the behavior of the lpfc_max_luns module parameter (Rob Evers) [726157]
- [scsi] lpfc: Fix to allow OCM to report FEC status (Rob Evers) [726157]
- [scsi] lpfc: Fixed a missing return code in a logging message (Rob Evers) [726157]
- [scsi] lpfc: Fixed some logging message fields (Rob Evers) [726157]
- [scsi] lpfc: Fixed list corruption when lpfc_drain_tx runs (Rob Evers) [726157]
- [scsi] lpfc: Fix starting reference tag when calculating BG error (Rob Evers) [726157]
- [scsi] lpfc: Fix inconsistent list removal causes crash (Rob Evers) [726157]
- [scsi] lpfc: Fixed system panic during handling unsolicited receive buffer error condition (Rob Evers) [726157]
- [scsi] lpfc: Fix BlockGuard error checking (Rob Evers) [726157]
- [scsi] lpfc: Fixed crash during FCoE failover testing (Rob Evers) [726157]
- [scsi] lpfc: Fix lpfc_used_cpu to be more dynamic (Rob Evers) [726157]
- [scsi] megaraid_sas: Fix synchronization problem between sysPD IO path and AEN path (Tomas Henzl) [1019819]
- [scsi] megaraid_sas: fixes for few endianess issues (Tomas Henzl) [1019819]
- [scsi] megaraid_sas: addded support for big endian architecture (Tomas Henzl) [1005934]
- [scsi] megaraid_sas: Version and Changelog update (Tomas Henzl) [1005934]
- [scsi] megaraid_sas: Add High Availability clustering support using shared Logical Disks (Tomas Henzl) [1005934]
- [scsi] megaraid_sas: fix memory leak if SGL has zero length entries (Tomas Henzl) [1005934]
- [scsi] megaraid_sas: Changelog and driver version update (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Add support to differentiate between iMR vs MR Firmware (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Add support for Uneven Span PRL11 (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Add support for Extended MSI-x vectors for 12Gb/s controller (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Set IoFlags to enable Fast Path for JBODs for 12 Gb/s controllers (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Add support to display Customer branding details in syslog (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Add support for MegaRAID Fury (device ID-0x005f) 12Gb/s controllers (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Set IO request timeout value provided by OS timeout for Tape devices (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Free event detail memory without device ID check (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Update balance count in driver to be in sync of firmware (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Fix the interrupt mask for Gen2 controller (Tomas Henzl) [726228]
- [scsi] megaraid_sas: Return DID_ERROR for SCSI IO, when controller is in critical h/w error (Tomas Henzl) [726228]
- [scsi] Add 'eh_deadline' to limit SCSI EH runtime (Ewan Milne) [988042]
- [scsi] remove check for 'resetting' (Ewan Milne) [988042]
- [scsi] dc395: Move 'last_reset' into internal host structure (Ewan Milne) [988042]
- [scsi] tmscsim: Move 'last_reset' into host structure (Ewan Milne) [988042]
- [scsi] advansys: Remove 'last_reset' references (Ewan Milne) [988042]
- [scsi] dpt_i2o: return SCSI_MLQUEUE_HOST_BUSY when in reset (Ewan Milne) [988042]
- [scsi] dpt_i2o: Remove DPTI_STATE_IOCTL (Ewan Milne) [988042]

* Tue Oct 29 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-38.el7]
- [net] ip_output: do skb ufo init for peeked non ufo skb as well (Jiri Pirko) [1014599]
- [net] ip6_output: do skb ufo init for peeked non ufo skb as well (Jiri Pirko) [1014599]
- [net] udp6: respect IPV6_DONTFRAG sockopt in case there are pending frames (Jiri Pirko) [1014599]
- [net] ipv6: udp packets following an UFO enqueued packet need also be handled by UFO (Jiri Pirko) [1011931] {CVE-2013-4387}
- [net] bonding: combine pr_debugs in bond_set_dev_addr into one (Nikolay Aleksandrov) [1020621]
- [net] bonding: when cloning a MAC use NET_ADDR_STOLEN (Nikolay Aleksandrov) [1020621]
- [net] bonding: remove unnecessary dev_addr_from_first member (Nikolay Aleksandrov) [1020621]
- [net] netfilter: nf_conntrack: use RCU safe kfree for conntrack extensions (Jesper Brouer) [1010252]
- [net] tcp: TSQ can use a dynamic limit (Jiri Pirko) [998775]
- [net] tcp: TSO packets automatic sizing (Jiri Pirko) [998775]
- [security] selinux: fix selinuxfs policy file on big endian systems (Eric Paris) [839671]
- [powerpc] Fix memory hotplug with sparse vmemmap (Steve Best) [805181]
- [powerpc] mm: Mark Memory Resources as busy (Steve Best) [805181]
- [tools] perf/bench: Fix failing assertions in numa bench (Petr Holasek) [1011923]
- [hid] pantherlord: heap overflow flaw (Radomir Vrbovsky) [1000436] {CVE-2013-2892}
- [powerpc] tm: Turn interrupts hard off in tm_reclaim() (Steve Best) [1017135]
- [powerpc] tm: Clear MSR RI in non-recoverable TM code (Steve Best) [1017135]
- [powerpc] perf: Fix handling of FAB events (Steve Best) [1015439]

* Thu Oct 24 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-37.el7]
- [fs] xfs: remove dead code from xlog_recover_inode_pass2 (Dave Chinner) [1001861]
- [fs] xfs: = vs == typo in ASSERT() (Dave Chinner) [1001861]
- [fs] xfs: don't assert fail on bad inode numbers (Dave Chinner) [1001861]
- [fs] xfs: aborted buf items can be in the AIL (Dave Chinner) [1001861]
- [fs] xfs: factor all the kmalloc-or-vmalloc fallback allocations (Dave Chinner) [1001861]
- [fs] xfs: fix memory allocation failures with ACLs (Dave Chinner) [1001861]
- [fs] xfs: ensure we copy buffer type in da btree root splits (Dave Chinner) [1001861]
- [fs] xfs: set remote symlink buffer type for recovery (Dave Chinner) [1001861]
- [fs] xfs: recovery of swap extents operations for CRC filesystems (Dave Chinner) [1001861]
- [fs] xfs: swap extents operations for CRC filesystems (Dave Chinner) [1001861]
- [fs] xfs: check magic numbers in dir3 leaf verifier first (Dave Chinner) [1001861]
- [fs] xfs: fix some minor sparse warnings (Dave Chinner) [1001861]
- [fs] xfs: fix endian warning in xlog_recover_get_buf_lsn() (Dave Chinner) [1001861]
- [fs] xfs: XFS_MOUNT_QUOTA_ALL needed by userspace (Dave Chinner) [1001861]
- [fs] xfs: dtype changed xfs_dir2_sfe_put_ino to xfs_dir3_sfe_put_ino (Dave Chinner) [1001861]
- [fs] xfs: Fix wrong flag ASSERT in xfs_attr_shortform_getvalue (Dave Chinner) [1001861]
- [fs] xfs: finish removing IOP_* macros (Dave Chinner) [1001861]
- [fs] xfs: inode log reservations are too small (Dave Chinner) [1001861]
- [fs] xfs: check correct status variable for xfs_inobt_get_rec() call (Dave Chinner) [1001861]
- [fs] xfs: inode buffers may not be valid during recovery readahead (Dave Chinner) [1001861]
- [fs] xfs: check LSN ordering for v5 superblocks during recovery (Dave Chinner) [1001861]
- [fs] xfs: btree block LSN escaping to disk uninitialised (Dave Chinner) [1001861]
- [fs] xfs: Assertion failed: first <= last && last < BBTOB(bp->b_length), file: fs/xfs/xfs_trans_buf.c, line: 568 (Dave Chinner) [1001861]
- [fs] xfs: fix bad dquot buffer size in log recovery readahead (Dave Chinner) [1001861]
- [fs] xfs: don't account buffer cancellation during log recovery readahead (Dave Chinner) [1001861]
- [fs] xfs: check for underflow in xfs_iformat_fork() (Dave Chinner) [1001861]
- [fs] xfs: xfs_dir3_sfe_put_ino can be static (Dave Chinner) [1001861]
- [fs] xfs: introduce object readahead to log recovery (Dave Chinner) [1001861]
- [fs] xfs: Simplify xfs_ail_min() with list_first_entry_or_null() (Dave Chinner) [1001861]
- [fs] xfs: Register hotcpu notifier after initialization (Dave Chinner) [1001861]
- [fs] xfs: add xfs sb v4 support for dirent filetype field (Dave Chinner) [1001861]
- [fs] xfs: Add write support for dirent filetype field (Dave Chinner) [1001861]
- [fs] xfs: Add read-only support for dirent filetype field (Dave Chinner) [1001861]
- [fs] xfs: Add support for the Q_XGETQSTATV (Dave Chinner) [1001861]
- [fs] quota: Add a new quotactl command Q_XGETQSTATV (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_mountfs() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_sb_quiet_read_verify() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xlog_recover_do_dquot_buffer() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_log_unmount_write() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_ifree_cluster() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_ialloc_ag_select() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_extent_busy_update_extent() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_setsize_buftarg_early() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_bmap_punch_delalloc_range() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_bmap_last_before() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_bmap_validate_ret() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_bmap_count_tree() (Dave Chinner) [1001861]
- [fs] xfs: rename bio_add_buffer() to xfs_bio_add_buffer() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xlog_find_head() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xlog_recover_buffer_pass2() (Dave Chinner) [1001861]
- [fs] xfs: remove two unused macro definitions in xfs_linux.h (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_btree_get_iroot() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_iroot_realloc() (Dave Chinner) [1001861]
- [fs] xfs: remove one blank line in xfs_btree_make_block_unfull() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xlog_write_setup_copy() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_mod_incore_sb_unlocked() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_btree_lookup() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_buf_free() (Dave Chinner) [1001861]
- [fs] xfs: fix the comment of xfs_check_sizes() (Dave Chinner) [1001861]
- [fs] xfs: use reference counts to free clean buffer items (Dave Chinner) [1001861]
- [fs] xfs: split the CIL lock (Dave Chinner) [1001861]
- [fs] xfs: Combine CIL insert and prepare passes (Dave Chinner) [1001861]
- [fs] xfs: avoid CIL allocation during insert (Dave Chinner) [1001861]
- [fs] xfs: Reduce allocations during CIL insertion (Dave Chinner) [1001861]
- [fs] xfs: return log item size in IOP_SIZE (Dave Chinner) [1001861]
- [fs] xfs: free bp in xlog_find_tail() error path (Dave Chinner) [1001861]
- [fs] xfs: free bp in xlog_find_zeroed() error path (Dave Chinner) [1001861]
- [fs] xfs: avoid double-free in xfs_attr_node_addname (Dave Chinner) [1001861]
- [fs] xfs: call roundup_64() to calculate the min_logblks (Dave Chinner) [1001861]
- [fs] xfs: Validate log space at mount time (Dave Chinner) [1001861]
- [fs] xfs: Add xfs_log_rlimit.c (Dave Chinner) [1001861]
- [fs] xfs: Refactor xfs_ticket_alloc() to extract a new helper (Dave Chinner) [1001861]
- [fs] xfs: Get rid of all XFS_XXX_LOG_RES() macro (Dave Chinner) [1001861]
- [fs] xfs: refactor xfs_trans_reserve() interface (Dave Chinner) [1001861]
- [fs] xfs: Make writeid transaction use tr_writeid (Dave Chinner) [1001861]
- [fs] xfs: Introduce tr_fsyncts to m_reservation (Dave Chinner) [1001861]
- [fs] xfs: Introduce a new structure to hold transaction reservation items (Dave Chinner) [1001861]
- [fs] xfs: make struct xfs_perag kernel only (Dave Chinner) [1001861]
- [fs] xfs: move kernel specific type definitions to xfs.h (Dave Chinner) [1001861]
- [fs] xfs: xfs_filestreams.h doesn't need __KERNEL__ (Dave Chinner) [1001861]
- [fs] xfs: remove __KERNEL__ check from xfs_dir2_leaf.c (Dave Chinner) [1001861]
- [fs] xfs: remove __KERNEL__ from debug code (Dave Chinner) [1001861]
- [fs] xfs: kill __KERNEL__ check for debug code in allocation code (Dave Chinner) [1001861]
- [fs] xfs: don't special case shared superblock mounts (Dave Chinner) [1001861]
- [fs] xfs: consolidate extent swap code (Dave Chinner) [1001861]
- [fs] xfs: consolidate xfs_utils.c (Dave Chinner) [1001861]
- [fs] xfs: consolidate xfs_rename.c (Dave Chinner) [1001861]
- [fs] xfs: kill xfs_vnodeops.[ch] (Dave Chinner) [1001861]
- [fs] xfs: fix issues that cause userspace warnings (Dave Chinner) [1001861]
- [fs] xfs: minor cleanups (Dave Chinner) [1001861]
- [fs] xfs: create xfs_bmap_util.[ch] (Dave Chinner) [1001861]
- [fs] xfs: introduce xfs_sb.c for sharing with libxfs (Dave Chinner) [1001861]
- [fs] xfs: split out the remote symlink handling (Dave Chinner) [1001861]
- [fs] xfs: split out attribute fork truncation code into separate file (Dave Chinner) [1001861]
- [fs] xfs: split out attribute listing code into separate file (Dave Chinner) [1001861]
- [fs] xfs: reshuffle dir2 definitions around for userspace (Dave Chinner) [1001861]
- [fs] xfs: move getdents code into it's own file (Dave Chinner) [1001861]
- [fs] xfs: introduce xfs_inode_buf.c for inode buffer operations (Dave Chinner) [1001861]
- [fs] xfs: move unrelated definitions out of xfs_inode.h (Dave Chinner) [1001861]
- [fs] xfs: move inode fork definitions to a new header file (Dave Chinner) [1001861]
- [fs] xfs: split out transaction reservation code (Dave Chinner) [1001861]
- [fs] xfs: sync minor header differences needed by userspace (Dave Chinner) [1001861]
- [fs] xfs: introduce xfs_quota_defs.h (Dave Chinner) [1001861]
- [fs] xfs: introduce xfs_rtalloc_defs.h (Dave Chinner) [1001861]
- [fs] xfs: split out on-disk transaction definitions (Dave Chinner) [1001861]
- [fs] xfs: separate icreate log format definitions from xfs_icreate_item.h (Dave Chinner) [1001861]
- [fs] xfs: separate dquot on disk format definitions out of xfs_quota.h (Dave Chinner) [1001861]
- [fs] xfs: split out EFI/EFD log item format definition (Dave Chinner) [1001861]
- [fs] xfs: split out buf log item format definitions (Dave Chinner) [1001861]
- [fs] xfs: split out inode log item format definition (Dave Chinner) [1001861]
- [fs] xfs: separate out log format definitions (Dave Chinner) [1001861]
- [fs] xfs: di_flushiter considered harmful (Dave Chinner) [1001861]
- [fs] xfs: Start using pquotaino from the superblock (Dave Chinner) [1001861]
- [fs] xfs: Initialize all quota inodes to be NULLFSINO (Dave Chinner) [1001861]
- [fs] xfs: Fix a deadlock in xfs_log_commit_cil() code path (Dave Chinner) [1001861]
- [fs] xfs: fix assertion failure in xfs_vm_write_failed() (Dave Chinner) [1001861]
- [fs] xfs: Fix the logic check for all quotas being turned off (Dave Chinner) [1001861]
- [fs] xfs: Add pquota fields where gquota is used (Dave Chinner) [1001861]
- [fs] xfs: fix sgid inheritance for subdirectories inheriting default acls (Dave Chinner) [1001861]
- [fs] xfs: dquot log reservations are too small (Dave Chinner) [1001861]
- [fs] xfs: remove local fork format handling from xfs_bmapi_write() (Dave Chinner) [1001861]
- [fs] xfs: use get_unused_fd_flags(0) instead of get_unused_fd() (Dave Chinner) [1001861]
- [fs] xfs: clean up unused codes at xfs_bulkstat() (Dave Chinner) [1001861]
- [fs] xfs: use XFS_BMAP_BMDR_SPACE vs. XFS_BROOT_SIZE_ADJ (Dave Chinner) [1001861]
- [fs] xfs: Remove incore use of XFS_OQUOTA_ENFD and XFS_OQUOTA_CHKD (Dave Chinner) [1001861]
- [fs] xfs: Change xfs_dquot_acct to be a 2-dimensional array (Dave Chinner) [1001861]
- [fs] xfs: Code cleanup and removal of some typedef usage (Dave Chinner) [1001861]
- [fs] xfs: Replace macro XFS_DQ_TO_QIP with a function (Dave Chinner) [1001861]
- [fs] xfs: Replace macro XFS_DQUOT_TREE with a function (Dave Chinner) [1001861]
- [fs] xfs: Define a new function xfs_is_quota_inode() (Dave Chinner) [1001861]
- [fs] xfs: implement inode change count (Dave Chinner) [1001861]
- [fs] xfs: Use inode create transaction (Dave Chinner) [1001861]
- [fs] xfs: Inode create item recovery (Dave Chinner) [1001861]
- [fs] xfs: Inode create transaction reservations (Dave Chinner) [1001861]
- [fs] xfs: Inode create log items (Dave Chinner) [1001861]
- [fs] xfs: Introduce an ordered buffer item (Dave Chinner) [1001861]
- [fs] xfs: Introduce ordered log vector support (Dave Chinner) [1001861]
- [fs] xfs: xfs_ifree doesn't need to modify the inode buffer (Dave Chinner) [1001861]
- [fs] xfs: don't do IO when creating an new inode (Dave Chinner) [1001861]
- [fs] xfs: don't use speculative prealloc for small files (Dave Chinner) [1001861]
- [fs] xfs: plug directory buffer readahead (Dave Chinner) [1001861]
- [fs] xfs: add pluging for bulkstat readahead (Dave Chinner) [1001861]
- [fs] xfs: Remove dead function prototype xfs_sync_inode_grab() (Dave Chinner) [1001861]
- [fs] xfs: Remove the left function variable from xfs_ialloc_get_rec() (Dave Chinner) [1001861]
- [fs] xfs: check on-disk (not incore) btree root size in dfrag.c (Dave Chinner) [1001861]
- [fs] xfs: Remove XFS_MOUNT_RETERR (Dave Chinner) [1001861]
- [fs] xfs: Remove two dead transaction log reservaion macros (Dave Chinner) [1001861]
- [fs] xfs: return FIEMAP_EXTENT_UNKNOWN for delayed allocation extent (Dave Chinner) [1001861]
- [fs] xfs: fix the symbolic link assert in xfs_ifree (Dave Chinner) [1001861]
- [fs] xfs: Remove struct xfs_chash from xfs_mount (Dave Chinner) [1001861]
- [fs] xfs: Don't keep silent if sunit/swidth can not be changed via mount (Dave Chinner) [1001861]
- [fs] xfs: Remove redundant error variable from xfs_growfs_data_private() (Dave Chinner) [1001861]
- [fs] xfs: Convert use of typedef ctl_table to struct ctl_table (Dave Chinner) [1001861]
- [fs] xfs: Avoid pathological backwards allocation (Dave Chinner) [1001861]

* Wed Oct 23 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-36.el7]
- [fs] btrfs: create the uuid tree on remount rw (Eric Sandeen) [1010071]
- [fs] btrfs: change extent-same to copy entire argument struct (Eric Sandeen) [1010071]
- [fs] btrfs: dir_inode_operations should use btrfs_update_time also (Eric Sandeen) [1010071]
- [fs] btrfs: add btrfs prefix to kernel log output (Eric Sandeen) [1010071]
- [fs] btrfs: refuse to remount read-write after abort (Eric Sandeen) [1010071]
- [fs] btrfs: don't leak transaction in btrfs_sync_file() (Eric Sandeen) [1010071]
- [fs] btrfs: add the missing mutex unlock in write_all_supers() (Eric Sandeen) [1010071]
- [fs] btrfs: iput inode on allocation failure (Eric Sandeen) [1010071]
- [fs] btrfs: remove space_info->reservation_progress (Eric Sandeen) [1010071]
- [fs] btrfs: kill delay_iput arg to the wait_ordered functions (Eric Sandeen) [1010071]
- [fs] btrfs: fix worst case calculator for space usage (Eric Sandeen) [1010071]
- [fs] btrfs: improve replacing nocow extents (Eric Sandeen) [1010071]
- [fs] btrfs: drop dir i_size when adding new names on replay (Eric Sandeen) [1010071]
- [fs] btrfs: replay dir_index items before other items (Eric Sandeen) [1010071]
- [fs] btrfs: check roots last log commit when checking if an inode has been logged (Eric Sandeen) [1010071]
- [fs] btrfs: actually log directory we are fsync()'ing (Eric Sandeen) [1010071]
- [fs] btrfs: actually limit the size of delalloc range (Eric Sandeen) [1010071]
- [fs] btrfs: allocate the free space by the existed max extent size when ENOSPC (Eric Sandeen) [1010071]
- [fs] btrfs: add lockdep and tracing annotations for uuid tree (Eric Sandeen) [1010071]
- [fs] btrfs: show compiled-in config features at module load time (Eric Sandeen) [1010071]
- [fs] btrfs: more efficient inode tree replace operation (Eric Sandeen) [1010071]
- [fs] btrfs: do not add replace target to the alloc_list (Eric Sandeen) [1010071]
- [fs] btrfs: fixup error handling in btrfs_reloc_cow (Eric Sandeen) [1010071]
- [fs] btrfs: optimize key searches in btrfs_search_slot (Eric Sandeen) [1010071]
- [fs] btrfs: don't use an async starter for most of our workers (Eric Sandeen) [1010071]
- [fs] btrfs: only update disk_i_size as we remove extents (Eric Sandeen) [1010071]
- [fs] btrfs: fix deadlock in uuid scan kthread (Eric Sandeen) [1010071]
- [fs] btrfs: stop refusing the relocation of chunk 0 (Eric Sandeen) [1010071]
- [fs] btrfs: fix memory leak of uuid_root in free_fs_info (Eric Sandeen) [1010071]
- [fs] btrfs: reuse kbasename helper (Eric Sandeen) [1010071]
- [fs] btrfs: return btrfs error code for dev excl ops err (Eric Sandeen) [1010071]
- [fs] btrfs: allow partial ordered extent completion (Eric Sandeen) [1010071]
- [fs] btrfs: convert all bug_ons in free-space-cache.c (Eric Sandeen) [1010071]
- [fs] btrfs: add support for asserts (Eric Sandeen) [1010071]
- [fs] btrfs: adjust the fs_devices->missing count on unmount (Eric Sandeen) [1010071]
- [fs] btrfs: don't check for root_refs == 0 twice (Eric Sandeen) [1010071]
- [fs] btrfs: fix for patch "cleanup: don't check the same thing twice" (Eric Sandeen) [1010071]
- [fs] btrfs: get rid of one BUG() in write_all_supers() (Eric Sandeen) [1010071]
- [fs] btrfs: allocate prelim_ref with a slab allocater (Eric Sandeen) [1010071]
- [fs] btrfs: pass gfp_t to __add_prelim_ref() to avoid always using GFP_ATOMIC (Eric Sandeen) [1010071]
- [fs] btrfs: fix race conditions in BTRFS_IOC_FS_INFO ioctl (Eric Sandeen) [1010071]
- [fs] btrfs: fix race between removing a dev and writing sbs (Eric Sandeen) [1010071]
- [fs] btrfs: remove ourselves from the cluster list under lock (Eric Sandeen) [1010071]
- [fs] btrfs: do not clear our orphan item runtime flag on eexist (Eric Sandeen) [1010071]
- [fs] btrfs: fix send to deal with sparse files properly (Eric Sandeen) [1010071]
- [fs] btrfs: fix printing of non NULL terminated string (Eric Sandeen) [1010071]
- [fs] btrfs: Use z to format size_t (Eric Sandeen) [1010071]
- [fs] btrfs: Do not truncate sector_t on 32-bit with CONFIG_LBDAF=y (Eric Sandeen) [1010071]
- [fs] btrfs: PAGE_CACHE_SIZE is already unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make btrfs_header_chunk_tree_uuid() return unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make btrfs_header_fsid() return unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make btrfs_dev_extent_chunk_tree_uuid() return unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make btrfs_device_fsid() return unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make btrfs_device_uuid() return unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Format mirror_num as int (Eric Sandeen) [1010071]
- [fs] btrfs: Format PAGE_SIZE as unsigned long (Eric Sandeen) [1010071]
- [fs] btrfs: Make BTRFS_DEV_REPLACE_DEVID an unsigned long long constant (Eric Sandeen) [1010071]
- [fs] btrfs: Remove superfluous casts from u64 to unsigned long long (Eric Sandeen) [1010071]
- [fs] btrfs: fix memory leak of orphan block rsv (Eric Sandeen) [1010071]
- [fs] btrfs: rollback btrfs_device fields on umount (Eric Sandeen) [1010071]
- [fs] btrfs: add alloc_fs_devices and switch to it (Eric Sandeen) [1010071]
- [fs] btrfs: add btrfs_alloc_device and switch to it (Eric Sandeen) [1010071]
- [fs] btrfs: find_next_devid: root -> fs_info (Eric Sandeen) [1010071]
- [fs] btrfs: don't allow the replace procedure on read only filesystems (Eric Sandeen) [1010071]
- [fs] btrfs: reset force_compress on btrfs_file_defrag failure (Eric Sandeen) [1010071]
- [fs] btrfs: use __u64 in exported user headers (Eric Sandeen) [1010071]
- [fs] btrfs: add mount option to force UUID tree checking (Eric Sandeen) [1010071]
- [fs] btrfs: check UUID tree during mount if required (Eric Sandeen) [1010071]
- [fs] btrfs: introduce uuid-tree-gen field (Eric Sandeen) [1010071]
- [fs] btrfs: fill UUID tree initially (Eric Sandeen) [1010071]
- [fs] btrfs: maintain subvolume items in the UUID tree (Eric Sandeen) [1010071]
- [fs] btrfs: create UUID tree if required (Eric Sandeen) [1010071]
- [fs] btrfs: support printing UUID tree elements (Eric Sandeen) [1010071]
- [fs] btrfs: introduce a tree for items that map UUIDs to something (Eric Sandeen) [1010071]
- [fs] btrfs: mark some local function as 'static' (Eric Sandeen) [1010071]
- [fs] btrfs: get rid of sparse warnings (Eric Sandeen) [1010071]
- [fs] btrfs: don't miss inode ref items in BTRFS_IOC_INO_LOOKUP (Eric Sandeen) [1010071]
- [fs] btrfs: add missing error code to BTRFS_IOC_INO_LOOKUP handler (Eric Sandeen) [1010071]
- [fs] btrfs: remove reduplicate check when disabling quota (Eric Sandeen) [1010071]
- [fs] btrfs: move btrfs_free_qgroup_config() out of spin_lock and fix comments (Eric Sandeen) [1010071]
- [fs] btrfs: fix oops when writing dirty qgroups to disk (Eric Sandeen) [1010071]
- [fs] btrfs: fix send issues related to inode number reuse (Eric Sandeen) [1010071]
- [fs] btrfs: separate out tests into their own directory (Eric Sandeen) [1010071]
- [fs] btrfs: avoid starting a transaction in the write path (Eric Sandeen) [1010071]
- [fs] btrfs: fix heavy delalloc related deadlock (Eric Sandeen) [1010071]
- [fs] btrfs: fix the error handling wrt orphan items (Eric Sandeen) [1010071]
- [fs] btrfs: don't allow a subvol to be deleted if it is the default subovl (Eric Sandeen) [1010071]
- [fs] btrfs: skip subvol entries when checking if we've created a dir already (Eric Sandeen) [1010071]
- [fs] btrfs: offline dedupe (Eric Sandeen) [1010071]
- [fs] btrfs: Introduce extent_read_full_page_nolock() (Eric Sandeen) [1010071]
- [fs] btrfs: btrfs_ioctl_clone, Move clone code into it's own function (Eric Sandeen) [1010071]
- [fs] btrfs: abtract out range locking in clone ioctl() (Eric Sandeen) [1010071]
- [fs] btrfs: fix possible memory leak in find_parent_nodes() (Eric Sandeen) [1010071]
- [fs] btrfs: return ENOSPC when target space is full (Eric Sandeen) [1010071]
- [fs] btrfs: don't ignore errors from btrfs_run_delayed_items (Eric Sandeen) [1010071]
- [fs] btrfs: fix inode leak on kmalloc failure in tree-log.c (Eric Sandeen) [1010071]
- [fs] btrfs: allow compressed extents to be merged during defragment (Eric Sandeen) [1010071]
- [fs] btrfs: add mount option to set commit interval (Eric Sandeen) [1010071]
- [fs] btrfs: stop using GFP_ATOMIC when allocating rewind ebs (Eric Sandeen) [1010071]
- [fs] btrfs: deal with enomem in the rewind path (Eric Sandeen) [1010071]
- [fs] btrfs: check our parent dir when doing a compare send (Eric Sandeen) [1010071]
- [fs] btrfs: handle errors when doing slow caching (Eric Sandeen) [1010071]
- [fs] btrfs: add missing error handling to read_tree_block (Eric Sandeen) [1010071]
- [fs] btrfs: Fix leak in __btrfs_map_block error path (Eric Sandeen) [1010071]
- [fs] btrfs: add missing error check to find_parent_nodes (Eric Sandeen) [1010071]
- [fs] btrfs: optimize function btrfs_read_chunk_tree (Eric Sandeen) [1010071]
- [fs] btrfs: don't bug_on when we fail when cleaning up transactions (Eric Sandeen) [1010071]
- [fs] btrfs: change how we queue blocks for backref checking (Eric Sandeen) [1010071]
- [fs] btrfs: check to see if we have an inline item properly (Eric Sandeen) [1010071]
- [fs] btrfs: fix what bits we clear when erroring out from delalloc (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup arguments to extent_clear_unlock_delalloc (Eric Sandeen) [1010071]
- [fs] btrfs: use BTRFS_SUPER_INFO_SIZE macro at btrfs_read_dev_super() (Eric Sandeen) [1010071]
- [fs] btrfs: cache the extent map struct when reading several pages (Eric Sandeen) [1010071]
- [fs] btrfs: batch the extent state operation when reading pages (Eric Sandeen) [1010071]
- [fs] btrfs: batch the extent state operation in the end io handle of the read page (Eric Sandeen) [1010071]
- [fs] btrfs: don't cache the csum value into the extent state tree (Eric Sandeen) [1010071]
- [fs] btrfs: add branch prediction hints in the read page end IO function (Eric Sandeen) [1010071]
- [fs] btrfs: remove unnecessary argument of bio_readpage_error() (Eric Sandeen) [1010071]
- [fs] btrfs: add missing mounting options in btrfs_show_options() (Eric Sandeen) [1010071]
- [fs] btrfs: use u64 for subvolid when parsing mount options (Eric Sandeen) [1010071]
- [fs] btrfs: add sanity checks regarding to parsing mount options (Eric Sandeen) [1010071]
- [fs] btrfs: fix memory leak when allocating pages for p/q stripes failed in raid56 (Eric Sandeen) [1010071]
- [fs] btrfs: fix and cleanup some error paths in raid56 (Eric Sandeen) [1010071]
- [fs] btrfs: don't bother autodefragging if our root is going away (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup reloc roots properly on error (Eric Sandeen) [1010071]
- [fs] btrfs: reset ret in record_one_backref (Eric Sandeen) [1010071]
- [fs] btrfs: fix get set label blocking against balance (Eric Sandeen) [1010071]
- [fs] btrfs: Print key type in decimal everywhere (Eric Sandeen) [1010071]
- [fs] btrfs: update delayed ref tracepoints (Eric Sandeen) [1010071]
- [fs] btrfs: btrfs_read_block_groups, Use enums to index (Eric Sandeen) [1010071]
- [fs] btrfs: Cleanup for using BTRFS_SETGET_STACK instead of raw convert (Eric Sandeen) [1010071]
- [fs] btrfs: set qgroup_ulist to be null after calling ulist_free() (Eric Sandeen) [1010071]
- [fs] btrfs: add missing error checks to add_data_references (Eric Sandeen) [1010071]
- [fs] btrfs: make errors in btrfs_num_copies less noisy (Eric Sandeen) [1010071]
- [fs] btrfs: make free space caching faster with many non-inline extent references (Eric Sandeen) [1010071]
- [fs] btrfs: fall back to global reservation when removing subvolumes (Eric Sandeen) [1010071]
- [fs] btrfs: optimize btrfs_lookup_extent_info() (Eric Sandeen) [1010071]
- [fs] btrfs: Release uuid_mutex for shrink during device delete (Eric Sandeen) [1010071]
- [fs] btrfs: set lockdep class before locking new extent buffer (Eric Sandeen) [1010071]
- [fs] btrfs: return -1 when lzo compression makes data bigger (Eric Sandeen) [1010071]
- [fs] btrfs: stop using GFP_ATOMIC for the tree mod log allocations (Eric Sandeen) [1010071]
- [fs] btrfs: treewide: Add __GFP_NOWARN to k.alloc calls with v.alloc fallbacks (Eric Sandeen) [1010071]
- [fs] btrfs: don't loop on large offsets in readdir (Eric Sandeen) [1010071]
- [fs] btrfs: check to see if root_list is empty before adding it to dead roots (Eric Sandeen) [1010071]
- [fs] btrfs: release both paths before logging dir/changed extents (Eric Sandeen) [1010071]
- [fs] btrfs: allow splitting of hole em's when dropping extent cache (Eric Sandeen) [1010071]
- [fs] btrfs: make sure the backref walker catches all refs to our extent (Eric Sandeen) [1010071]
- [fs] btrfs: fix backref walking when we hit a compressed extent (Eric Sandeen) [1010071]
- [fs] btrfs: do not offset physical if we're compressed (Eric Sandeen) [1010071]
- [fs] btrfs: fix extent buffer leak after backref walking (Eric Sandeen) [1010071]
- [fs] btrfs: fix a bug of snapshot-aware defrag to make it work on partial extents (Eric Sandeen) [1010071]
- [fs] btrfs: fix file truncation if FALLOC_FL_KEEP_SIZE is specified (Eric Sandeen) [1010071]
- [fs] btrfs: fix wrong write offset when replacing a device (Eric Sandeen) [1010071]
- [fs] btrfs: re-add root to dead root list if we stop dropping it (Eric Sandeen) [1010071]
- [fs] btrfs: fix lock leak when resuming snapshot deletion (Eric Sandeen) [1010071]
- [fs] btrfs: update drop progress before stopping snapshot dropping (Eric Sandeen) [1010071]
- [fs] btrfs: wait ordered range before doing direct io (Eric Sandeen) [1010071]
- [fs] btrfs: only do the tree_mod_log_free_eb if this is our last ref (Eric Sandeen) [1010071]
- [fs] btrfs: hold the tree mod lock in __tree_mod_log_rewind (Eric Sandeen) [1010071]
- [fs] btrfs: make backref walking code handle skinny metadata (Eric Sandeen) [1010071]
- [fs] btrfs: fix crash regarding to ulist_add_merge (Eric Sandeen) [1010071]
- [fs] btrfs: fix several potential problems in copy_nocow_pages_for_inode (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup the code of copy_nocow_pages_for_inode() (Eric Sandeen) [1010071]
- [fs] btrfs: fix oops when recovering the file data by scrub function (Eric Sandeen) [1010071]
- [fs] btrfs: make the chunk allocator completely tree lockless (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup orphaned root orphan item (Eric Sandeen) [1010071]
- [fs] btrfs: fix wrong mirror number tuning (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup redundant code in btrfs_submit_direct() (Eric Sandeen) [1010071]
- [fs] btrfs: remove btrfs_sector_sum structure (Eric Sandeen) [1010071]
- [fs] btrfs: check if we can nocow if we don't have data space (Eric Sandeen) [1010071]
- [fs] btrfs: stop using try_to_writeback_inodes_sb_nr to flush delalloc (Eric Sandeen) [1010071]
- [fs] btrfs: use a percpu to keep track of possibly pinned bytes (Eric Sandeen) [1010071]
- [fs] btrfs: check for actual acls rather than just xattrs when caching no acl (Eric Sandeen) [1010071]
- [fs] btrfs: move btrfs_truncate_page to btrfs_cont_expand instead of btrfs_truncate (Eric Sandeen) [1010071]
- [fs] btrfs: optimize reada_for_balance (Eric Sandeen) [1010071]
- [fs] btrfs: optimize read_block_for_search (Eric Sandeen) [1010071]
- [fs] btrfs: unlock extent range on enospc in compressed submit (Eric Sandeen) [1010071]
- [fs] btrfs: fix the comment typo for btrfs_attach_transaction_barrier (Eric Sandeen) [1010071]
- [fs] btrfs: fix not being able to find skinny extents during relocate (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup backref search commit root flag stuff (Eric Sandeen) [1010071]
- [fs] btrfs: free csums when we're done scrubbing an extent (Eric Sandeen) [1010071]
- [fs] btrfs: fix transaction throttling for delayed refs (Eric Sandeen) [1010071]
- [fs] btrfs: stop waiting on current trans if we aborted (Eric Sandeen) [1010071]
- [fs] btrfs: wake up delayed ref flushing waiters on abort (Eric Sandeen) [1010071]
- [fs] btrfs: fix the code comments for LZO compression workspace (Eric Sandeen) [1010071]
- [fs] btrfs: fix broken nocow after balance (Eric Sandeen) [1010071]
- [fs] btrfs: more open-coded file_inode() (Eric Sandeen) [1010071]
- [fs] btrfs: exclude logged extents before replying when we are mixed (Eric Sandeen) [1010071]
- [fs] btrfs: put our inode if orphan cleanup fails (Eric Sandeen) [1010071]
- [fs] btrfs: add some missing iput()'s in btrfs_orphan_cleanup (Eric Sandeen) [1010071]
- [fs] btrfs: do not pin while under spin lock (Eric Sandeen) [1010071]
- [fs] btrfs: Cocci spatch "memdup.spatch" (Eric Sandeen) [1010071]
- [fs] btrfs: Cocci spatch "ptr_ret.spatch" (Eric Sandeen) [1010071]
- [fs] btrfs: fix qgroup rescan resume on mount (Eric Sandeen) [1010071]
- [fs] btrfs: avoid double free of fs_info->qgroup_ulist (Eric Sandeen) [1010071]
- [fs] btrfs: fix memory patcher through fs_info->qgroup_ulist (Eric Sandeen) [1010071]
- [fs] btrfs: simplify unlink reservations (Eric Sandeen) [1010071]
- [fs] btrfs: merge pending IO for tree log write back (Eric Sandeen) [1010071]
- [fs] btrfs: allow file data clone within a file (Eric Sandeen) [1010071]
- [fs] btrfs: remove unused code in btrfs_del_root (Eric Sandeen) [1010071]
- [fs] btrfs: kill replicate code in replay_one_buffer (Eric Sandeen) [1010071]
- [fs] btrfs: check if leaf's parent exists before pushing items around (Eric Sandeen) [1010071]
- [fs] btrfs: update new flags for tracepoint (Eric Sandeen) [1010071]
- [fs] btrfs: dont do log_removal in insert_new_root (Eric Sandeen) [1010071]
- [fs] btrfs: return error code in btrfs_check_trunc_cache_free_space() (Eric Sandeen) [1010071]
- [fs] btrfs: fix estale with btrfs send (Eric Sandeen) [1010071]
- [fs] btrfs: device delete to get errors from the kernel (Eric Sandeen) [1010071]
- [fs] btrfs: do delay iput in sync_fs (Eric Sandeen) [1010071]
- [fs] btrfs: make the state of the transaction more readable (Eric Sandeen) [1010071]
- [fs] btrfs: remove the time check in btrfs_commit_transaction() (Eric Sandeen) [1010071]
- [fs] btrfs: remove unnecessary varient ->num_joined in btrfs_transaction structure (Eric Sandeen) [1010071]
- [fs] btrfs: don't flush the delalloc inodes in the while loop if flushoncommit is set (Eric Sandeen) [1010071]
- [fs] btrfs: don't wait for all the writers circularly during the transaction commit (Eric Sandeen) [1010071]
- [fs] btrfs: remove the code for the impossible case in cleanup_transaction() (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup unnecessary assignment when cleaning up all the residual transaction (Eric Sandeen) [1010071]
- [fs] btrfs: just flush the delalloc inodes in the source tree before snapshot creation (Eric Sandeen) [1010071]
- [fs] btrfs: introduce per-subvolume ordered extent list (Eric Sandeen) [1010071]
- [fs] btrfs: introduce per-subvolume delalloc inode list (Eric Sandeen) [1010071]
- [fs] btrfs: introduce grab/put functions for the root of the fs/file tree (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup the similar code of the fs root read (Eric Sandeen) [1010071]
- [fs] btrfs: make the snap/subv deletion end more early when the fs is R/O (Eric Sandeen) [1010071]
- [fs] btrfs: move the R/O check out of btrfs_clean_one_deleted_snapshot() (Eric Sandeen) [1010071]
- [fs] btrfs: make the cleaner complete early when the fs is going to be umounted (Eric Sandeen) [1010071]
- [fs] btrfs: remove unnecessary ->s_umount in cleaner_kthread() (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup: don't check the same thing twice (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup, btrfs_read_fs_root_no_name() doesn't return NULL (Eric Sandeen) [1010071]
- [fs] btrfs: delete unused function (Eric Sandeen) [1010071]
- [fs] btrfs: remove useless copy in quota_ctl (Eric Sandeen) [1010071]
- [fs] btrfs: Minor format cleanup (Eric Sandeen) [1010071]
- [fs] btrfs: cleanup unused arguments in send.c (Eric Sandeen) [1010071]
- [fs] btrfs: add ioctl to wait for qgroup rescan completion (Eric Sandeen) [1010071]
- [fs] btrfs: introduce qgroup_ulist to avoid frequently allocating/freeing ulist (Eric Sandeen) [1010071]
- [fs] btrfs: show compiled-in config features at module load time (Eric Sandeen) [1010071]
- [fs] btrfs: move ifdef around sanity checks out of init_btrfs_fs (Eric Sandeen) [1010071]
- [fs] btrfs: add prefix to sanity tests messages (Eric Sandeen) [1010071]
- [fs] btrfs: add debug check for extent_io range alignment (Eric Sandeen) [1010071]
- [fs] btrfs: fix check on same raid type flag twice (Eric Sandeen) [1010071]
- [fs] btrfs: Fix typo in printk (Eric Sandeen) [1010071]
- [fs] btrfs: fix btrfs_extend_item() comment (Eric Sandeen) [1010071]

* Wed Oct 16 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-35.el7]
- [netdrv] mlx4: Fix handling of dma_map failure (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Notify user when TX ring in error state (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Disable global flow control when PFC enabled (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Coding style cleanup in mlx4_en_dcbnl_ieee_setpfc() (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Staticize local functions (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: VFs must ignore the enable_64b_cqe_eqe module param (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Don't give VFs MAC addresses which are derived from the PF MAC (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Respond to operation request by firmware (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Fix BlueFlame race (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: fix small memory leak on error (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Add HW enforcement to VF link state (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Dynamic VST to VST vlan/qos changes (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Fail device init if num_vfs is negative (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Add warning in case of command timeouts (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Replace sscanf() with kstrtoint() (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Remove an unnecessary test (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Add prints when TX timeout occurs (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Fix a race between napi poll function and RX ring cleanup (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Change log level from error to debug for vlan related messages (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Move register_netdev() to the end of initialization function (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Do not query stats when device port is down (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Fix resource leak in error flow (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: allow order-0 memory allocations in RX path (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Add support for busy poll (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Add VF link state support (Amir Vadai) [862498 868244 920465 978058 998202]
- [net] core: Add VF link state control (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: use __netdev_pick_tx instead of __skb_tx_hash in mlx4_en_select_queue (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: use one page fragment per incoming frame (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] ipoib: Fix pkey change flow for virtualization environments (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] ipoib: Make sure child devices use valid/proper pkeys (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Create QP1 using the pkey index which contains the default pkey (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] mlx4: Use default pkey when creating tunnel QPs (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Fix redundant pointer check in dealloc flow (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Fix possible memory leak in iser_create_frwr_pool() (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Introduce fast memory registration model (FRWR) (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Place the fmr pool into a union in iser's IB conn struct (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Handle unaligned SG in separate function (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Generalize rdma memory registration (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Accept session->cmds_max from user space (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Restructure allocation/deallocation of connection resources (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Use proper debug level value for info prints (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] iser: Add Discovery support (Amir Vadai) [862498 868244 920465 978058 998202]
- [scsi] libiscsi: Exporting new attrs for iscsi session and connection in sysfs (Amir Vadai) [862498 868244 920465 978058 998202]
- [scsi] scsi_transport_iscsi: Exporting new attrs for iscsi session and connection in sysfs (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Better checking of userspace values for receive flow steering (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] mlx4: Add receive flow steering support (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Export ib_create/destroy_flow through uverbs (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Infrastructure for extensible uverbs commands (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Add receive flow steering support (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Fixes to XRC reference counting in uverbs (Amir Vadai) [862498 868244 920465 978058 998202]
- [infiniband] core: Add locking around event dispatching on XRC target QPs (Amir Vadai) [862498 868244 920465 978058 998202]
- [netdrv] mlx4: Fix XRC QPs detection in the resource tracker (Amir Vadai) [862498 868244 920465 978058 998202]
- [powerpc] irq: Don't switch to irq stack from softirq stack (Steve Best) [1016454]
- [powerpc] hvsi: Increase handshake timeout from 200ms to 400ms (Steve Best) [1012654]
- [powerpc] zimage: make the "OF" wrapper support ePAPR boot (Steve Best) [1012654]
- [powerpc] pseries: Do not start secondaries in Open Firmware (Steve Best) [1012654]
- [powerpc] Make prom_init.c endian safe (Steve Best) [1012654]
- [powerpc] Remove ksp_limit on ppc64 (Steve Best) [1012654]
- [powerpc] irq: Run softirqs off the top of the irq stack (Steve Best) [1012654]
- [mm] avoid reinserting isolated balloon pages into LRU lists (Rafael Aquini) [1017445]
- [kernel] sched: fix race in migrate_swap_stop (Rik van Riel) [683513]
- [kernel] sched/numa: Retry task_numa_migrate() periodically (Rik van Riel) [683513]
- [kernel] sched/numa: Use unsigned longs for numa group fault stats (Rik van Riel) [683513]
- [kernel] sched/numa: Skip some page migrations after a shared fault (Rik van Riel) [683513]
- [kernel] sched/numa: Remove the numa_balancing_scan_period_reset sysctl (Rik van Riel) [683513]
- [kernel] sched/numa: Adjust scan rate in task_numa_placement (Rik van Riel) [683513]
- [kernel] sched/numa: Take false sharing into account when adapting scan rate (Rik van Riel) [683513]
- [kernel] sched/numa: Be more careful about joining numa groups (Rik van Riel) [683513]
- [kernel] sched/numa: Avoid migrating tasks that are placed on their preferred node (Rik van Riel) [683513]
- [kernel] sched/numa: Fix task or group comparison (Rik van Riel) [683513]
- [kernel] sched/numa: Decide whether to favour task or group weights based on swap candidate relationships (Rik van Riel) [683513]
- [kernel] sched/numa: Add debugging (Rik van Riel) [683513]
- [kernel] sched/numa: Prevent parallel updates to group stats during placement (Rik van Riel) [683513]
- [kernel] sched/numa: Call task_numa_free() from do_execve () (Rik van Riel) [683513]
- [kernel] sched/numa: Use group fault statistics in numa placement (Rik van Riel) [683513]
- [kernel] sched/numa: Stay on the same node if CLONE_VM (Rik van Riel) [683513]
- [mm] numa: Do not batch handle PMD pages (Rik van Riel) [683513]
- [mm] numa: Do not group on RO pages (Rik van Riel) [683513]
- [mm] numa: Copy cpupid on page migration (Rik van Riel) [683513]
- [kernel] sched/numa: Report a NUMA task group ID (Rik van Riel) [683513]
- [kernel] sched/numa: Use {cpu, pid} to create task groups for shared faults (Rik van Riel) [683513]
- [mm] numa: Change page last {nid, pid} into {cpu, pid} (Rik van Riel) [683513]
- [kernel] sched/numa: Fix placement of workloads spread across multiple nodes (Rik van Riel) [683513]
- [kernel] sched/numa: Favor placing a task on the preferred node (Rik van Riel) [683513]
- [kernel] sched/numa: Use a system-wide search to find swap/migration candidates (Rik van Riel) [683513]
- [kernel] sched/numa: Introduce migrate_swap() (Rik van Riel) [683513]
- [kernel] stop_machine: Introduce stop_two_cpus() (Rik van Riel) [683513]
- [mm] numa: Trap pmd hinting faults only if we would otherwise trap PTE faults (Rik van Riel) [683513]
- [kernel] sched/numa: Do not trap hinting faults for shared libraries (Rik van Riel) [683513]
- [kernel] sched/numa: Increment numa_migrate_seq when task runs in correct location (Rik van Riel) [683513]
- [kernel] sched/numa: Retry migration of tasks to CPU on a preferred node (Rik van Riel) [683513]
- [kernel] sched/numa: Avoid overloading CPUs on a preferred NUMA node (Rik van Riel) [683513]
- [kernel] numa: Limit NUMA scanning to migrate-on-fault VMAs (Rik van Riel) [683513]
- [kernel] sched/numa: Do not migrate memory immediately after switching node (Rik van Riel) [683513]
- [mm] sched/numa: Set preferred NUMA node based on number of private faults (Rik van Riel) [683513]
- [kernel] sched/numa: Remove check that skips small VMAs (Rik van Riel) [683513]
- [mm] numa: Scan pages with elevated page_mapcount (Rik van Riel) [683513]
- [kernel] sched/numa: Check current-> mm before allocating NUMA faults (Rik van Riel) [683513]
- [kernel] sched/numa: Add infrastructure for split shared/ private accounting of NUMA hinting faults (Rik van Riel) [683513]
- [kernel] sched/numa: Reschedule task on preferred NUMA node once selected (Rik van Riel) [683513]
- [kernel] sched/numa: Resist moving tasks towards nodes with fewer hinting faults (Rik van Riel) [683513]
- [kernel] sched/numa: Favour moving tasks towards the preferred node (Rik van Riel) [683513]
- [kernel] sched/numa: Update NUMA hinting faults once per scan (Rik van Riel) [683513]
- [kernel] sched/numa: Select a preferred node with the most numa hinting faults (Rik van Riel) [683513]
- [mm] sched/numa: Track NUMA hinting faults on per-node basis (Rik van Riel) [683513]
- [mm] sched/numa: Slow scan rate if no NUMA hinting faults are being recorded (Rik van Riel) [683513]
- [mm] sched/numa: Set the scan rate proportional to the memory usage of the task being scanned (Rik van Riel) [683513]
- [mm] sched/numa: Initialise numa_next_scan properly (Rik van Riel) [683513]
- [mm] sched/numa: Continue PTE scanning even if migrate rate limited (Rik van Riel) [683513]
- [mm] sched/numa: Mitigate chance that same task always updates PTEs (Rik van Riel) [683513]
- [mm] numa: Do not migrate or account for hinting faults on the zero page (Rik van Riel) [683513]
- [mm] Only flush TLBs if a transhuge PMD is modified for NUMA pte scanning (Rik van Riel) [683513]
- [mm] Do not flush TLB during protection change if !pte_present && !migration_entry (Rik van Riel) [683513]
- [mm] Account for a THP NUMA hinting update as one PTE update (Rik van Riel) [683513]
- [mm] Close races between THP migration and PMD numa clearing (Rik van Riel) [683513]
- [mm] numa: Sanitize task_numa_fault() callsites (Rik van Riel) [683513]
- [mm] Prevent parallel splits during THP migration (Rik van Riel) [683513]
- [mm] Wait for THP migrations to complete during NUMA hinting faults (Rik van Riel) [683513]
- [mm] numa: Do not account for a hinting fault if we raced (Rik van Riel) [683513]
- [mm] sched/numa: Fix comments (Rik van Riel) [683513]
- [mm] numa: Document automatic NUMA balancing sysctls (Rik van Riel) [683513]
- [kernel] sched: monolithic code dump of what is being pushed (Rik van Riel) [683513]
- [kernel] sched: Use an accessor to read the rq clock (Rik van Riel) [683513]
- [kernel] sched: fix NUMA balancing when !SCHED_DEBUG (Rik van Riel) [683513]
- [kernel] sched: Ensure update_cfs_shares() is called for parents of continuously-running tasks (Rik van Riel) [683513]
- [kernel] sched: Fix some kernel-doc warnings (Rik van Riel) [683513]
- [virt] kvm/vmx: do not check bit 12 of EPT violation exit qualification when undefined (Gleb Natapov) [1009441]
- [virt] kvm/vmx: set "blocked by NMI" flag if EPT violation happens during IRET from NMI (Gleb Natapov) [1009441]

* Fri Oct 11 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-34.el7]
- [netdrv] netxen_nic: Update version to 4.0.81 (Chad Dupuis) [725019]
- [netdrv] netxen_nic: clean up unnecessary MSI/MSI-X capability find (Chad Dupuis) [725019]
- [netdrv] netxen_nic: Convert mac address uses of 6 to ETH_ALEN (Chad Dupuis) [725019]
- [netdrv] netxen_nic: replace strict_strtoul() with kstrtoul() (Chad Dupuis) [725019]
- [netdrv] netxen_nic: Avoid mixed mode interrupts (Chad Dupuis) [725019]
- [netdrv] netxen_nic: netxen_setup_intr() function code cleanup (Chad Dupuis) [725019]
- [netdrv] netxen_nic: Log proper error message in case of mismatched adapter type (Chad Dupuis) [725019]
- [netdrv] netxen_nic: Log driver version with firmware version (Chad Dupuis) [725019]
- [tools] perf/diff: Add generic order option for compute sorting (Jiri Olsa) [1011529]
- [tools] perf/diff: Making compute functions static (Jiri Olsa) [1011529]
- [tools] perf/diff: Update perf diff documentation for multiple data comparison (Jiri Olsa) [1011529]
- [tools] perf/diff: Change diff command to work over multiple data files (Jiri Olsa) [1011529]
- [tools] perf/diff: Move columns into struct data__file (Jiri Olsa) [1011529]
- [tools] perf/diff: Move diff related columns into diff command (Jiri Olsa) [1011529]
- [tools] perf/diff: Display data file info ahead of the diff output (Jiri Olsa) [1011529]
- [tools] perf/hists: Marking dummy hists entries (Jiri Olsa) [1011529]
- [tools] perf/diff: Switching the base hists to be pairs head (Jiri Olsa) [1011529]
- [tools] perf/diff: Introducing diff_data object to hold files (Jiri Olsa) [1011529]
- [tools] perf: Centralize default columns init in perf_hpp__init (Jiri Olsa) [1011529]
- [tools] perf: Add struct perf_hpp_fmt into hpp callbacks (Jiri Olsa) [1011529]
- [s390] vmcore: use vmcore for zfcpdump (Hendrik Brueckner) [1012102]
- [fs] proc/vmcore: enable /proc/vmcore mmap for s390 (Hendrik Brueckner) [1012102]
- [s390] vmcore: implement remap_oldmem_pfn_range for s390 (Hendrik Brueckner) [1012102]
- [fs] proc/vmcore: introduce remap_oldmem_pfn_range() (Hendrik Brueckner) [1012102]
- [s390] vmcore: use ELF header in new memory feature (Hendrik Brueckner) [1012102]
- [fs] proc/vmcore: introduce ELF header in new memory feature (Hendrik Brueckner) [1012102]
- [fs] proc/vmcore: Disable mmap for s390 (Hendrik Brueckner) [1012102]
- [s390] kdump: Allow copy_oldmem_page() copy to virtual memory (Hendrik Brueckner) [1012102]
- [tracing] Add function probe to trigger a ftrace dump of current CPU trace (Jiri Olsa) [1011527]
- [tracing] Add function probe to trigger a ftrace dump to console (Jiri Olsa) [1011527]
- [virt] xen-gnt: prevent adding duplicate gnt callbacks (Radim Krcmar) [1013818]
- [x86] microcode_amd: Fix patch level reporting for family 15h (Prarit Bhargava) [1014400]
- [tty] Fix SIGTTOU not sent with tcflush() (Oleg Nesterov) [1012397]
- [powerpc] sysfs: Disable writing to PURR in guest mode (Steve Best) [1015450]
- [powerpc] vio: fix modalias_show return values (Prarit Bhargava) [1007924]
- [powerpc] Correct FSCR bit definitions (Steve Best) [1008893]
- [x86] microcode/amd: Fix early microcode loading (Jarod Wilson) [1016168]
- [x86] microcode/amd: Make cpu_has_amd_erratum() use the correct struct cpuinfo_x86 (Jarod Wilson) [1016168]
- [x86] microcode/amd: Fix error path in apply_microcode_amd() (Jarod Wilson) [1016168]
- [x86] microcode/amd: Another early loading fixup (Jarod Wilson) [1016168]
- [x86] microcode/amd: Allow multiple families' bin files appended together (Jarod Wilson) [1016168]
- [x86] microcode/amd: Make find_ucode_in_initrd() __init (Jarod Wilson) [1016168]
- [x86] microcode/amd: Fix warnings and errors on with CONFIG_MICROCODE=m (Jarod Wilson) [1016168]
- [x86] microcode/amd: Early microcode patch loading support for AMD (Jarod Wilson) [1016168]
- [x86] microcode/amd: Refactor functions to prepare for early loading (Jarod Wilson) [1016168]
- [x86] microcode: Vendor abstract out save_microcode_in_initrd() (Jarod Wilson) [1016168]
- [x86] microcode/intel: Correct typo in printk (Jarod Wilson) [1016168]
- [block] nvme: Update nvme_id_power_state with latest spec (David Milburn) [1005908]
- [block] nvme: Split header file into user-visible and kernel-visible pieces (David Milburn) [1005908]
- [block] nvme: Merge issue on character device bring-up (David Milburn) [1005908]
- [block] nvme: Handle ioremap failure (David Milburn) [1005908]
- [block] nvme: Add pci suspend/resume driver callbacks (David Milburn) [1005908]
- [block] nvme: Use normal shutdown (David Milburn) [1005908]
- [block] nvme: Separate controller init from disk discovery (David Milburn) [1005908]
- [block] nvme: Separate queue alloc/free from create/delete (David Milburn) [1005908]
- [block] nvme: Group pci related actions in functions (David Milburn) [1005908]
- [block] nvme: Disk stats for read/write commands only (David Milburn) [1005908]
- [block] nvme: Bring up cdev on set feature failure (David Milburn) [1005908]
- [block] nvme: Fix checkpatch issues (David Milburn) [1005908]
- [block] nvme: Namespace IDs are unsigned (David Milburn) [1005908]
- [block] nvme: Call nvme_process_cq from submission path (David Milburn) [1005908]
- [block] nvme: Remove "process_cq did something" message (David Milburn) [1005908]
- [block] nvme: Return correct value from interrupt handler (David Milburn) [1005908]
- [block] nvme: Disk IO statistics (David Milburn) [1005908]
- [block] nvme: Restructure MSI / MSI-X setup (David Milburn) [1005908]
- [block] nvme: Use kzalloc instead of kmalloc+memset (David Milburn) [1005908]

* Fri Oct 04 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-33.el7]
- [fs] nfs: Give "flavor" an initial value to fix a compile warning (Jeff Layton) [1009119]
- [fs] nfs: try SECINFO_NO_NAME flavs until one works (Jeff Layton) [1009119]
- [fs] nfs: Ensure memory ordering between nfs4_ds_connect and nfs4_fl_prepare_ds (Jeff Layton) [1009119]
- [fs] nfs: nfs4_fl_prepare_ds, fix bugs when the connect attempt fails (Jeff Layton) [1009119]
- [fs] nfs: Honour the 'opened' parameter in the atomic_open() filesystem method (Jeff Layton) [1009119]
- [net] sunrpc: rpcsec_gss, fix crash on destroying gss auth (Jeff Layton) [1009119]
- [net] sunrpc: No, I did not intend to create a 256KiB hashtable (Jeff Layton) [1009119]
- [net] sunrpc: Add missing kuids conversion for printing (Jeff Layton) [1009119]
- [fs] nfs: sp4_mach_cred, WARN_ON -> WARN_ON_ONCE (Jeff Layton) [1009119]
- [fs] nfs: sp4_mach_cred, no need to ref count creds (Jeff Layton) [1009119]
- [fs] nfs: fix SECINFO* use of put_rpccred (Jeff Layton) [1009119]
- [fs] nfs: sp4_mach_cred: ask for WRITE and COMMIT (Jeff Layton) [1009119]
- [fs] nfs: fix decode_free_stateid (Jeff Layton) [1009119]
- [fs] nfs: use mach cred for SECINFO_NO_NAME w/ integrity (Jeff Layton) [1009119]
- [fs] nfs: nfs_compare_super shouldn't check the auth flavour unless 'sec=' was set (Jeff Layton) [1009119]
- [fs] nfs: Allow security autonegotiation for submounts (Jeff Layton) [1009119]
- [fs] nfs: Disallow security negotiation for lookups when 'sec=' is specified (Jeff Layton) [1009119]
- [fs] nfs: Fix security auto-negotiation (Jeff Layton) [1009119]
- [fs] nfs: Clean up nfs_parse_security_flavors() (Jeff Layton) [1009119]
- [fs] nfs: Clean up the auth flavour array mess (Jeff Layton) [1009119]
- [fs] nfs: Use MDS auth flavor for data server connection (Jeff Layton) [1009119]
- [fs] nfs: Map NFS4ERR_WRONG_CRED to EPERM (Jeff Layton) [1009119]
- [fs] nfs: Add SP4_MACH_CRED write and commit support (Jeff Layton) [1009119]
- [fs] nfs: Add SP4_MACH_CRED stateid support (Jeff Layton) [1009119]
- [fs] nfs: Add SP4_MACH_CRED secinfo suppor (Jeff Layton) [1009119]
- [fs] nfs: Add SP4_MACH_CRED cleanup support (Jeff Layton) [1009119]
- [fs] nfs: Add state protection handler (Jeff Layton) [1009119]
- [fs] nfs: Minimal SP4_MACH_CRED implementation (Jeff Layton) [1009119]
- [net] sunrpc: Replace pointer values with task->tk_pid and rpc_clnt->cl_clid (Jeff Layton) [1009119]
- [net] sunrpc: Add an identifier for struct rpc_clnt (Jeff Layton) [1009119]
- [net] sunrpc: Ensure rpc_task->tk_pid is available for tracepoints (Jeff Layton) [1009119]
- [fs] nfs: Document the recover_lost_locks kernel parameter (Jeff Layton) [1009119]
- [fs] nfs: Don't try to recover NFSv4 locks when they are lost (Jeff Layton) [1009119]
- [net] sunrpc: Add tracepoints to help debug socket connection issues (Jeff Layton) [1009119]
- [fs] nfs: Fix warning introduced by NFSv4.0 transport blocking patches (Jeff Layton) [1009119]
- [fs] nfs: fix CONFIG_NFS_V4_1 not enabled "make C=2" warning (Jeff Layton) [1009119]
- [fs] nfs: Update session draining barriers for NFSv4.0 transport blocking (Jeff Layton) [1009119]
- [fs] nfs: Add nfs4_sequence calls for OPEN_CONFIRM (Jeff Layton) [1009119]
- [fs] nfs: Add nfs4_sequence calls for RELEASE_LOCKOWNER (Jeff Layton) [1009119]
- [fs] nfs: Enable nfs4_setup_sequence() for DELEGRETURN (Jeff Layton) [1009119]
- [fs] nfs: NFSv4.0 transport blocking (Jeff Layton) [1009119]
- [fs] nfs: Add a slot table to struct nfs_client for NFSv4.0 transport blocking (Jeff Layton) [1009119]
- [fs] nfs: Add global helper for releasing slot table resources (Jeff Layton) [1009119]
- [fs] nfs: Add global helper to set up a stand-along nfs4_slot_table (Jeff Layton) [1009119]
- [fs] nfs: Enable slot table helpers for NFSv4.0 (Jeff Layton) [1009119]
- [fs] nfs: Remove unused call_sync minor version op (Jeff Layton) [1009119]
- [fs] nfs: Add RPC callouts to start NFSv4.0 synchronous requests (Jeff Layton) [1009119]
- [fs] nfs: Common versions of sequence helper functions (Jeff Layton) [1009119]
- [fs] nfs: Clean up nfs4_setup_sequence() (Jeff Layton) [1009119]
- [fs] nfs: Rename nfs41_call_sync_data as a common data structure (Jeff Layton) [1009119]
- [fs] nfs: When displaying session slot numbers, use "u" consistently (Jeff Layton) [1009119]
- [fs] nfs: Ensure that rmdir() waits for sillyrenames to complete (Jeff Layton) [1009119]
- [fs] nfs: use the mach cred for SECINFO w/ integrity (Jeff Layton) [1009119]
- [net] sunrpc: refactor rpcauth_checkverf error returns (Jeff Layton) [1009119]
- [fs] nfs: avoid expired credential keys for buffered writes (Jeff Layton) [1009119]
- [net] sunrpc: new rpc_credops to test credential expiry (Jeff Layton) [1009119]
- [net] sunrpc: don't map EKEYEXPIRED to EACCES in call_refreshresult (Jeff Layton) [1009119]
- [fs] nfs: Fix up two use-after-free issues with the new tracing code (Jeff Layton) [1009119]
- [fs] nfs: remove incorrect "Lock reclaim failed!" warning (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging test_stateid events (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging slot table operations (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging layoutget/return/commit (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging reads and writes (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging getattr (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging the idmapper (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging delegations (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging rename (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging inode manipulations (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging lookup/create operations (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging file locking (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging file open (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging state management problems (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging NFS hard links (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging NFS rename and sillyrename issues (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging directory changes (Jeff Layton) [1009119]
- [fs] nfs: Add tracepoints for debugging generic file create events (Jeff Layton) [1009119]
- [fs] nfs: Add event tracing for generic NFS lookups (Jeff Layton) [1009119]
- [fs] nfs: Pass in lookup flags from nfs_atomic_open to nfs_lookup (Jeff Layton) [1009119]
- [fs] nfs: Add event tracing for generic NFS events (Jeff Layton) [1009119]
- [fs] nfs: refactor code for calculating the crc32 hash of a filehandle (Jeff Layton) [1009119]
- [fs] nfs: Clean up nfs_sillyrename() (Jeff Layton) [1009119]
- [fs] nfs: Fix an incorrect pointer declaration in decode_first_pnfs_layout_type (Jeff Layton) [1009119]
- [fs] nfs: Deal with a sparse warning in nfs_idmap_get_key() (Jeff Layton) [1009119]
- [fs] nfs: Deal with some more sparse warnings (Jeff Layton) [1009119]
- [fs] nfs: Deal with a sparse warning in nfs4_opendata_alloc (Jeff Layton) [1009119]
- [fs] nfs: Deal with a sparse warning in nfs3_proc_create (Jeff Layton) [1009119]
- [fs] nfs: Remove the NFSv4 "open optimisation" from nfs_permission (Jeff Layton) [1009119]
- [fs] nfs: Use clientid management rpc_clnt for secinfo_no_name (Jeff Layton) [1009119]
- [fs] nfs: Use clientid management rpc_clnt for secinfo (Jeff Layton) [1009119]
- [fs] nfs: Increase NFS4_DEF_SLOT_TABLE_SIZE (Jeff Layton) [1009119]
- [fs] nfs: Remove unused authflavour parameter from init_client (Jeff Layton) [1009119]
- [fs] nfs: Never use user credentials for lease renewal (Jeff Layton) [1009119]
- [fs] nfs: Use root's credential for lease management when keytab is missing (Jeff Layton) [1009119]
- [fs] nfs: Refuse mount attempts with proto=udp (Jeff Layton) [1009119]
- [fs] nfs: Fix nfs4_init_uniform_client_string for net namespaces (Jeff Layton) [1009119]
- [fs] nfs: Use the mount point rpc_clnt for layoutreturn (Jeff Layton) [1009119]
- [fs] nfs: Fix return type of nfs4_end_drain_session() stub (Jeff Layton) [1009119]
- [fs] nfs: encode_attrs should not backfill the bitmap and attribute length (Jeff Layton) [1009119]
- [net] sunrpc: Fix memory corruption issue on 32-bit highmem systems (Jeff Layton) [1009119]
- [fs] nfs: Remove unnecessary call to nfs_setsecurity in nfs_fhget() (Jeff Layton) [1009119]
- [fs] nfs: Fix the sync mount option for nfs4 mounts (Jeff Layton) [1009119]
- [fs] nfs: Fix writeback performance issue on cache invalidation (Jeff Layton) [1009119]
- [net] sunrpc: If the rpcbind channel is disconnected, fail the call to unregister (Jeff Layton) [1009119]
- [net] sunrpc: Don't auto-disconnect from the local rpcbind socket (Jeff Layton) [1009119]
- [hid] zeroplus: validate output report details (Frantisek Hrbata) [999907] {CVE-2013-2889}
- [hid] provide a helper for validating hid reports (Frantisek Hrbata) [999907] {CVE-2013-2889}
- [s390] zfcp: enable FCP hardware data router by default (Hendrik Brueckner) [980146]
- [scsi] csiostor: fix failure to communicate with firmware, error -110 (Jay Fenlason) [917907]
- [block] mtip32xx: add SRSI support (David Milburn) [842533]
- [misc] hpilo: Correct panic when an AUX iLO is detected (Nigel Croxon) [996603]
- [Documentation] add write up on module signing (Kyle McMartin) [905495]
- [net] netfilter: SYNPROXY: let unrelated packets continue (Jesper Brouer) [1007439]
- [net] netfilter: synproxy_core: fix warning in __nf_ct_ext_add_length() (Jesper Brouer) [1007439]
- [net] netfilter: more strict TCP flag matching in SYNPROXY (Jesper Brouer) [1007439]
- [net] netfilter: add IPv6 SYNPROXY target (Jesper Brouer) [1007439]
- [net] syncookies: export cookie_v6_init_sequence/cookie_v6_check (Jesper Brouer) [1007439]
- [net] netfilter: add SYNPROXY core/target (Jesper Brouer) [1007439]
- [net] syncookies: export cookie_v4_init_sequence/cookie_v4_check (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: make sequence number adjustments usuable without NAT (Jesper Brouer) [1007439]
- [net] netfilter: nf_defrag_ipv6.o included twice (Jesper Brouer) [1007439]
- [net] netfilter: ip[6]t_REJECT, tcp-reset using wrong MAC source if bridged (Jesper Brouer) [1007439]
- [net] netfilter: export xt_HMARK.h to userland (Jesper Brouer) [1007439]
- [net] netfilter: export xt_rpfilter.h to userland (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: fix uninitialized variable (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_queue: allow to attach expectations to conntracks (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: refactor ctnetlink_create_expect (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: fix tcp_in_window for Fast Open (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: don't send destroy events from iterator (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_{log, queue}, fix information leaks in netlink message (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPMSS: correct return value in tcpmss_mangle_packet (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPOPTSTRIP: fix possible off by one access (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPMSS: fix handling of malformed TCP header and options (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: use per-conntrack locking for sequence number adjustments (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: change sequence number adjustments to 32 bits (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: fix locking in nf_nat_seq_adjust() (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: remove duplicate code in ctnetlink (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: constify sk_buff argument to nf_ct_attach() (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: remove net_ratelimit() for LOG_INVALID() (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: fix incorrect NAT expectation dumping (Jesper Brouer) [1007439]
- [net] netfilter: Fix build errors with xt_socket.c (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: fix broken v0 support (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: add XT_SOCKET_NOWILDCARD flag (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: avoid large timeout for mid-stream pickup (Jesper Brouer) [1007439]
- [net] netfilter: check return code from nla_parse_tested (Jesper Brouer) [1007439]
- [net] Convert uses of typedef ctl_table to struct ctl_table (Jesper Brouer) [1007439]
- [net] netfilter: Implement RFC 1123 for FTP conntrack (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_queue: avoid peer_portid test (Jesper Brouer) [1007439]
- [net] netfilter: don't panic on error while walking through the init path (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: use IP early demux (Jesper Brouer) [1007439]
- [net] netfilter: xt_CT: optimize XT_CT_NOTRACK (Jesper Brouer) [1007439]
- [net] qdisc: fix build with !CONFIG_NET_SCHED (Jesper Brouer) [1000395]
- [net] qdisc: make args to qdisc_create_default const (Jesper Brouer) [1000395]
- [net] qdisc: allow setting default queuing discipline (Jesper Brouer) [1000395]
- [net] Remove extern from include/net/ scheduling prototypes (Jesper Brouer) [1000395]
- [net] htb: fix sign extension bug (Jesper Brouer) [1000395]
- [net] htb: refactor struct htb_sched fields for performance (Jesper Brouer) [1000395]
- [net] htb: reorder struct htb_class fields for performance (Jesper Brouer) [1000395]
- [net] htb: do not setup default rate estimators (Jesper Brouer) [1000395]
- [net] net_sched: add 64bit rate estimators (Jesper Brouer) [1000395]

* Fri Oct 04 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-32.el7]
- [net] netfilter: SYNPROXY: let unrelated packets continue (Jesper Brouer) [1007439]
- [net] netfilter: synproxy_core: fix warning in __nf_ct_ext_add_length() (Jesper Brouer) [1007439]
- [net] netfilter: more strict TCP flag matching in SYNPROXY (Jesper Brouer) [1007439]
- [net] netfilter: add IPv6 SYNPROXY target (Jesper Brouer) [1007439]
- [net] syncookies: export cookie_v6_init_sequence/cookie_v6_check (Jesper Brouer) [1007439]
- [net] netfilter: add SYNPROXY core/target (Jesper Brouer) [1007439]
- [net] syncookies: export cookie_v4_init_sequence/cookie_v4_check (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: make sequence number adjustments usuable without NAT (Jesper Brouer) [1007439]
- [net] netfilter: nf_defrag_ipv6.o included twice (Jesper Brouer) [1007439]
- [net] netfilter: ip[6]t_REJECT, tcp-reset using wrong MAC source if bridged (Jesper Brouer) [1007439]
- [net] netfilter: export xt_HMARK.h to userland (Jesper Brouer) [1007439]
- [net] netfilter: export xt_rpfilter.h to userland (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: fix uninitialized variable (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_queue: allow to attach expectations to conntracks (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: refactor ctnetlink_create_expect (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: fix tcp_in_window for Fast Open (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: don't send destroy events from iterator (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_{log, queue}, fix information leaks in netlink message (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPMSS: correct return value in tcpmss_mangle_packet (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPOPTSTRIP: fix possible off by one access (Jesper Brouer) [1007439]
- [net] netfilter: xt_TCPMSS: fix handling of malformed TCP header and options (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: use per-conntrack locking for sequence number adjustments (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: change sequence number adjustments to 32 bits (Jesper Brouer) [1007439]
- [net] netfilter: nf_nat: fix locking in nf_nat_seq_adjust() (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: remove duplicate code in ctnetlink (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: constify sk_buff argument to nf_ct_attach() (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: remove net_ratelimit() for LOG_INVALID() (Jesper Brouer) [1007439]
- [net] netfilter: ctnetlink: fix incorrect NAT expectation dumping (Jesper Brouer) [1007439]
- [net] netfilter: Fix build errors with xt_socket.c (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: fix broken v0 support (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: add XT_SOCKET_NOWILDCARD flag (Jesper Brouer) [1007439]
- [net] netfilter: nf_conntrack: avoid large timeout for mid-stream pickup (Jesper Brouer) [1007439]
- [net] netfilter: check return code from nla_parse_tested (Jesper Brouer) [1007439]
- [net] Convert uses of typedef ctl_table to struct ctl_table (Jesper Brouer) [1007439]
- [net] netfilter: Implement RFC 1123 for FTP conntrack (Jesper Brouer) [1007439]
- [net] netfilter: nfnetlink_queue: avoid peer_portid test (Jesper Brouer) [1007439]
- [net] netfilter: don't panic on error while walking through the init path (Jesper Brouer) [1007439]
- [net] netfilter: xt_socket: use IP early demux (Jesper Brouer) [1007439]
- [net] netfilter: xt_CT: optimize XT_CT_NOTRACK (Jesper Brouer) [1007439]
- [net] qdisc: fix build with !CONFIG_NET_SCHED (Jesper Brouer) [1000395]
- [net] qdisc: make args to qdisc_create_default const (Jesper Brouer) [1000395]
- [net] qdisc: allow setting default queuing discipline (Jesper Brouer) [1000395]
- [net] Remove extern from include/net/ scheduling prototypes (Jesper Brouer) [1000395]
- [net] htb: fix sign extension bug (Jesper Brouer) [1000395]
- [net] htb: refactor struct htb_sched fields for performance (Jesper Brouer) [1000395]
- [net] htb: reorder struct htb_class fields for performance (Jesper Brouer) [1000395]
- [net] htb: do not setup default rate estimators (Jesper Brouer) [1000395]
- [net] net_sched: add 64bit rate estimators (Jesper Brouer) [1000395]

* Mon Sep 30 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-31.el7]
- [watchdog] hpwdt: Patch to ignore auxilary iLO devices (Nigel Croxon) [996605]
- [s390] tx: allow program interruption filtering in user space (Hendrik Brueckner) [1006517]
- [block] add padding for kabi to block_device_operations (Don Zickus) [988500]
- [fs] gfs2: Don't flag consistency error if first mounter is a spectator (Robert S Peterson) [1004448]
- [tty] disassociate_ctty() sends the extra SIGCONT (Oleg Nesterov) [1011820]
- [x86] mm: Add memory tracking support for 1G hugepages (David Bulkow) [1000149]
- [tty] hvc_iucv: Disconnect IUCV connection when lowering DTR (Hendrik Brueckner) [1007571]
- [tty] hvc_console: Add DTR/RTS callback to handle HUPCL control (Hendrik Brueckner) [1007571]
- [netdrv] enic: update enic maintainers and driver (Stefan Assmann) [747385]
- [netdrv] enic: Exposing symbols for Cisco's low latency driver (Stefan Assmann) [747385]
- [netdrv] enic: Try DMA 64 first, then failover to DMA (Stefan Assmann) [747385]
- [netdrv] enic: record q_number and rss_hash for skb (Stefan Assmann) [747385]
- [netdrv] enic: Add multi tx support for enic (Stefan Assmann) [747385]
- [netdrv] enic: Generate notification of hardware crash (Stefan Assmann) [747385]
- [netdrv] enic: Add an interface for USNIC to interact with firmware (Stefan Assmann) [747385]
- [netdrv] enic: Adding support for Cisco Low Latency NIC (Stefan Assmann) [747385]
- [netdrv] enic: Move ethtool code to a separate file (Stefan Assmann) [747385]
- [netdrv] enic: release rtnl_lock on error-path (Stefan Assmann) [747385]
- [powerpc] perf: Power7 Update testing ABI to list CPI-stack events (Steve Best) [1009105]
- [powerpc] perf: Make Power7 events available for perf (Steve Best) [1009105]
- [powerpc] perf: fix a typo of a Power7 event name (Steve Best) [1009105]
- [tools] perf/tests: Add parse events tests for leader sampling (Jiri Olsa) [1011533]
- [tools] perf/tests: Add attr record group sampling test (Jiri Olsa) [1011533]
- [tools] perf: Add 'S' event/group modifier to read sample value (Jiri Olsa) [1011533]
- [tools] perf/evsel: Add PERF_SAMPLE_READ sample related processing (Jiri Olsa) [1011533]
- [tools] perf/evlist: Add perf_evlist__id2sid method to get event ID related data (Jiri Olsa) [1011533]
- [tools] perf/evlist: Fix event ID retrieval for group format read case (Jiri Olsa) [1011533]
- [tools] perf: Add support for parsing PERF_SAMPLE_READ sample type (Jiri Olsa) [1011533]
- [kernel] perf/evlist: Use PERF_EVENT_IOC_ID perf ioctl to read event id (Jiri Olsa) [1011533]
- [kernel] perf: Do not get values from disabled counters in group format read (Jiri Olsa) [1011533]
- [kernel] perf: Add PERF_EVENT_IOC_ID ioctl to return event ID (Jiri Olsa) [1011533]
- [kernel] add support for init_array constructors fix (Frantisek Hrbata) [824466]
- [kernel] add support for init_array constructors (Frantisek Hrbata) [824466]
- [kernel] gcov: compile specific gcov implementation based on gcc version (Frantisek Hrbata) [824466]
- [kernel] gcov: add support for gcc 47 gcov format fix 3 (Frantisek Hrbata) [824466]
- [kernel] gcov: add support for gcc 47 gcov format checkpatch fixes (Frantisek Hrbata) [824466]
- [kernel] gcov: add support for gcc 47 gcov format fix fix (Frantisek Hrbata) [824466]
- [kernel] gcov: add support for gcc 47 gcov format fix (Frantisek Hrbata) [824466]
- [kernel] gcov: add support for gcc 4.7 gcov format (Frantisek Hrbata) [824466]
- [kernel] gcov: move gcov structs definitions to a gcc version specific file (Frantisek Hrbata) [824466]

* Mon Sep 30 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-30.el7]
- [drm] qxl: add delayed fb operations (Dave Airlie) [1002056]
- [edac] Fix lockdep splat (Aristeu Rozanski) [967459]
- [mm] vmalloc: fix memleak in __vunmap (Jan Stancek) [1012358]
- [x86] perf_event_amd: Rework AMD PMU init code (Prarit Bhargava) [1000672]
- [md] dm: add reserved_bio_based_ios module parameter (Mike Snitzer) [1010450]
- [md] dm: add reserved_rq_based_ios module parameter (Mike Snitzer) [1010450]
- [md] dm: lower bio-based mempool reservation (Mike Snitzer) [1010450]
- [block] Add nr_bios to block_rq_remap tracepoint (Mike Snitzer) [1010450]
- [md] dm-mpath: disable WRITE SAME if it fails (Mike Snitzer) [987454]
- [md] dm-mpath: do not fail path on -ENOSPC (Mike Snitzer) [1010437]
- [scsi] Return ENODATA on medium error (Mike Snitzer) [1010437]
- [scsi] return ENOSPC on thin provisioning failure (Mike Snitzer) [1010437]
- [scsi] Set hostbyte status in scsi_check_sense() (Mike Snitzer) [1010437]
- [scsi] Document enhanced error codes (Mike Snitzer) [1010437]
- [md] dm-thin: do not expose non-zero discard limits if discards disabled (Mike Snitzer) [998421]
- [md] dm-snapshot: fix performance degradation due to small hash size (Mike Snitzer) [1010437]
- [md] dm-snapshot: workaround for a false positive lockdep warning (Mike Snitzer) [1010437]
- [md] dm-stripe: silence a couple sparse warnings (Mike Snitzer) [1010437]
- [md] dm-stats: fix possible counter corruption on 32-bit systems (Mike Snitzer) [1010437]
- [md] dm: add statistics support (Mike Snitzer) [1010437]
- [lib] math64: New separate div64_u64_rem helper (Mike Snitzer) [1010437]
- [md] dm-thin: always return -ENOSPC if no_free_space is set (Mike Snitzer) [1010437]
- [md] dm-ioctl: cleanup error handling in table_load (Mike Snitzer) [1010437]
- [md] dm-ioctl: increase granularity of type_lock when loading table (Mike Snitzer) [1010437]
- [md] dm-ioctl: prevent rename to empty name or uuid (Mike Snitzer) [1010437]
- [md] dm-thin: set pool read-only if breaking_sharing fails block allocation (Mike Snitzer) [1010437]
- [md] dm-thin: prefix pool error messages with pool device name (Mike Snitzer) [1010437]
- [md] dm: allow error target to replace bio-based and request-based targets (Mike Snitzer) [1010437]
- [md] dm-space-map: optimise sm_ll_dec and sm_ll_inc (Mike Snitzer) [1010437]
- [md] dm-btree: prefetch child nodes when walking tree for a dm_btree_del (Mike Snitzer) [1010437]
- [md] dm-btree: use pop_frame in dm_btree_del to cleanup code (Mike Snitzer) [1010437]
- [md] dm-cache: eliminate holes in cache structure (Mike Snitzer) [1010437]
- [md] dm-cache: fix stacking of geometry limits (Mike Snitzer) [1010437]
- [md] dm-thin: fix stacking of geometry limits (Mike Snitzer) [1010437]
- [md] dm-cache: add data block size limits to code and Documentation (Mike Snitzer) [1010437]
- [md] dm: stop using WQ_NON_REENTRANT (Mike Snitzer) [1010437]
- [md] dm-cache: avoid conflicting remove_mapping() in mq policy (Mike Snitzer) [1010437]
- [md] dm: optimize reorder structure (Mike Snitzer) [1010437]
- [md] dm: optimize use SRCU and RCU (Mike Snitzer) [1010437]
- [md] dm-bufio: submit writes outside lock (Mike Snitzer) [1010437]
- [md] dm-cache: fix arm link errors with inline (Mike Snitzer) [1010437]
- [md] dm-verity: use __ffs and __fls (Mike Snitzer) [1010437]
- [md] dm-flakey: correct ctr alloc failure mesg (Mike Snitzer) [1010437]
- [md] dm-verity: remove pointless comparison (Mike Snitzer) [1010437]
- [md] dm: use __GFP_HIGHMEM in __vmalloc (Mike Snitzer) [1010437]
- [md] dm-verity: fix inability to use a few specific devices sizes (Mike Snitzer) [1010437]
- [md] dm-ioctl: set noio flag to avoid __vmalloc deadlock (Mike Snitzer) [1010437]
- [md] dm-mpath: fix ioctl deadlock when no paths (Mike Snitzer) [1010437]
- [powerpc] Default arch idle could cede processor on pseries (Steve Best) [1008895]

* Wed Sep 25 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-29.el7]
- [s390] zfcp: remove access control tables interface (keep sysfs files) (Hendrik Brueckner) [1006516]
- [s390] zfcp: fix lock imbalance by reworking request queue locking (Hendrik Brueckner) [1006525]
- [s390] zfcp: fix schedule-inside-lock in scsi_device list loops (Hendrik Brueckner) [1006524]
- [x86] setup: avoid remapping data in parse_setup_data() (Nigel Croxon) [1004428]
- [hid] validate HID report id size (Frantisek Hrbata) [1000454] {CVE-2013-2888}
- [kernel] userns: prevent the use of user namespaces (Aristeu Rozanski) [993320]
- [crypto] x509: don't reject not-yet-valid keys (kyle mcmartin) [905910]
- [kernel] perf: Prevent race in unthrottling code (Jiri Olsa) [992941]
- [s390] pci: use adapter interrupt vector helpers (Hendrik Brueckner) [1005896]
- [s390] pci: cleanup function names (Hendrik Brueckner) [1005896]
- [s390] airq: introduce adapter interrupt vector helper (Hendrik Brueckner) [1005896]
- [s390] pci: use virtual memory for iommu bitmap (Hendrik Brueckner) [1005896]
- [s390] cio: fix unlocked access of global bitmap (Hendrik Brueckner) [1005896]
- [s390] pci: update function handle after resume from hibernate (Hendrik Brueckner) [1005896]
- [s390] pci: try harder to modify a function (Hendrik Brueckner) [1005896]
- [s390] pci: split lpf (Hendrik Brueckner) [1005896]
- [s390] hibernate: add early resume function (Hendrik Brueckner) [1005896]
- [s390] pci: add recover sysfs knob (Hendrik Brueckner) [1005896]
- [s390] pci: use claim_resource (Hendrik Brueckner) [1005896]
- [s390] pci/hotplug: convert to be builtin only (Hendrik Brueckner) [1005896]
- [s390] airq: simplify adapter interrupt code (Hendrik Brueckner) [1005896]
- [s390] qdio: cleanup chsc SADC usage (Hendrik Brueckner) [1005896]
- [s390] qdio: cleanup chsc SSQD usage (Hendrik Brueckner) [1005896]
- [s390] pci: remove per device debug attribute (Hendrik Brueckner) [1005896]
- [s390] pci: sysfs remove strlen (Hendrik Brueckner) [1005896]
- [s390] pci: remove pdev during unplug (Hendrik Brueckner) [1005896]
- [s390] pci: cleanup hotplug code (Hendrik Brueckner) [1005896]
- [s390] pci: implement pcibios_release_device (Hendrik Brueckner) [1005896]
- [s390] pci: use to_pci_dev (Hendrik Brueckner) [1005896]
- [netdrv] sfc: check for allocation failure (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Update copyright banners (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add support for Solarflare SFC9100 family (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Make efx_mcdi_{init, fini}() call efx_mcdi_drv_attach() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Allocate NVRAM partition ID range for PHY images (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add EF10 register and structure definitions (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Extend struct efx_tx_buffer to allow pushing option descriptors (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Use a global count of active queues instead of pending drains (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Prepare for RX scatter on EF10 (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Initialise IRQ moderation for all NIC types from efx_init_eventq() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Allow efx_nic_type::dimension_resources to fail (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Allow event queue initialisation to fail (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Document conditions for multicast replication vs filter replacement (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Implement asynchronous MCDI requests (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove unnecessary use of atomic_t (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Refactor efx_mcdi_rpc_start() and efx_mcdi_copyin() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add support for new board sensors (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Use extended MC_CMD_SENSOR_INFO and MC_CMD_READ_SENSORS (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Return an error code when a sensor is busy (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add support for reading packet length from prefix (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add TX merged completion counter (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Generalise packet hash lookup to support EF10 RX prefix (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rename EFX_PAGE_BLOCK_SIZE to EFX_VI_PAGE_SIZE and adjust comments (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove early call to efx_nic_type::reconfigure_mac in efx_reset_up() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: use MCDI epoch flag to improve MC reboot detection in the driver (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add EF10 support for TX/RX DMA error events handling (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add a function pointer to abstract write of host time into NIC shared memory (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: PTP MCDI requests need to initialise periph ID field (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Delegate MAC/NIC statistic description to efx_nic_type (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove driver-local struct ethtool_string (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove more left-overs from Falcon GMAC support (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move MTD operations into efx_nic_type (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move NIC-type-specific MTD partition date into separate structures (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Eliminate struct efx_mtd (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rename SPI stuff to show that it is Falcon-specific (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Cleanup Falcon-arch simple MAC filter state (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Define and use MCDI_POPULATE_DWORD_{1, 2, 3, 4, 5, 6, 7} (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add flag for stack-owned RX MAC filters (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Refactor Falcon-arch filter removal (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Make most filter operations NIC-type-specific (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Refactor Falcon-arch search limit reset (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Split Falcon-arch-specific and common filter state (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Extend and abstract efx_filter_spec to cover Huntington/EF10 (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Name the RX drop queue ID (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rename Falcon-arch filter implementation types and functions (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove unused filter_flags variables and efx_farch_filter_id_flags() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Do not assume efx_nic_type::ev_fini is idempotent (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: EFX_WORKAROUND_ALWAYS is really specific to Falcon-architecture (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Get rid of per-NIC-type phys_addr_channels and mem_map_size (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Update and improve kernel-doc for efx_mcdi_state & efx_mcdi_iface (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fix race in completion handling (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add support for MCDI v2 (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Update MCDI protocol definitions for EF10 (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Translate MCDI error numbers received in events (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move and rename Falcon/Siena common NIC operations (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Refactor queue teardown sequence to allow for EF10 flush behaviour (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove bogus call to efx_release_tx_buffers() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Stop RX refill before flushing RX queues (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Limit scope of a Falcon A1 IRQ workaround (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rework IRQ enable/disable (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Remove efx_process_channel_now() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rename Falcon-architecture register definitions (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Make struct efx_special_buffer less special (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add GFP flags to efx_nic_alloc_buffer() and make most callers allow blocking (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Make MCDI independent of Siena (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Make efx_mcdi_init() call efx_mcdi_handle_assertion() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Collect all MCDI port functions into mcdi_port.c (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move efx_mcdi_mac_reconfigure() to siena.c and rename (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move siena_reset_hw() and siena_map_reset_reason() into MCDI module (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Add and use MCDI_SET_QWORD() and MCDI_SET_ARRAY_QWORD() (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Ensure MCDI buffers, but not lengths, are dword aligned (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Use proper macros to declare and access MCDI arrays (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Introduce and use MCDI_CTL_SDU_LEN_MAX_V1 macro for Siena-specific code (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fill out the set of MCDI accessors (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Rationalise MCDI buffer accessors (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Introduce and use MCDI_DECLARE_BUF macro (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move more Falcon-specific code and definitions into falcon.c (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Move details of a Falcon bug workaround out of ethtool.c (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Use efx_mcdi_mon() to find efx_mcdi_mon structure from efx_nic (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: const-qualify source pointers for MMIO write functions (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fix lookup of default RX MAC filters when steered using ethtool (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Enable RX scatter for flows steered by RFS (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fix memory leak when discarding scattered packets (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Improve test for IOMMU in use (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fix IRQ cleanup in case of a probe failure (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Do not pass non-TCP packets into GRO code (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Define and set RX buffer flag for packets parsed as TCP (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Enable accelerated RFS on vlans (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Report software timestamping capabilities (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Increase size of RX SKB header area (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Enable RX checksum offload for packets not handled by GRO (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Fix EEH with legacy interrupts (Nikolay Aleksandrov) [1005248]
- [netdrv] sfc: Store port number in private data, not net_device::dev_id (Nikolay Aleksandrov) [1005248]

* Mon Sep 23 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-28.el7]
- [fs] namei: Add missing unlocks to error paths of mountpoint_last (Jeff Layton) [980172]
- [fs] autofs4: fix device ioctl mount lookup (Jeff Layton) [980172]
- [fs] namei: introduce kern_path_mountpoint() (Jeff Layton) [980172]
- [fs] namei: rename user_path_umountat() to user_path_mountpoint_at() (Jeff Layton) [980172]
- [fs] namei: take unlazy_walk() into umount_lookup_last() (Jeff Layton) [980172]
- [fs] vfs: allow umount to handle mountpoints without revalidating them (Jeff Layton) [980172]
- [acpi] apei: Soft-offline a page on firmware GHES notification (Janet Morgan) [984133]
- [acpi] apei: Add a boot option to disable ff mode for corrected errors (Janet Morgan) [984133]
- [mcheck] mce: Honour Firmware First for MCA banks listed in APEI HEST CMC (Janet Morgan) [984133]
- [fs] cifs: Respect epoch value from create lease context v2 (Sachin Prabhu) [1007981]
- [fs] cifs: Add create lease v2 context for SMB3 (Sachin Prabhu) [1007981]
- [fs] cifs: Move parsing lease buffer to ops struct (Sachin Prabhu) [1007981]
- [fs] cifs: Move creating lease buffer to ops struct (Sachin Prabhu) [1007981]
- [fs] cifs: Store lease state itself rather than a mapped oplock value (Sachin Prabhu) [1007981]
- [fs] cifs: Replace clientCanCache* bools with an integer (Sachin Prabhu) [1007981]
- [fs] cifs: quiet sparse compile warning (Sachin Prabhu) [1007981]
- [fs] cifs: Start using per session key for smb2/3 for signature generation (Sachin Prabhu) [1007981]
- [fs] cifs: Add a variable specific to NTLMSSP for key exchange (Sachin Prabhu) [1007981]
- [fs] cifs: Process post session setup code in respective dialect functions (Sachin Prabhu) [1007981]
- [fs] cifs: convert to use le32_add_cpu() (Sachin Prabhu) [1007981]
- [fs] cifs: Fix missing lease break (Sachin Prabhu) [1007981]
- [fs] cifs: Fix a memory leak when a lease break comes (Sachin Prabhu) [1007981]
- [fs] cifs: convert case-insensitive dentry ops to use new case conversion routines (Sachin Prabhu) [1007981]
- [fs] cifs: add new case-insensitive conversion routines that are based on wchar_t's (Sachin Prabhu) [1007981]
- [fs] cifs: Move and expand MAX_SERVER_SIZE definition (Sachin Prabhu) [1007981]
- [fs] cifs: Expand max share name length to 256 (Sachin Prabhu) [1007981]
- [fs] cifs: Move string length definitions to uapi (Sachin Prabhu) [1007981]
- [fs] cifs: Implement follow_link for nounix CIFS mounts (Sachin Prabhu) [1007981]
- [fs] cifs: Implement follow_link for SMB2 (Sachin Prabhu) [1007981]
- [fs] cifs: display iocharset= option in /proc/mounts (Sachin Prabhu) [1007981]
- [fs] cifs: create a new Documentation/ directory and move docfiles into it (Sachin Prabhu) [1007981]
- [fs] cifs: ensure that srv_mutex is held when dealing with ssocket pointer (Sachin Prabhu) [1007981]
- [fs] cifs: don't instantiate new dentries in readdir for inodes that need to be revalidated immediately (Sachin Prabhu) [1007981]
- [fs] cifs: set sb->s_d_op before calling d_make_root() (Sachin Prabhu) [1007981]
- [fs] cifs: file, initialize oparms.reconnect before using it (Sachin Prabhu) [1007981]
- [fs] cifs: Do not attempt to do cifs operations reading symlinks with SMB2 (Sachin Prabhu) [1007981]
- [fs] cifs: extend the buffer length enought for sprintf() using (Sachin Prabhu) [1007981]
- [fs] dlm: log an error for unmanaged lockspaces (David Teigland) [1008005]
- [acpi] acpi_ipmi, replace mutex with spin_lock_irqsave (Tony Camuso) [1007574]
- [kernel] sched: Micro-optimize the smart wake-affine logic (Larry Woodman) [947186]
- [kernel] sched: Implement smarter wake-affine logic (Larry Woodman) [947186]
- [net] sunrpc: rpcauth_create needs to know about rpc_clnt clone status (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Share all credential caches on a per-transport basis (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Share rpc_pipes when an rpc_clnt owns multiple rpcsec auth caches (Jeff Layton) [1002576]
- [net] sunrpc: Add a helper to allow sharing of rpc_pipefs directory objects (Jeff Layton) [1002576]
- [net] sunrpc: Remove the rpc_client->cl_dentry (Jeff Layton) [1002576]
- [fs] nfs: Convert idmapper to use the new framework for pipefs dentries (Jeff Layton) [1002576]
- [net] sunrpc: Remove the obsolete auth-only interface for pipefs dentry management (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Switch auth_gss to use the new framework for pipefs dentries (Jeff Layton) [1002576]
- [net] sunrpc: Add a framework to clean up management of rpc_pipefs directories (Jeff Layton) [1002576]
- [fs] nfs: Fix a potentially Oopsable condition in __nfs_idmap_unregister (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Fix an Oopsable condition when creating/destroying pipefs objects (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Further cleanups (Jeff Layton) [1002576]
- [net] sunrpc: Replace clnt->cl_principal (Jeff Layton) [1002576]
- [net] sunrpc: RPCSEC_GSS, Clean up upcall message allocation (Jeff Layton) [1002576]
- [net] sunrpc: Cleanup rpc_setup_pipedir (Jeff Layton) [1002576]
- [net] sunrpc: Remove unused struct rpc_clnt field cl_protname (Jeff Layton) [1002576]
- [net] sunrpc: Deprecate rpc_client->cl_protname (Jeff Layton) [1002576]
- [net] sunrpc/rpc_pipe: convert back to simple_dir_inode_operations (Jeff Layton) [1002576]
- [fs] libfs: make simple_lookup() usable for filesystems that set ->s_d_op (Jeff Layton) [1002576]
- [net] sunrpc: __rpc_lookup_create_exclusive, pass string instead of qstr (Jeff Layton) [1002576]
- [net] sunrpc: rpc_create_*_dir, don't bother with qstr (Jeff Layton) [1002576]

* Mon Sep 23 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-27.el7]
- [netdrv] i40e: include i40e in kernel proper (Stefan Assmann) [726825]
- [netdrv] i40e: debugfs interface (Stefan Assmann) [726825]
- [netdrv] i40e: init code and hardware support (Stefan Assmann) [726825]
- [netdrv] i40e: implement virtual device interface (Stefan Assmann) [726825]
- [netdrv] i40e: driver core headers (Stefan Assmann) [726825]
- [netdrv] i40e: driver ethtool core (Stefan Assmann) [726825]
- [netdrv] i40e: transmit, receive, and NAPI (Stefan Assmann) [726825]
- [netdrv] i40e: main driver core (Stefan Assmann) [726825]
- [netdrv] e1000e: balance semaphore put/get for 82573 (Dean Nelson) [726816]
- [netdrv] e1000e: resolve checkpatch JIFFIES_COMPARISON warning (Dean Nelson) [726816]
- [netdrv] e1000e: Avoid kernel crash during shutdown (Dean Nelson) [726816]
- [netdrv] e1000e: Add code to check for failure of pci_disable_link_state call (Dean Nelson) [726816]
- [netdrv] e1000e: cleanup whitespace in recent commit (Dean Nelson) [726816]
- [netdrv] e1000e: fix I217/I218 PHY initialization flow (Dean Nelson) [726816]
- [netdrv] e1000e: do not resume device from RPM suspend to read PHY status registers (Dean Nelson) [726816]
- [netdrv] e1000e: enable support for new device IDs (Dean Nelson) [726816]
- [netdrv] e1000e: ethtool unnecessarily takes device out of RPM suspend (Dean Nelson) [726816]
- [netdrv] e1000e: Tx hang on I218 when linked at 100Half and slow response at 10Mbps (Dean Nelson) [726816]
- [netdrv] e1000e: low throughput using 4K jumbos on I218 (Dean Nelson) [726816]
- [netdrv] e1000e: iAMT connections drop on driver unload when jumbo frames enabled (Dean Nelson) [726816]
- [netdrv] e1000e: disable ASPM L1 on 82583 (Dean Nelson) [726816]
- [netdrv] e1000e: Use marco instead of digit for defining e1000_rx_desc_packet_split (Dean Nelson) [726816]
- [netdrv] e1000e: Remove duplicate assignment of default rx/tx ring size (Dean Nelson) [726816]
- [netdrv] e1000e: restore call to pci_clear_master() (Dean Nelson) [726816]
- [netdrv] e1000e: Release mutex lock only if it has been initially acquired (Dean Nelson) [726816]
- [netdrv] e1000e: prevent warning from -Wunused-parameter (Dean Nelson) [726816]
- [netdrv] e1000e: cleanup whitespace (Dean Nelson) [726816]
- [netdrv] bna: Staticize local functions (Ivan Vecera) [978045]
- [netdrv] bna: switch to fixed_size_llseek() (Ivan Vecera) [978045]
- [fs] read_write: new helper, fixed_size_llseek() (Ivan Vecera) [978045]
- [netdrv] bna: Driver and Firmware Updated (Ivan Vecera) [978045]
- [netdrv] bna: Enahncement to Identify Default IOC Function (Ivan Vecera) [978045]
- [netdrv] bna: Fix Ucast Failure Handling (Ivan Vecera) [978045]
- [netdrv] bna: Clear Driver Config Flags When HW Resets (Ivan Vecera) [978045]
- [netdrv] tg3: Don't turn off led on 5719 serdes port 0 (Ivan Vecera) [1006987]
- [netdrv] tg3: Convert dma_alloc_coherent(...__GFP_ZERO) to dma_zalloc_coherent (Ivan Vecera) [1006987]
- [netdrv] tg3: fix NULL pointer dereference in tg3_io_error_detected and tg3_io_slot_reset (Ivan Vecera) [1006987]
- [netdrv] tg3: clean up unnecessary MSI/MSI-X capability find (Ivan Vecera) [1006987]
- [netdrv] tg3: Fix warning from pci_disable_device() (Ivan Vecera) [1006987]
- [netdrv] tg3: Fix kernel crash (Ivan Vecera) [1006987]
- [netdrv] tg3: Update version to 3.133 (Ivan Vecera) [1006987]
- [netdrv] tg3: Fix UDP fragments treated as RMCP (Ivan Vecera) [1006987]
- [netdrv] tg3: Enable support for timesync gpio output (Ivan Vecera) [1006987]
- [netdrv] tg3: Implement the shutdown handler (Ivan Vecera) [1006987]
- [netdrv] tg3: Allow NVRAM programming when interface is down (Ivan Vecera) [1006987]
- [netdrv] tg3: Remove incorrect switch to aux power (Ivan Vecera) [1006987]
- [netdrv] tg3: Prevent system hang during repeated EEH errors (Ivan Vecera) [1006987]
- [netdrv] tg3: remove redundant pm init code (Ivan Vecera) [1006987]
- [netdrv] tg3: Remove unnecessary lock around tg3_flag_set (Ivan Vecera) [1006987]
- [netdrv] tg3: Fix misplaced empty line (Ivan Vecera) [1006987]
- [netdrv] tg3: Use descriptive label names in tg3_start (Ivan Vecera) [1006987]
- [netdrv] tg3: Make tg3_rings_reset() more concise (Ivan Vecera) [1006987]
- [netdrv] tg3: Simplify ring control block setup (Ivan Vecera) [1006987]
- [netdrv] tg3: Split APE driver state change out of boot reset signature update (Ivan Vecera) [1006987]
- [netdrv] tg3: Use module_pci_driver to register driver (Ivan Vecera) [1006987]
- [netdrv] tg3: Implement set/get_eee handlers (Ivan Vecera) [1006987]
- [netdrv] tg3: Simplify tg3_phy_eee_config_ok() by reusing tg3_eee_pull_config() (Ivan Vecera) [1006987]
- [netdrv] tg3: Add tg3_eee_pull_config() function (Ivan Vecera) [1006987]
- [netdrv] tg3: Add ethtool_eee struct and tg3_setup_eee() (Ivan Vecera) [1006987]
- [netdrv] be2net: set and query VEB/VEPA mode of the PF interface (Ivan Vecera) [726160]
- [netdrv] be2net: Convert dma_alloc_coherent(...__GFP_ZERO) to dma_zalloc_coherent (Ivan Vecera) [726160]
- [netdrv] be2net: implement ethtool set/get_channel hooks (Ivan Vecera) [726160]
- [netdrv] be2net: refactor be_setup() to consolidate queue creation routines (Ivan Vecera) [726160]
- [netdrv] be2net: Fix be_cmd_if_create() to use MBOX if MCCQ is not created (Ivan Vecera) [726160]
- [netdrv] be2net: refactor be_get_resources() code (Ivan Vecera) [726160]
- [netdrv] be2net: Fixup profile management routines (Ivan Vecera) [726160]
- [netdrv] be2net: use EQ_CREATEv2 for SH-R (Ivan Vecera) [726160]
- [netdrv] be2net: Check for POST state in suspend-resume sequence (Ivan Vecera) [726160]
- [netdrv] be2net: fix disabling TX in be_close() (Ivan Vecera) [726160]
- [netdrv] be2net: Clear any capability flags that driver is not interested in (Ivan Vecera) [726160]
- [netdrv] be2net: update driver version (Ivan Vecera) [726160]
- [netdrv] be2net: Initialize "status" in be_cmd_get_die_temperature() (Ivan Vecera) [726160]
- [netdrv] be2net: fixup log msgs for async events (Ivan Vecera) [726160]
- [netdrv] be2net: Fix displaying supported speeds for BE2 (Ivan Vecera) [726160]
- [netdrv] be2net: don't limit max MAC and VLAN counts (Ivan Vecera) [726160]
- [netdrv] be2net: Do not call get_die_temperature cmd for VF (Ivan Vecera) [726160]
- [netdrv] be2net: Adding more speeds reported by get_settings (Ivan Vecera) [726160]
- [netdrv] be2net: Staticize local functions (Ivan Vecera) [726160]
- [netdrv] be2net: don't use dev_err when AER enabling fails (Ivan Vecera) [726160]
- [netdrv] be2net: delete primary MAC address while unloading (Ivan Vecera) [726160]
- [netdrv] be2net: use SET/GET_MAC_LIST for SH-R (Ivan Vecera) [726160]
- [netdrv] be2net: refactor MAC-addr setup code (Ivan Vecera) [726160]
- [netdrv] be2net: fix pmac_id for BE3 VFs (Ivan Vecera) [726160]
- [netdrv] be2net: allow VFs to program MAC and VLAN filters (Ivan Vecera) [726160]
- [netdrv] be2net: fix MAC address modification for VF (Ivan Vecera) [726160]
- [netdrv] be2net: replace numeric with standard PM state macros (Ivan Vecera) [726160]
- [netdrv] be2net: use pci_vfs_assigned()/pci_num_vf() instead of be_find_vfs() (Ivan Vecera) [726160]
- [netdrv] be2net: Implement initiate FW dump feature for Lancer (Ivan Vecera) [726160]
- [netdrv] be2net: Trim padded packets for Lancer (Ivan Vecera) [726160]
- [netdrv] be2net: Pad skb to meet min Tx pkt size in lancer (Ivan Vecera) [726160]
- [netdrv] be2net: cleanup be_get_drvinfo() (Ivan Vecera) [726160]
- [netdrv] be2net: refactor HW workarounds in be_xmit() (Ivan Vecera) [726160]
- [netdrv] mlx5: remove unused MLX5_DEBUG param in Kconfig (Amir Vadai) [864578]
- [netdrv] mlx5: Support MANAGE_PAGES and QUERY_PAGES firmware command changes (Amir Vadai) [864578]
- [netdrv] mlx5: remove health handler plugin (Amir Vadai) [864578]
- [infiniband] mlx5: Variable may be used uninitialized (Amir Vadai) [864578]
- [netdrv] mlx5: Implement new initialization sequence (Amir Vadai) [864578]
- [infiniband] mlx5: Fix stack info leak in mlx5_ib_alloc_ucontext() (Amir Vadai) [864578]
- [infiniband] mlx5: Fix error return code in init_one() (Amir Vadai) [864578]
- [netdrv] mlx5: fix error return code in mlx5_alloc_uuars() (Amir Vadai) [864578]
- [netdrv] mlx5: use after free in mlx5_cmd_comp_handler() (Amir Vadai) [864578]
- [netdrv] mlx5: Fix __udivdi3 when compiling for 32 bit arches (Amir Vadai) [864578]
- [netdrv] mlx5: Return -EFAULT instead of -EPERM (Amir Vadai) [864578]
- [netdrv] mlx5: Adjust hca_cap.uar_page_sz to conform to Connect-IB spec (Amir Vadai) [864578]
- [netdrv] mlx5: Fixes for sparse warnings (Amir Vadai) [864578]
- [infiniband] mlx5: Make profile[] static in main.c (Amir Vadai) [864578]
- [infiniband] mlx5: Add driver for Mellanox Connect-IB adapters (Amir Vadai) [864578]
- [infiniband] core: Add reserved values to enums for low-level driver use (Amir Vadai) [864578]

* Thu Sep 19 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-26.el7]
- [net] tuntap: correctly handle error in tun_set_iff() (Jiri Benc) [1007739] {CVE-2013-4343}
- [net] sctp: fix ipv6 ipsec encryption bug in sctp_v6_xmit (Daniel Borkmann) [998398] {CVE-2013-4350}
- [net] netlink: filter particular protocols from analyzers (Daniel Borkmann) [957721]
- [net] ipv6: accept tlv which includes only padding (Jiri Pirko) [990968]

* Thu Sep 19 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-25.el7]
- [scsi] mpt2sas: Bump driver version to v16.100.00.00 (Tomas Henzl) [736230]
- [scsi] mpt2sas: Remove phys on topology change (Tomas Henzl) [736230]
- [scsi] mpt2sas: Fix for kernel panic when driver loads with HBA connected to non LUN 0 configured expander (Tomas Henzl) [736230]
- [scsi] mpt2sas: when Async scanning is enabled then while scanning, devices are removed but their transport layer entries are not removed (Tomas Henzl) [736230]
- [scsi] mpt2sas: Infinite loop can occur if MPI2_IOCSTATUS_CONFIG_INVALID_PAGE is not returned (Tomas Henzl) [736230]
- [scsi] mpt2sas: The copyright in driver sources is updated for the year 2013 (Tomas Henzl) [736230]
- [scsi] mpt2sas: MPI2 Rev X (2.00.16) specifications (Tomas Henzl) [736230]
- [scsi] mpt2sas: Change in MPI2_RAID_ACTION_SYSTEM_SHUTDOWN_INITIATED notification methodology (Tomas Henzl) [736230]
- [scsi] mpt2sas: Null pointer deference possibility in mpt2sas_ctl_event_callback function (Tomas Henzl) [736230]
- [scsi] mpt2sas: fix cleanup on controller resource mapping failure (Tomas Henzl) [736230]
- [scsi] mpt2sas: fix for unused variable 'event_data' warning (Tomas Henzl) [736230]
- [scsi] mpt2sas: Calulate the Reply post queue depth calculation as per the MPI spec (Tomas Henzl) [736230]
- [scsi] mpt2sas: fix firmware failure with wrong task attribute (Tomas Henzl) [736230]
- [scsi] mpt2sas: Fix for device scan following host reset could get stuck in a infinite loop (Tomas Henzl) [736230]
- [scsi] mpt2sas: Update the timing requirements for issuing a Hard Reset (Tomas Henzl) [736230]
- [scsi] mpt2sas: MPI2 Rev W (2.00.15) specification (Tomas Henzl) [736230]
- [powerpc] Fix possible deadlock on page fault (Steve Best) [999374]
- [scsi] qla2xxx: Update driver version to 8.06.00.08.07.0-k (Chad Dupuis) [725014]
- [scsi] qla2xxx: Select link initialization option bits from current operating mode (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add loopback IDC-TIME-EXTEND aen handling support (Chad Dupuis) [725014]
- [scsi] qla2xxx: Set default critical temperature value in cases when ISPFX00 firmware doesn't provide it (Chad Dupuis) [725014]
- [scsi] qla2xxx: QLAFX00 make over temperature AEN handling informational, add log for normal temperature AEN (Chad Dupuis) [725014]
- [scsi] qla2xxx: Correct Interrupt Register offset for ISPFX00 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove handling of Shutdown Requested AEN from qlafx00_process_aen() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Send all AENs for ISPFx00 to above layers (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add changes in initialization for ISPFX00 cards with BIOS (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add changes to support extended IOs for ISPFX00 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add missing FCP statistics to sysfs interface (Chad Dupuis) [725014]
- [scsi] qla2xxx: Make log message that prints when a completion status requires a port down more readable (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add critical temperature handling for ISPFX00 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Notify ISPFX00 firmware when driver is unloaded or system is shut down (Chad Dupuis) [725014]
- [scsi] qla2xxx: Reconfigure thermal temperature (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add setting of driver version string for vendor application (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove QL_DEBUG_LEVEL_17 defines from qla_nx.c (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add ISPFX00 specific bus reset routine (Chad Dupuis) [725014]
- [scsi] qla2xxx: Perform warm reset every 2 minutes if firmware load fails for ISPFX00 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Set factory reset recovery timeout to 10 min. for ISPFX00 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Correct multiqueue offset calculations (Chad Dupuis) [725014]
- [scsi] qla2xxx: Fix incorrect test after list_for_each_entry() exits (Chad Dupuis) [725014]
- [scsi] qla2xxx: Add support for ISP8044 (Chad Dupuis) [725014]
- [scsi] qla2xxx: Print some variables to hexadecimal string via *phN format (Chad Dupuis) [725014]
- [scsi] qla2xxx: Fix sparse warnings in qlafx00_fxdisc_iocb function (Chad Dupuis) [725014]
- [scsi] qla2xxx: Properly set the tagging for commands (Chad Dupuis) [725014]
- [scsi] qla2xxx: Fix a memory leak in an error path of qla2x00_process_els() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove an unused variable from qla2x00_remove_one() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Fix qla2xxx_check_risc_status() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Help Coverity with analyzing ct_sns_pkt initialization (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove redundant assignments (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove a dead assignment in qla24xx_build_scsi_crc_2_iocbs() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove two superfluous tests (Chad Dupuis) [725014]
- [scsi] qla2xxx: Remove dead code in qla2x00_configure_hba() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Clean up qla84xx_mgmt_cmd() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Clean up qla24xx_iidma() (Chad Dupuis) [725014]
- [scsi] qla2xxx: Fix sparse warning from qla_mr.c and qla_iocb.c (Chad Dupuis) [725014]
- [scsi] qla2xxx: Do not take a second firmware dump when intentionally generating one (Chad Dupuis) [725014]
- [scsi] qla2xxx: Do not query FC statistics during chip reset (Chad Dupuis) [725014]
- [scsi] qla2xxx: Move qla2x00_free_device to the correct location (Chad Dupuis) [725014]
- [scsi] qla2xxx: Set the index in outstanding command array to NULL when cmd is aborted when the request timeout (Chad Dupuis) [725014]
- [scsi] qla2xxx: Clear the MBX_INTR_WAIT flag when the mailbox time-out happens (Chad Dupuis) [725014]
- [scsi] mpt3sas: Bump driver version to v02.100.00.00 (Tomas Henzl) [889435]
- [scsi] mpt3sas: Added a driver module parameter max_msix_vectors (Tomas Henzl) [889435]
- [scsi] mpt3sas: fix cleanup on controller resource mapping failure (Tomas Henzl) [889435]
- [scsi] mpt3sas: when async scanning is enabled then while scanning, devices are removed but their transport layer entries are not removed (Tomas Henzl) [889435]
- [scsi] mpt3sas: MPI2.5 Rev F v2.5.1.1 specification (Tomas Henzl) [889435]
- [scsi] mpt3sas: Infinite loops can occur if MPI2_IOCSTATUS_CONFIG_INVALID_PAGE is not returned (Tomas Henzl) [889435]
- [scsi] mpt3sas: fix for kernel panic when driver loads with HBA conected to non LUN 0 configured expander (Tomas Henzl) [889435]
- [scsi] mpt3sas: Updated the Hardware timing requirements (Tomas Henzl) [889435]
- [scsi] mpt3sas: 2013 source code copyright (Tomas Henzl) [889435]
- [netdrv] ixgbe: add support for older QSFP active DA cables (Andy Gospodarek) [726818]
- [netdrv] ixgbe: include QSFP PHY types in ixgbe_is_sfp() (Andy Gospodarek) [726818]
- [netdrv] ixgbe: add 1Gbps support for QSFP+ (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix SFF data dumps of SFP+ modules from an offset (Andy Gospodarek) [726818]
- [netdrv] ixgbe: cleanup some log messages (Andy Gospodarek) [726818]
- [netdrv] ixgbe: zero out mailbox buffer on init (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix link test when connected to 1Gbps link partner (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix incorrect limit value in ring transverse (Andy Gospodarek) [726818]
- [netdrv] ixgbe: Check return value on eeprom reads (Andy Gospodarek) [726818]
- [netdrv] ixgbe: disable link when adapter goes down (Andy Gospodarek) [726818]
- [netdrv] ixgbe: add support for quad-port x520 adapter (Andy Gospodarek) [726818]
- [netdrv] ixgbe: clear semaphore bits on timeouts (Andy Gospodarek) [726818]
- [netdrv] ixgbe: rename LL_EXTENDED_STATS to use queue instead of q (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix lockdep annotation issue for ptp's work item (Andy Gospodarek) [726818]
- [netdrv] ixgbe: call pcie_get_mimimum_link to check if device has enough bandwidth (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix SFF data dumps of SFP+ modules (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix semaphore lock for I2C read/writes on 82598 (Andy Gospodarek) [726818]
- [netdrv] ixgbe: bump version number (Andy Gospodarek) [726818]
- [netdrv] ixgbe: add new media type (Andy Gospodarek) [726818]
- [netdrv] ixgbe: fix fc autoneg ethtool reporting (Andy Gospodarek) [726818]
- [netdrv] ixgbe: Use pci_vfs_assigned instead of ixgbe_vfs_are_assigned (Andy Gospodarek) [726818]
- [netdrv] ixgbe: Retain VLAN filtering in promiscuous + VT mode (Andy Gospodarek) [726818]
- [netdrv] ixgbe: Fix Tx Hang issue with lldpad on 82598EB (Andy Gospodarek) [726818]
- [netdrv] ixgbe: Set the SW prio_tc values at initialization to the HW setting (Andy Gospodarek) [726818]
- [pci] expose pcie_link_speed and pcix_bus_speed arrays (Andy Gospodarek) [726818]
- [pci] move enum pcie_link_width into pci.h (Andy Gospodarek) [726818]
- [pci] Add function to obtain minimum link width and speed (Andy Gospodarek) [726818]
- [netdrv] cnic: Update version to 2.5.18 (Tomas Henzl) [725064]
- [netdrv] cnic: Eliminate local copy of pfid (Tomas Henzl) [725064]
- [netdrv] cnic: Eliminate CNIC_PORT macro and port_mode in local struct (Tomas Henzl) [725064]
- [netdrv] cnic: Redefine BNX2X_HW_CID using existing bnx2x macros (Tomas Henzl) [725064]
- [netdrv] cnic: Use CHIP_NUM macros from bnx2x.h (Tomas Henzl) [725064]
- [netdrv] cnic: Convert mac address uses of 6 to ETH_ALEN (Tomas Henzl) [725064]
- [netdrv] cnic: Update version to 2.5.17 and copyright year (Tomas Henzl) [725064]
- [netdrv] cnic: Add missing error checking for RAMROD_CMD_ID_CLOSE (Tomas Henzl) [725064]
- [netdrv] cnic: Update TCP options setup for iSCSI (Tomas Henzl) [725064]
- [netdrv] cnic: Reset tcp_flags during cnic_cm_create() (Tomas Henzl) [725064]
- [netdrv] cnic: Simplify cnic_release() (Tomas Henzl) [725064]
- [netdrv] cnic: Simplify netdev events handling (Tomas Henzl) [725064]

* Thu Sep 19 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-24.el7]
- [Documentation] kvm: Add documentation on Hypercalls and features used for PV spinlock (Andrew Jones) [981581]
- [virt] kvm: Simplify kvm_for_each_vcpu with kvm_irq_delivery_to_apic (Andrew Jones) [981581]
- [virt] kvm: Add a hypercall to KVM hypervisor to support pv-ticketlocks (Andrew Jones) [981581]
- [virt] kvm: Paravirtual ticketlocks support for linux guests running on KVM hypervisor (Andrew Jones) [981581]
- [virt] kvm: Add configuration support to enable debug information for KVM Guests (Andrew Jones) [981581]
- [virt] kvm: Add KICK_CPU and PV_UNHALT definition to uapi (Andrew Jones) [981581]
- [virt] pvticketlock: Allow interrupts to be enabled while blocking (Andrew Jones) [981581]
- [virt] ticketlock: Add slowpath logic (Andrew Jones) [981581]
- [kernel] jump_label: Split jumplabel ratelimit (Andrew Jones) [981581]
- [virt] pvticketlock: Use callee-save for lock_spinning (Andrew Jones) [981581]
- [virt] pvticketlocks: Add xen_nopvspin parameter to disable xen pv ticketlocks (Andrew Jones) [981581]
- [virt] pvticketlock: Xen implementation for PV ticket locks (Andrew Jones) [981581]
- [virt] xen: Defer spinlock setup until boot CPU setup (Andrew Jones) [981581]
- [virt] ticketlock: Collapse a layer of functions (Andrew Jones) [981581]
- [virt] ticketlock: Don't inline _spin_unlock when using paravirt spinlocks (Andrew Jones) [981581]
- [virt] spinlock: Replace pv spinlocks with pv ticketlocks (Andrew Jones) [981581]
- [fs] proc/vmcore: support mmap() on /proc/vmcore (Nigel Croxon) [990298]
- [fs] proc/vmcore: calculate vmcore file size from buffer size and total size of vmcore objects (Nigel Croxon) [990298]
- [fs] proc/vmcore: allow user process to remap ELF note segment buffer (Nigel Croxon) [990298]
- [fs] proc/vmcore: allocate ELF note segment in the 2nd kernel vmalloc memory (Nigel Croxon) [990298]
- [mm] vmalloc: introduce remap_vmalloc_range_partial (Nigel Croxon) [990298]
- [mm] vmalloc: make find_vm_area check in range (Nigel Croxon) [990298]
- [fs] proc/vmcore: treat memory chunks referenced by PT_LOAD program header entries in page-size boundary in vmcore_list (Nigel Croxon) [990298]
- [fs] proc/vmcore: allocate buffer for ELF headers on page-size alignment (Nigel Croxon) [990298]
- [fs] proc/vmcore: clean up read_vmcore() (Nigel Croxon) [990298]
- [mm] add PAGE_ALIGNED() helper (Nigel Croxon) [990298]
- [fs] nfs Fix up nfs4_proc_lookup_mountpoint (Jeff Layton) [1007357]
- [fs] nfs: Don't check lock owner compatability unless file is locked (part 2) (Jeff Layton) [1007035]
- [fs] nfs: Don't check lock owner compatibility in writes unless file is locked (Jeff Layton) [1007035]
- [pci] Remove pcie_cap_has_devctl() (Myron Stowe) [1005229]
- [pci] Support PCIe Capability Slot registers only for ports with slots (Myron Stowe) [1005229]
- [pci] Remove PCIe Capability version checks (Myron Stowe) [1005229]
- [pci] Allow PCIe Capability link-related register access for switches (Myron Stowe) [1005229]
- [pci] Add offsets of PCIe capability registers (Myron Stowe) [1005229]
- [pci] Tidy bitmasks and spacing of PCIe capability definitions (Myron Stowe) [1005229]
- [pci] Remove obsolete comment reference to pci_pcie_cap2() (Myron Stowe) [1005229]
- [pci] Clarify PCI_EXP_TYPE_PCI_BRIDGE comment (Myron Stowe) [1005229]
- [pci] Rename PCIe capability definitions to follow convention (Myron Stowe) [1005229]
- [pci] Warn if unsafe MPS settings detected (Myron Stowe) [1005229]
- [pci] Fix MPS peer-to-peer DMA comment syntax (Myron Stowe) [1005229]
- [pci] Disable decoding for BAR sizing only when it was actually enabled (Myron Stowe) [1005229]
- [pci] Add comment about needing pci_msi_off() even when CONFIG_PCI_MSI=n (Myron Stowe) [1005229]
- [pci] Add pcibios_pm_ops for optional arch-specific hibernate functionality (Myron Stowe) [1005229]
- [pci] Don't restrict MPS for slots below Root Ports (Myron Stowe) [1005229]
- [pci] Simplify MPS test for Downstream Port (Myron Stowe) [1005229]
- [pci] Remove unnecessary check for pcie_get_mps() failure (Myron Stowe) [1005229]
- [pci] Simplify pcie_bus_configure_settings() interface (Myron Stowe) [1005229]
- [pci] Drop "PCI-E" prefix from Max Payload Size message (Myron Stowe) [1005229]
- [pci] Add pci_probe_reset_slot() and pci_probe_reset_bus() (Myron Stowe) [1005229]
- [pci] Remove aer_do_secondary_bus_reset() (Myron Stowe) [1005229]
- [pci] Tune secondary bus reset timing (Myron Stowe) [1005229]
- [pci] Wake-up devices before saving config space for reset (Myron Stowe) [1005229]
- [pci] Add pci_reset_slot() and pci_reset_bus() (Myron Stowe) [1005229]
- [pci] Split out pci_dev lock/unlock and save/restore (Myron Stowe) [1005229]
- [pci] Add slot reset option to pci_dev_reset() (Myron Stowe) [1005229]
- [pci] pciehp: Add reset_slot() method (Myron Stowe) [1005229]
- [pci] Add hotplug_slot_ops.reset_slot() (Myron Stowe) [1005229]
- [pci] quirks: Use pci_wait_for_pending_transaction() instead of for loop (Myron Stowe) [1005229]
- [netdrv] bnx2x: Use pci_wait_for_pending_transaction() instead of for loop (Myron Stowe) [1005229]
- [pci] quirks: Enable Bus Master during Function-Level Reset on Chelsio (Myron Stowe) [1005229]
- [pci] Add pci_wait_for_pending_transaction() (Myron Stowe) [1005229]
- [pci] Add pci_reset_bridge_secondary_bus() (Myron Stowe) [1005229]
- [pci] Align bridge I/O windows as required by downstream devices & bridges (Myron Stowe) [1005229]
- [pci] Fix types in pbus_size_io() (Myron Stowe) [1005229]
- [pci] Add comments for pbus_size_mem() parameters (Myron Stowe) [1005229]
- [pci] Enumerate subordinate buses, not devices, in pci_bus_get_depth() (Myron Stowe) [1005229]
- [pci] Fix comment typo for pci_add_cap_save_buffer() (Myron Stowe) [1005229]
- [pci] Return -ENOSYS for SR-IOV operations on non-SR-IOV devices (Myron Stowe) [1005229]
- [pci] Update NumVFs register when disabling SR-IOV (Myron Stowe) [1005229]
- [pci] mmconfig: Check earlier for MMCONFIG region at address zero (Myron Stowe) [1005229]
- [pci] Assign resources for hot-added host bridge more aggressively (Myron Stowe) [1005229]
- [pci] Move resource reallocation code to non-__init (Myron Stowe) [1005229]
- [pci] Delay enabling bridges until they're needed (Myron Stowe) [1005229]
- [pci] Assign resources on a per-bus basis (Myron Stowe) [1005229]
- [pci] Enable unassigned resource reallocation on per-bus basis (Myron Stowe) [1005229]
- [pci] Turn on reallocation for unassigned resources with host bridge offset (Myron Stowe) [1005229]
- [pci] Look for unassigned resources on per-bus basis (Myron Stowe) [1005229]
- [pci] Drop temporary variable in pci_assign_unassigned_resources() (Myron Stowe) [1005229]
- [pci] Claim ACS support for AMD southbridge devices (Myron Stowe) [1005229]
- [pci] Differentiate ACS controllable from enabled (Myron Stowe) [1005229]
- [pci] Check all ACS features for multifunction downstream ports (Myron Stowe) [1005229]
- [pci] Convert class code to use dev_groups (Myron Stowe) [1005229]
- [pci] mrst: Cleanup checkpatch.pl warnings (Myron Stowe) [1005229]
- [pci] Rename "PCI Express support" kconfig title (Myron Stowe) [1005229]
- [pci] Fix comment typo in iov.c (Myron Stowe) [1005229]
- [fs] sysfs: use file mode defines from stat.h (Myron Stowe) [1005229]
- [fs] sysfs: add more helper macro's for (bin_)attribute(_groups) (Myron Stowe) [1005229]
- [misc] device: add default groups to struct class (Myron Stowe) [1005229]
- [misc] device: Introduce device_create_groups (Myron Stowe) [1005229]
- [fs] sysfs: prevent warning when only using binary attributes (Myron Stowe) [1005229]
- [fs] sysfs: add support for binary attributes in groups (Myron Stowe) [1005229]
- [misc] device: add RW and RO attribute macros (Myron Stowe) [1005229]
- [misc] sysfs: add BIN_ATTR macro (Myron Stowe) [1005229]
- [misc] sysfs: add ATTRIBUTE_GROUPS() macro (Myron Stowe) [1005229]
- [misc] sysfs: add __ATTR_RW() macro (Myron Stowe) [1005229]

* Tue Sep 17 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-23.el7]
- [kernel] kexec: improve logging when crashkernel=auto can't be satisfied (Steve Best) [989576]

* Fri Sep 13 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-22.el7]
- [netdrv] bnx2: Convert dma_alloc_coherent(...__GFP_ZERO) to dma_zalloc_coherent (Neil Horman) [725061]
- [netdrv] bnx2: clean up unnecessary MSI/MSI-X capability find (Neil Horman) [725061]
- [netdrv] bnx2: Update version to 2.2.4 (Neil Horman) [725061]
- [netdrv] bnx2: Add pci shutdown handler (Neil Horman) [725061]
- [netdrv] bnx2: Use SIMPLE_DEV_PM_OPS (Neil Horman) [725061]
- [netdrv] bnx2: Refactor WoL setup into a separate function (Neil Horman) [725061]
- [netdrv] bnx2: Use kernel APIs for WoL and power state changes (Neil Horman) [725061]
- [netdrv] bnx2: Handle error condition in ->slot_reset() (Neil Horman) [725061]
- [netdrv] bnx2: use pdev->pm_cap instead of pci_find_capability(.., PCI_CAP_ID_PM) (Neil Horman) [725061]
- [netdrv] bnx2: Use module_pci_driver to register driver (Neil Horman) [725061]
- [netdrv] igb: Update version number (Stefan Assmann) [726817]
- [netdrv] igb: Implementation to report advertised/supported link on i354 devices (Stefan Assmann) [726817]
- [netdrv] igb: Get speed and duplex for 1G non_copper devices (Stefan Assmann) [726817]
- [netdrv] igb: Support to get 2_5G link status for appropriate media type (Stefan Assmann) [726817]
- [netdrv] igb: No PHPM support in i354 devices (Stefan Assmann) [726817]
- [netdrv] igb: M88E1543 PHY downshift implementation (Stefan Assmann) [726817]
- [netdrv] igb: New PHY_ID for i354 device (Stefan Assmann) [726817]
- [netdrv] igb: Implementation of 1-sec delay for i210 devices (Stefan Assmann) [726817]
- [netdrv] igb: Don't look for a PBA in the iNVM when flashless (Stefan Assmann) [726817]
- [netdrv] igb: Expose RSS indirection table for ethtool (Stefan Assmann) [726817]
- [netdrv] igb: Add macro for size of RETA indirection table (Stefan Assmann) [726817]
- [netdrv] igb: Fix get_fw_version function for all parts (Stefan Assmann) [726817]
- [netdrv] igb: Add device support for flashless SKU of i210 device (Stefan Assmann) [726817]
- [netdrv] igb: Refactor NVM read functions to accommodate devices with no flash (Stefan Assmann) [726817]
- [netdrv] igb: Refactor of init_nvm_params (Stefan Assmann) [726817]
- [netdrv] igb: Update MTU so that it is always at least a standard frame size (Stefan Assmann) [726817]
- [netdrv] igb: don't allow SR-IOV without MSI-X (Stefan Assmann) [726817]
- [netdrv] igb: Added rcu_lock to avoid race (Stefan Assmann) [726817]
- [netdrv] igb: Read register for latch_on without return value (Stefan Assmann) [726817]
- [netdrv] igb: Reset the link when EEE setting changed (Stefan Assmann) [726817]
- [netdrv] igb: fix vlan filtering in promisc mode when not in VT mode (Stefan Assmann) [726817]
- [netdrv] igb: relase -> release (Stefan Assmann) [726817]
- [netdrv] igb: Removed unused i2c function (Stefan Assmann) [726817]
- [netdrv] igb: Implementation of i210/i211 LED support (Stefan Assmann) [726817]
- [netdrv] igb: Fix possible panic caused by Rx traffic arrival while interface is down (Stefan Assmann) [726817]
- [netdrv] igb: Fix set_ethtool function to call update nvm for entire image (Stefan Assmann) [726817]
- [netdrv] igb: SerDes flow control setting (Stefan Assmann) [726817]
- [netdrv] igb: Support for SFP modules discovery (Stefan Assmann) [726817]
- [netdrv] igb: Add update to last_rx_timestamp in Rx rings (Stefan Assmann) [726817]
- [netdrv] igb: Changed LEDs blink mechanism to include designs using cathode (Stefan Assmann) [726817]
- [virt] kvm/mmu: avoid fast page fault fixing mmio page fault (Gleb Natapov) [981979]
- [virt] kvm/vmx: mark unusable segment as nonpresent (Gleb Natapov) [981979]
- [virt] kvm: get rid of $(addprefix ../../../virt/kvm/, ...) in Makefiles (Gleb Natapov) [981979]
- [virt] kvm: Fix RTC interrupt coalescing tracking (Gleb Natapov) [981979]
- [virt] kvm: Add a tracepoint write_tsc_offset (Gleb Natapov) [981979]
- [virt] kvm: Inform users of mmio generation wraparound (Gleb Natapov) [981979]
- [virt] kvm: document fast invalidate all mmio sptes (Gleb Natapov) [981979]
- [virt] kvm: document fast invalidate all pages (Gleb Natapov) [981979]
- [virt] kvm: document fast page fault (Gleb Natapov) [981979]
- [virt] kvm: document mmio page fault (Gleb Natapov) [981979]
- [virt] kvm: document write_flooding_count (Gleb Natapov) [981979]
- [virt] kvm: document clear_spte_count (Gleb Natapov) [981979]
- [virt] kvm: drop kvm_mmu_zap_mmio_sptes (Gleb Natapov) [981979]
- [virt] kvm: init kvm generation close to mmio wrap-around value (Gleb Natapov) [981979]
- [virt] kvm: add tracepoint for check_mmio_spte (Gleb Natapov) [981979]
- [virt] kvm: fast invalidate all mmio sptes (Gleb Natapov) [981979]
- [virt] kvm: make return value of mmio page fault handler more readable (Gleb Natapov) [981979]
- [virt] kvm: store generation-number into mmio spte (Gleb Natapov) [981979]
- [virt] kvm: retain more available bits on mmio spte (Gleb Natapov) [981979]
- [virt] kvm: update the documentation for reverse mapping of parent_pte (Gleb Natapov) [981979]
- [Documentation] kvm: fix section numbers (Gleb Natapov) [981979]
- [virt] kvm: handle idiv overflow at kvm_write_tsc (Gleb Natapov) [981979]
- [virt] kvm: reduce KVM_REQ_MMU_RELOAD when root page is zapped (Gleb Natapov) [981979]
- [virt] kvm: reclaim the zapped-obsolete page first (Gleb Natapov) [981979]
- [virt] kvm: collapse TLB flushes when zap all pages (Gleb Natapov) [981979]
- [virt] kvm: zap pages in batch (Gleb Natapov) [981979]
- [virt] kvm: do not reuse the obsolete page (Gleb Natapov) [981979]
- [virt] kvm: add tracepoint for kvm_mmu_invalidate_all_pages (Gleb Natapov) [981979]
- [virt] kvm: show mmu_valid_gen in shadow page related tracepoints (Gleb Natapov) [981979]
- [virt] kvm: use the fast way to invalidate all pages (Gleb Natapov) [981979]
- [virt] kvm: fast invalidate all pages (Gleb Natapov) [981979]
- [virt] kvm: drop unnecessary kvm_reload_remote_mmus (Gleb Natapov) [981979]
- [virt] kvm: drop calling kvm_mmu_zap_all in emulator_fix_hypercall (Gleb Natapov) [981979]
- [virt] kvm: exclude ioeventfd from counting kvm_io_range limit (Gleb Natapov) [981979]
- [virt] kvm: convert XADD to fastop (Gleb Natapov) [981979]
- [virt] kvm: drop unused old-style inline emulation (Gleb Natapov) [981979]
- [virt] kvm: convert DIV/IDIV to fastop (Gleb Natapov) [981979]
- [virt] kvm: convert single-operand MUL/IMUL to fastop (Gleb Natapov) [981979]
- [virt] kvm: Switch fastop src operand to RDX (Gleb Natapov) [981979]
- [virt] kvm: switch MUL/DIV to DstXacc (Gleb Natapov) [981979]
- [virt] kvm: decode extended accumulator explicity (Gleb Natapov) [981979]
- [virt] kvm: add support for writing back the source operand (Gleb Natapov) [981979]
- [virt] kvm: clenaup locking in mmu_free_roots() (Gleb Natapov) [981979]
- [virt] kvm: limit difference between kvmclock updates (Gleb Natapov) [981979]
- [virt] kvm: Remove support for reporting coalesced APIC IRQs (Gleb Natapov) [981979]
- [virt] kvm: Use kvm_mmu_sync_roots() in kvm_mmu_load() (Gleb Natapov) [981979]
- [virt] kvm: add missing misc_deregister() on error in kvm_init() (Gleb Natapov) [981979]

* Thu Sep 12 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-21.el7]
- [net] net_sched: fix a typo in htb_change_class() (Jesper Brouer) [998588]
- [net] tcp_probe: adapt tbuf size for recent changes (Daniel Borkmann) [1000470]
- [net] tcp_probe: allow more advanced ingress filtering by mark (Daniel Borkmann) [1000470]
- [net] tcp_probe: add IPv6 support (Daniel Borkmann) [1000470]
- [net] tcp_probe: kprobes: adapt jtcp_rcv_established signature (Daniel Borkmann) [1000470]
- [net] tcp_probe: also include rcv_wnd next to snd_wnd (Daniel Borkmann) [1000470]
- [lib] vsprintf: add IPv4/v6 generic p[Ii]S[pfs] format specifier (Daniel Borkmann) [1000470]
- [net] ipv6: fix potential use after free in tcp_v6_do_rcv (Jiri Benc) [1004165]
- [net] netlabel: use domain based selectors when address based selectors are not available (Paul Moore) [983949]

* Wed Sep 11 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-20.el7]
- [fs] gfs2: dirty inode correctly in gfs2_write_end (Benjamin Marzinski) [1004054]
- [netdrv] bnx2x: Convert dma_alloc_coherent(...__GFP_ZERO) to dma_zalloc_coherent (Michal Schmidt) [819849]
- [netdrv] bnx2x: clean up unnecessary MSI/MSI-X capability find (Michal Schmidt) [819849]
- [netdrv] bnx2x: Revising locking scheme for MAC configuration (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix VF stats sync (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix VF memory leak unload (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix functionality of configuring vlan list (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix move FP memory deallocations (Michal Schmidt) [819849]
- [netdrv] bnx2x: vf mark stats started (Michal Schmidt) [819849]
- [netdrv] bnx2x: set VF DMAE when first function has 0 supported VFs (Michal Schmidt) [819849]
- [netdrv] bnx2x: Protect against VFs' ndos when SR-IOV is disabled (Michal Schmidt) [819849]
- [netdrv] bnx2x: prevent VF benign attentions (Michal Schmidt) [819849]
- [netdrv] bnx2x: Consider DCBX remote error (Michal Schmidt) [819849]
- [netdrv] bnx2x: Change DCB context handling (Michal Schmidt) [819849]
- [netdrv] bnx2x: dropless flow control not always functional (Michal Schmidt) [819849]
- [netdrv] bnx2x: prevent crash in shutdown flow with CNIC (Michal Schmidt) [819849]
- [netdrv] bnx2x: fix PTE write access error (Michal Schmidt) [819849]
- [netdrv] bnx2x: fix memory leak in VF (Michal Schmidt) [819849]
- [netdrv] bnx2x: update fairness parameters following DCB negotiation (Michal Schmidt) [819849]
- [netdrv] bnx2x: protect different statistics flows (Michal Schmidt) [819849]
- [netdrv] bnx2x: fix tunneling CSUM calculation (Michal Schmidt) [819849]
- [netdrv] bnx2x: fill in sane dump flag information (Michal Schmidt) [819849]
- [netdrv] bnx2x: fix dump flag handling (Michal Schmidt) [819849]
- [netdrv] bnx2x: remove zeroing of dump data buffer (Michal Schmidt) [819849]
- [netdrv] bnx2x: Remove sparse and coccinelle warnings (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix compilation with no IOV support (Michal Schmidt) [819849]
- [netdrv] bnx2x: Fix 20G KR2 support claims (Michal Schmidt) [819849]
- [netdrv] bnx2x: improve VF timings (Michal Schmidt) [819849]
- [netdrv] bnx2x: VF ndo sanity (Michal Schmidt) [819849]
- [netdrv] bnx2x: Improve PF behaviour toward VF (Michal Schmidt) [819849]
- [netdrv] bnx2x: remove redundant D0 power state set (Michal Schmidt) [819849]
- [netdrv] bnx2x: replace mechanism to check for next available packet (Michal Schmidt) [819849]
- [netdrv] bnx2x: add support for busy-poll (Michal Schmidt) [819849]
- [netdrv] bnx2x: fix a power state test (Michal Schmidt) [819849]
- [netdrv] bnx2x: semi-Semantic changes (Michal Schmidt) [819849]
- [netdrv] bnx2x: Revise prints (Michal Schmidt) [819849]
- [netdrv] bnx2x: Semantic removal and beautification (Michal Schmidt) [819849]
- [netdrv] bnx2x: Revise comments and alignment (Michal Schmidt) [819849]
- [netdrv] bnx2x: Semantic change of empty lines (Michal Schmidt) [819849]
- [netdrv] bnx2x: use XPS if possible for bnx2x_select_queue instead of pure hash (Michal Schmidt) [819849]
- [netdrv] bnx2x: Change to D3hot only on removal (Michal Schmidt) [819849]
- [netdrv] bnx2x: Implement PCI shutdown (Michal Schmidt) [819849]
- [netdrv] bnx2x: Count number of possible FCoE interfaces (Michal Schmidt) [819849]
- [netdrv] bnx2x: Ack unknown VF messages (Michal Schmidt) [819849]
- [netdrv] bnx2x: Add and correct PCI link speed prints (Michal Schmidt) [819849]
- [netdrv] bnx2x: Zero VFs starting MACs (Michal Schmidt) [819849]
- [netdrv] bnx2x: Enable `set_phys_id' for all functions (Michal Schmidt) [819849]
- [netdrv] bnx2x: Link-flap avoidance in switch dependent mode (Michal Schmidt) [819849]
- [netdrv] bnx2x: Add Private Flags Support (Michal Schmidt) [819849]
- [netdrv] bnx2x: dont reload on GRO change (Michal Schmidt) [819849]

* Tue Sep 10 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-19.el7]
- [crypto] nx: fix SHA-2 for chunks bigger than block size (Steve Best) [999606]
- [crypto] nx: fix GCM for zero length messages (Steve Best) [999606]
- [crypto] nx: fix XCBC for zero length messages (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-CCM (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-XCBC (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-GCM (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-CTR (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-CBC (Steve Best) [999606]
- [crypto] nx: fix limits to sg lists for AES-ECB (Steve Best) [999606]
- [crypto] nx: add offset to nx_build_sg_lists() (Steve Best) [999606]
- [virt] virtio_console: prevent use-after-free of port name in port unplug (Amit Shah) [990419]
- [virt] virtio_console: fix locking around send_sigio_to_port() (Amit Shah) [986968]
- [virt] virtio_console: add locking in port unplug path (Amit Shah) [990419]
- [virt] virtio_console: add locks around buffer removal in port unplug path (Amit Shah) [990419]
- [virt] virtio_console: return -ENODEV on all read operations after unplug (Amit Shah) [975716]
- [virt] virtio_console: fix raising SIGIO after port unplug (Amit Shah) [986968]
- [virt] virtio_console: clean up port data immediately at time of unplug (Amit Shah) [990419]
- [virt] virtio_console: fix race in port_fops_open() and port unplug (Amit Shah) [990419]
- [virt] virtio_console: fix race with port unplug and open/close (Amit Shah) [990419]
- [virt] virtio_console: Add pipe_lock/unlock for splice_write (Amit Shah) [987722]
- [virt] virtio_console: Quit from splice_write if pipe->nrbufs is 0 (Amit Shah) [987722]
- [scsi] Generate uevents on certain unit attention codes (Ewan Milne) [740795]
- [virt] kvm: update masterclock when kvmclock_offset is calculated (Marcelo Tosatti) [978425]
- [acpi] pci_root: Fix _OSC ordering to allow PCIe hotplug use when available (Neil Horman) [990078]

* Thu Sep 05 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-18.el7]
- [net] ipv4: make snmp_mib_free static inline (Amerigo Wang) [970585]
- [net] vxlan: include net/ip6_checksum.h for csum_ipv6_magic() (Amerigo Wang) [970585]
- [net] vxlan: fix flowi6_proto value (Amerigo Wang) [970585]
- [net] udp: unify skb_udp_tunnel_segment() and skb_udp6_tunnel_segment() (Amerigo Wang) [970585]
- [net] ipv6: Add generic UDP Tunnel segmentation (Amerigo Wang) [970585]
- [net] vxlan: add ipv6 proxy support (Amerigo Wang) [970585]
- [net] ipv6: move in6_dev_finish_destroy() into core kernel (Amerigo Wang) [970585]
- [net] ipv6: add include file to suppress sparse warnings (Amerigo Wang) [970585]
- [net] vxlan: add ipv6 route short circuit support (Amerigo Wang) [970585]
- [net] vxlan: add ipv6 support (Amerigo Wang) [970585]
- [net] ipv6: do not call ndisc_send_rs() with write lock (Amerigo Wang) [970585]
- [net] ipv6: export in6addr_loopback to modules (Amerigo Wang) [970585]
- [net] ipv6: export a stub for IPv6 symbols used by vxlan (Amerigo Wang) [970585]
- [net] ipv6: Remove extern function prototypes (Amerigo Wang) [970585]
- [net] ipv6: always hold idev->lock before mca_lock (Amerigo Wang) [970585]
- [net] ipv6: move ip6_local_out into core kernel (Amerigo Wang) [970585]
- [net] ipv6: move ip6_dst_hoplimit() into core kernel (Amerigo Wang) [970585]
- [net] udp: move GSO functions to udp_offload (Amerigo Wang) [970585]
- [net] tcp: move GRO/GSO functions to tcp_offload (Amerigo Wang) [970585]
- [net] tcp: use tcp_skb_mss helper in tcp_tso_segment (Amerigo Wang) [970585]
- [scsi] csgb4i: convert skb->transport_header into skb_transport_header(skb) (Amerigo Wang) [970585]
- [net] pass correct parameter to skb_headers_offset_update() (Amerigo Wang) [970585]
- [netdrv] cxgb3: Correct comparisons and calculations using skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [net] clean up skb headers code (Amerigo Wang) [970585]
- [net] Fix build warnings after mac_header and transport_header became __u16 (Amerigo Wang) [970585]
- [net] netfilter: Correct calculation using skb->tail and skb-network_header (Amerigo Wang) [970585]
- [net] Correct assignment of skb->network_header to skb->tail (Amerigo Wang) [970585]
- [net] sctp: Correct access to skb->{network, transport}_header (Amerigo Wang) [970585]
- [net] ipv4: Correct comparisons and calculations using skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [net] ipv6: Correct comparisons and calculations using skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [net] Correct comparisons and calculations using skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [netdrv] cxgb3: Correct comparisons and calculations using skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [netdrv] isdn: Correct comparison of skb->tail and skb-transport_header (Amerigo Wang) [970585]
- [net] Copy inner_protocol in copy_skb_header() (Amerigo Wang) [970585]
- [net] mpls: Add limited GSO support (Amerigo Wang) [970585]
- [net] Use 16bits for *_headers fields of struct skbuff (Amerigo Wang) [970585]

* Wed Sep 04 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-17.el7]
- [fs] lockd: Don't call utsname()->nodename from nlmclnt_setlockargs (Jan Stancek) [999289]
- [scsi] ipr: Add sereral new CCIN definitions for new adapters support (Steve Best) [1002200]
- [virt] x86/xen: Sync the CMOS RTC as well as the Xen wallclock (Radim Krcmar) [1003683]
- [virt] x86/xen: Sync the wallclock when the system time is set (Radim Krcmar) [1003683]
- [virt] x86: Increase precision of x86_platform.get/set_wallclock() (Radim Krcmar) [1003683]
- [powerpc] Don't Oops when accessing /proc/powerpc/lparcfg without hypervisor (Steve Best) [1002206]
- [virt] xen/smp: initialize IPI vectors before marking CPU online (Radim Krcmar) [1003683]
- [virt] xen/events: mask events when changing their VCPU binding (Radim Krcmar) [1003683]
- [virt] xen/events: initialize local per-cpu mask for all possible events (Radim Krcmar) [1003683]
- [virt] x86/xen: do not identity map UNUSABLE regions in the machine E820 (Radim Krcmar) [1003683]
- [virt] xen/evtchn: avoid a deadlock when unbinding an event channel (Radim Krcmar) [1003683]
- [virt] xenbus: frontend resume cleanup (Radim Krcmar) [1003683]
- [virt] xen-netfront: pull on receive skb may need to happen earlier (Radim Krcmar) [1003683]
- [virt] xen: Use more current logging styles (Radim Krcmar) [1003683]
- [virt] xen/time: remove blocked time accounting from xen "clockchip" (Radim Krcmar) [1003683]
- [virt] xen: Convert printks to pr_<level> (Radim Krcmar) [1003683]
- [virt] xen: ifdef CONFIG_HIBERNATE_CALLBACKS xen_*_suspend (Radim Krcmar) [1003683]
- [virt] xen-blkfront: set blk_queue_max_hw_sectors correctly (Radim Krcmar) [1003683]
- [virt] xen/io: new macro to detect whether there are too many requests on the ring (Radim Krcmar) [1003683]
- [virt] xen-netfront: use skb_partial_csum_set() to simplify the codes (Radim Krcmar) [1003683]
- [virt] xen/time: Free onlined per-cpu data structure if we want to online it again (Radim Krcmar) [1003683]
- [virt] xen/time: Check that the per_cpu data structure has data before freeing (Radim Krcmar) [1003683]
- [virt] xen/time: Don't leak interrupt name when offlining (Radim Krcmar) [1003683]
- [virt] xen/time: Encapsulate the struct clock_event_device in another structure (Radim Krcmar) [1003683]
- [virt] xen/spinlock: Don't leak interrupt name when offlining (Radim Krcmar) [1003683]
- [virt] xen/smp: Don't leak interrupt name when offlining (Radim Krcmar) [1003683]
- [virt] xen/smp: Set the per-cpu IRQ number to a valid default (Radim Krcmar) [1003683]
- [virt] xen/smp: Introduce a common structure to contain the IRQ name and interrupt line (Radim Krcmar) [1003683]
- [virt] xen/smp: Coalesce the free_irq calls in one function (Radim Krcmar) [1003683]
- [virt] xen-blkback: Use physical sector size for setup (Radim Krcmar) [1003683]
- [virt] xen-blkfront: Introduce a 'max' module parameter to alter the amount of indirect segments (Radim Krcmar) [1003683]
- [virt] xen/netif: document feature-split-event-channels (Radim Krcmar) [1003683]
- [virt] xen-netfront: split event channels support for Xen frontend driver (Radim Krcmar) [1003683]
- [virt] xen-netfront: avoid leaking resources when setup_netfront fails (Radim Krcmar) [1003683]
- [virt] xen-blkfront: use a different scatterlist for each request (Radim Krcmar) [1003683]
- [virt] xen-block: implement indirect descriptors (Radim Krcmar) [1003683]
- [acpi] Try harder to resolve _ADR collisions for bridges (Myron Stowe) [1003183]
- [cpufreq] rename ignore_nice as ignore_nice_load (Myron Stowe) [1003183]
- [acpi] processor: move try_offline_node() after acpi_unmap_lsapic() (Myron Stowe) [1003183]
- [acpi] Drop physical_node_id_bitmap from struct acpi_device (Myron Stowe) [1003183]
- [acpi] pm: Walk physical_node_list under physical_node_lock (Myron Stowe) [1003183]
- [acpi] video: improve quirk check in acpi_video_bqc_quirk() (Myron Stowe) [1003183]
- [kernel] freezer: set PF_SUSPEND_TASK flag on tasks that call freeze_processes (Myron Stowe) [1003183]
- [acpi] battery: Fix parsing _BIX return value (Myron Stowe) [1003183]
- [cpufreq] Fix cpufreq driver module refcount balance after suspend/resume (Myron Stowe) [1003183]
- [cpufreq] intel_pstate: Change to scale off of max P-state (Myron Stowe) [1003183]
- [acpi] video: ignore BIOS initial backlight value for Fujitsu E753 (Myron Stowe) [1003183]
- [pnp] acpi: avoid garbage in resource name (Myron Stowe) [1003183]
- [power] sleep: Fix comment typo in pm_wakeup.h (Myron Stowe) [1003183]
- [power] sleep: avoid 'autosleep' in shutdown progress (Myron Stowe) [1003183]
- [acpi] scan: Always call acpi_bus_scan() for bus check notifications (Myron Stowe) [1003183]
- [acpi] scan: Do not try to attach scan handlers to devices having them (Myron Stowe) [1003183]

* Tue Sep 03 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-16.el7]
- [powerpc] Avoid link stack corruption for MMU on exceptions (Steve Best) [999556]
- [virt] net/hyperv: Fix the NETIF_F_SG flag setting in netvsc (Jason Wang) [984810]
- [pci] Retry allocation of only the resource type that failed (Myron Stowe) [1001217]
- [pci] pciehp: Convert pciehp to be builtin only, not modular (Myron Stowe) [1001217]
- [pci] hotplug: Convert to be builtin only, not modular (Myron Stowe) [1001217]
- [pci] pciehp: Fix null pointer deref when hot-removing SR-IOV device (Myron Stowe) [1001217]

* Fri Aug 30 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-15.el7]
- [drm] qxl: backport updates from v3.11-rc1 (Dave Airlie) [979176]
- [drm] add hotspot support for cursors (Dave Airlie) [983312]
- [virt] x86: Correctly detect hypervisor (Jason Wang) [985743]
- [virt] kvm: Switch to use hypervisor_cpuid_base() (Jason Wang) [985743]
- [virt] xen: Switch to use hypervisor_cpuid_base() (Jason Wang) [985743]
- [virt] x86: Introduce hypervisor_cpuid_base() (Jason Wang) [985743]
- [net] sunrpc: prepare NFS for 2038 (Harshula Jayasuriya) [847926]
- [netdrv] macvtap: Ignore tap features when VNET_HDR is off (Vlad Yasevich) [1001053]
- [netdrv] macvtap: Correctly set tap features when IFF_VNET_HDR is disabled (Vlad Yasevich) [1001053]
- [netdrv] macvtap: simplify usage of tap_features (Vlad Yasevich) [1001053]

* Thu Aug 29 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-14.el7]
- [net] openvswitch: optimize flow compare and mask functions (Thomas Graf) [1002051]
- [net] openvswitch: Rename key_len to key_end (Thomas Graf) [1002051]
- [net] openvswitch: Add SCTP support (Thomas Graf) [1002051]
- [net] ipv6: Add NEXTHDR_SCTP to ipv6.h (Thomas Graf) [1002051]
- [net] sctp: Refactor SCTP skb checksum computation (Thomas Graf) [1002051]
- [net] sctp: prevent checksum.h from double inclusion (Thomas Graf) [1002051]
- [net] openvswitch: Mega flow implementation (Thomas Graf) [1002051]
- [net] openvswitch: Fix argument descriptions in vport.c (Thomas Graf) [1002051]
- [net] openvswitch: link upper device for port devices (Thomas Graf) [1002051]
- [net] openvswitch: Use non rcu hlist_del() flow table entry (Thomas Graf) [1002051]
- [net] openvswitch: Use RCU lock for dp dump operation (Thomas Graf) [1002051]
- [net] openvswitch: Use RCU lock for flow dump operation (Thomas Graf) [1002051]
- [net] ipv6: prevent race between address creation and removal (Jiri Benc) [991392]
- [net] ipv6: move peer_addr init into ipv6_add_addr() (Jiri Benc) [991392]
- [net] ipv6: use ipv6_addr_scope() helper (Jiri Benc) [991392]
- [net] ipv6: add support of peer address (Jiri Benc) [991392]
- [net] rtm_to_ifaddr: free ifa if ifa_cacheinfo processing fails (Daniel Borkmann) [992908]
- [net] net_sched: restore "linklayer atm" handling (Jesper Brouer) [998588]
- [net] net_sched: psched_ratecfg_precompute() improvements (Jesper Brouer) [998588]
- [net] ip_tunnel: Do not use inner ip-header-id for tunnel ip-header-id (Amerigo Wang) [989522]
- [net] openvswitch: Add vxlan tunneling support (Amerigo Wang) [989522]
- [net] vxlan: Add tx-vlan offload support (Amerigo Wang) [989522]
- [net] vxlan: Improve vxlan headroom calculation (Amerigo Wang) [989522]
- [net] vxlan: Factor out vxlan send api (Amerigo Wang) [989522]
- [net] vxlan: Extend vxlan handlers for openvswitch (Amerigo Wang) [989522]
- [net] vxlan: Add vxlan recv demux (Amerigo Wang) [989522]
- [net] vxlan: Restructure vxlan receive (Amerigo Wang) [989522]
- [net] vxlan: Restructure vxlan socket apis (Amerigo Wang) [989522]
- [net] openvswitch: Reset tunnel key between input and output (Amerigo Wang) [989522]
- [net] openvswitch: Use correct type while allocating flex array (Amerigo Wang) [989522]
- [net] openvswitch: Fix bad merge resolution (Amerigo Wang) [989522]
- [net] rtnetlink: Fix inverted check in ndo_dflt_fdb_del() (Amerigo Wang) [989522]
- [net] rtnetlink: allow using zero MAC address in rtnl_fdb_{add, del} (Amerigo Wang) [989522]
- [net] vxlan: fix a soft lockup in vxlan module removal (Amerigo Wang) [989522]
- [net] vxlan: fix a regression of igmp join (Amerigo Wang) [989522]
- [net] vxlan: fix rcu related warning (Amerigo Wang) [989522]
- [net] vxlan: fdb: replace an existing entry (Amerigo Wang) [989522]
- [net] vxlan: fix igmp races (Amerigo Wang) [989522]
- [net] vxlan: unregister on namespace exit (Amerigo Wang) [989522]
- [net] vxlan: add necessary locking on device removal (Amerigo Wang) [989522]
- [net] vxlan: Fix kernel crash on rmmod (Amerigo Wang) [989522]
- [net] vxlan: fix function name spelling (Amerigo Wang) [989522]
- [net] vxlan: fdb: allow specifying multiple destinations for zero MAC (Amerigo Wang) [989522]
- [net] vxlan: allow removal of single destination from fdb entry (Amerigo Wang) [989522]
- [net] vxlan: introduce vxlan_fdb_parse (Amerigo Wang) [989522]
- [net] vxlan: introduce vxlan_fdb_find_rdst (Amerigo Wang) [989522]
- [net] vxlan: add implicit fdb entry for default destination (Amerigo Wang) [989522]
- [net] vxlan: Fix sparse warnings (Amerigo Wang) [989522]
- [net] vxlan: cosmetic cleanup's (Amerigo Wang) [989522]
- [net] vxlan: Use initializer for dummy structures (Amerigo Wang) [989522]
- [net] vxlan: port module param should be ushort (Amerigo Wang) [989522]
- [net] vxlan: convert remotes list to list_rcu (Amerigo Wang) [989522]
- [net] vxlan: make vxlan_xmit_one void (Amerigo Wang) [989522]
- [net] vxlan: move cleanup to uninit (Amerigo Wang) [989522]
- [net] vxlan: fix race caused by dropping rtnl_unlock (Amerigo Wang) [989522]
- [net] vxlan: send notification when MAC migrates (Amerigo Wang) [989522]
- [net] vxlan: move IGMP join/leave to work queue (Amerigo Wang) [989522]
- [net] vxlan: fix crash from work pending on module removal (Amerigo Wang) [989522]
- [net] vxlan: fix out of order operation on module removal (Amerigo Wang) [989522]
- [net] vxlan: defer vxlan init as late as possible (Amerigo Wang) [989522]
- [net] vxlan: use unsigned int instead of unsigned (Amerigo Wang) [989522]
- [net] vxlan: remove the unused rcu head from struct vxlan_rdst (Amerigo Wang) [989522]
- [net] vxlan: listen on multiple ports (Amerigo Wang) [989522]
- [rhel] Kconfig: enable CONFIG_OPENVSWITCH_GRE (Amerigo Wang) [992917]
- [net] ip_tunnel: embed hash list head (Amerigo Wang) [992917]
- [net] sit: fix tunnel update via netlink (Amerigo Wang) [992917]
- [net] ipv6: only apply anti-spoofing checks to not-pointopoint tunnels (Amerigo Wang) [992917]
- [net] gre: Fix MTU sizing check for gretap tunnels (Amerigo Wang) [992917]
- [net] ip_tunnels: Use skb-len to PMTU check (Amerigo Wang) [992917]
- [net] gso: Update tunnel segmentation to support Tx checksum offload (Amerigo Wang) [992917]
- [net] gre: move GSO functions to gre_offload (Amerigo Wang) [992917]
- [net] gre: fix a regression in ioctl (Amerigo Wang) [992917]
- [net] sit: add support of x-netns (Amerigo Wang) [992917]
- [net] dev: introduce skb_scrub_packet() (Amerigo Wang) [992917]
- [net] dev: remove duplicate 'skb->dev = dev' in dev_forward_skb() (Amerigo Wang) [992917]
- [net] sit: fix an oops when IFLA_IPTUN_PROTO is not set (Amerigo Wang) [992917]
- [net] sit: fix 4in4 + IPsec scenario (Amerigo Wang) [992917]
- [net] openvswitch: Add Kconfig dependency on GRE-DEMUX (Amerigo Wang) [992917]
- [net] ip_tunnel: Protect tunnel functions with CONFIG_INET guard (Amerigo Wang) [992917]
- [net] openvswitch: Use correct config guard (Amerigo Wang) [992917]
- [net] openvswitch: Add gre tunnel support (Amerigo Wang) [992917]
- [net] openvswitch: Optimize flow key match for non tunnel flows (Amerigo Wang) [992917]
- [net] openvswitch: Expand action buffer size (Amerigo Wang) [992917]
- [net] openvswitch: Add tunneling interface (Amerigo Wang) [992917]
- [net] openvswitch: Copy individual actions (Amerigo Wang) [992917]
- [net] ip_tunnel: Add dont fragment flag (Amerigo Wang) [992917]
- [net] ip_tunnel: push generic protocol handling to ip_tunnel module (Amerigo Wang) [992917]
- [net] ip_tunnel: extend iptunnel_xmit() (Amerigo Wang) [992917]
- [net] gre: export gre_handle_offloads() function (Amerigo Wang) [992917]
- [net] gre: export gre_build_header() function (Amerigo Wang) [992917]
- [net] gre: Allow multiple protocol listener for gre protocol (Amerigo Wang) [992917]
- [net] gre: Simplify gre protocol registration locking (Amerigo Wang) [992917]
- [net] openvswitch: make skb->csum consistent with rest of networking stack (Amerigo Wang) [992917]
- [net] openvswitch: Simplify interface ovs_flow_metadata_from_nlattrs() (Amerigo Wang) [992917]
- [net] openvswitch: Fix misspellings in comments and docs (Amerigo Wang) [992917]
- [net] openvswitch: Unify vport error stats handling (Amerigo Wang) [992917]
- [net] openvswitch: fix variable names in comment (Amerigo Wang) [992917]
- [net] openvswitch: Immediately exit on error in ovs_vport_cmd_set() (Amerigo Wang) [992917]
- [net] openvswitch: Remove unused get_config vport op (Amerigo Wang) [992917]
- [net] iptunnel: specify protocol outside IP header (Amerigo Wang) [992917]
- [net] sit: add IPv4 over IPv4 support (Amerigo Wang) [992917]
- [net] export physical port id via sysfs (Jiri Pirko) [991026]
- [net] rtnl: export physical port id via RT netlink (Jiri Pirko) [991026]
- [net] add ndo to get id of physical port of the device (Jiri Pirko) [991026]
- [net] busy_poll: revert unsupported bits from creation of BUSY_POLL socket option (Neil Horman) [958330]
- [net] busy_poll: rename busy poll socket op and globals (Neil Horman) [958330]
- [net] busy_poll: rename ll methods to busy-poll (Neil Horman) [958330]
- [net] busy_poll: rename include/net/ll_poll.h to include/net/busy_poll.h (Neil Horman) [958330]
- [net] busy_poll: change busy poll time accounting (Neil Horman) [958330]
- [net] busy_poll: rename low latency sockets functions to busy poll (Neil Horman) [958330]
- [net] busy_poll: lls fix build with allnoconfig (Neil Horman) [958330]
- [net] busy_poll: convert lls to use time_in_range() (Neil Horman) [958330]
- [net] busy_poll: avoid calling sched_clock when LLS is off (Neil Horman) [958330]
- [net] busy_poll: fix LLS debug_smp_processor_id() warning (Neil Horman) [958330]
- [net] busy_poll: poll/select low latency socket support (Neil Horman) [958330]
- [net] busy_poll: add socket option for low latency polling (Neil Horman) [958330]
- [net] busy_poll: remove NET_LL_RX_POLL config menu (Neil Horman) [958330]
- [net] busy_poll: convert low latency sockets to sched_clock() (Neil Horman) [958330]
- [net] busy_poll: change sysctl_net_ll_poll into an unsigned int (Neil Horman) [958330]
- [netdrv] ixgbe: add extra stats for ndo_ll_poll (Neil Horman) [958330]
- [netdrv] ixgbe: add support for ndo_ll_poll (Neil Horman) [958330]
- [net] tcp: add low latency socket poll support (Neil Horman) [958330]
- [net] udp: add low latency socket poll support (Neil Horman) [958330]
- [net] busy_poll: add low latency socket poll (Neil Horman) [958330]
- [net] add napi_id and hash (Neil Horman) [958330]

* Wed Aug 28 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-13.el7]
- [powerpc] pseries: Drop "select HOTPLUG" (Myron Stowe) [999178]
- [misc] Finally eradicate CONFIG_HOTPLUG (Myron Stowe) [999178]
- [vfio] vfio-pci: Avoid deadlock on remove (Alex Williamson) [912293]
- [vfio] Ignore sprurious notifies (Alex Williamson) [912293]
- [vfio] Don't overreact to DEL_DEVICE (Alex Williamson) [912293]
- [s390] qeth: Fix crash on initial MTU size change (Hendrik Brueckner) [997607]
- [s390] qeth: change default standard blkt settings for OSA (Hendrik Brueckner) [997635]
- [s390] dasd: fix hanging devices after path events (Hendrik Brueckner) [996178]
- [s390] zcrypt: Alias for new zcrypt device driver base module (Hendrik Brueckner) [996731]
- [s390] zfcp: status read buffers on first adapter open with link down (Hendrik Brueckner) [976636]
- [s390] zfcp: fix adapter (re)open recovery while link to SAN is down (Hendrik Brueckner) [889079]
- [netdrv] be2net: Fix to avoid hardware workaround when not needed (Ivan Vecera) [982900]
- [fs] gfs2: Take glock reference in examine_bucket() (Steven Whitehouse) [999897]
- [fs] gfs2: Check for glock already held in gfs2_getxattr (Steven Whitehouse) [997604]
- [crypto] nx: fix nx-aes-gcm verification (Steve Best) [997057]
- [s390] zfcp: remove access control tables interface (Hendrik Brueckner) [994519]
- [s390] zfcp: cfdc fops add owner (Hendrik Brueckner) [994519]
- [scsi] fcoe: cleanup return codes from fcoe_rcv (Neil Horman) [984876]
- [scsi] fcoe: make sure fcoe frames are unshared prior to manipulating them (Neil Horman) [984876]
- [scsi] fcoe: ensure that skb placed on the fip_recv_list are unshared (Neil Horman) [984876]
- [mm] zswap: add documentation (Steve Best) [731499]
- [mm] zswap: add to mm (Steve Best) [731499]
- [mm] zbud: add to mm (Steve Best) [731499]
- [misc] MAINTAINERS: add zswap and zbud maintainer (Steve Best) [731499]
- [fs] debugfs: add get/set for atomic types (Steve Best) [731499]

* Mon Aug 26 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-12.el7]
- [acpi] memhotplug: Fix a stale pointer in error path (Lenny Szubowicz) [995322]
- [powerpc] Add second POWER8 PVR entry (Steve Best) [995355]
- [acpi] power: add missing newline to debug messages (Myron Stowe) [998633]
- [tools] cpupower: Add Haswell family 0x45 specific idle monitor to show PC8, 9, 10 states (Myron Stowe) [998633]
- [tools] cpupower: Haswell also supports the C-states introduced with SandyBridge (Myron Stowe) [998633]
- [tools] cpupower: Introduce idle-set subcommand and C-state enabling/disabling (Myron Stowe) [998633]
- [tools] cpupower: Implement disabling of cstate interface (Myron Stowe) [998633]
- [tools] cpupower: Make idlestate usage unsigned (Myron Stowe) [998633]
- [acpi] fan: Initialize acpi_state variable (Myron Stowe) [998633]
- [acpi] scan: remove unused LIST_HEAD(acpi_device_list) (Myron Stowe) [998633]
- [acpi] dock: Actually define acpi_dock_init() as void (Myron Stowe) [998633]
- [acpi] pm: Fix corner case in acpi_bus_update_power() (Myron Stowe) [998633]
- [cpufreq] Fix serialization of frequency transitions (Myron Stowe) [998633]
- [cpufreq] Fix cpufreq regression after suspend/resume (Myron Stowe) [991615]
- [acpi] pm: Fix possible NULL pointer deref in acpi_pm_device_sleep_state() (Myron Stowe) [991615]
- [kernel] power: Warn about system time after resume with pm_trace (Myron Stowe) [991615]
- [cpufreq] don't leave stale policy pointer in cdbs->cur_policy (Myron Stowe) [991615]
- [cpufreq] acpi-cpufreq: Add new sysfs attribute freqdomain_cpus (Myron Stowe) [991615]
- [cpufreq] make sure frequency transitions are serialized (Myron Stowe) [991615]
- [acpi] implement acpi_os_get_timer() according the spec (Myron Stowe) [991615]
- [acpi] ec: Add HP Folio 13 to ec_dmi_table in order to skip DSDT scan (Myron Stowe) [991615]
- [acpi] Add CMOS RTC Operation Region handler support (Myron Stowe) [991615]
- [acpi] processor: Drop unused variable from processor_perflib.c (Myron Stowe) [991615]
- [cpufreq] powernow-k8: call CPUFREQ_POSTCHANGE notfier in error cases (Myron Stowe) [991615]
- [cpufreq] pcc: call CPUFREQ_POSTCHANGE notfier in error cases (Myron Stowe) [991615]
- [cpufreq] acpi-cpufreq: call CPUFREQ_POSTCHANGE notfier in error cases (Myron Stowe) [991615]
- [Documentation] power: Add pm_qos and dev_pm_qos to events-power.txt (Myron Stowe) [991615]
- [base] power/qos: Add dev_pm_qos_request tracepoints (Myron Stowe) [991615]
- [kernel] power/qos: Add pm_qos_request tracepoints (Myron Stowe) [991615]
- [kernel] power/qos: Add pm_qos_update_target/flags tracepoints (Myron Stowe) [991615]
- [acpi] processor: Remove unused macros in processor_driver.c (Myron Stowe) [991615]
- [Documentation] power: Update Documentation/power/pm_qos_interface.txt (Myron Stowe) [991615]
- [Documentation] cpu-hotplug: Rephrase the outdated description for MADT entries (Myron Stowe) [991615]
- [cpufreq] make __cpufreq_notify_transition() static (Myron Stowe) [991615]
- [cpufreq] Fix minor formatting issues (Myron Stowe) [991615]
- [cpufreq] Fix governor start/stop race condition (Myron Stowe) [991615]
- [kernel] power: Print last wakeup source on failed wakeup_count write (Myron Stowe) [991615]
- [kernel] power/qos: correct the valid range of pm_qos_class (Myron Stowe) [991615]
- [Documentation] video: update video_extension.txt for backlight control (Myron Stowe) [991615]
- [Documentation] video: move video_extension.txt to Documentation/acpi (Myron Stowe) [991615]
- [Documentation] video: add description for brightness_switch_enabled (Myron Stowe) [991615]
- [Documentation] Add ACPI namespace documentation (Myron Stowe) [991615]
- [Documentation] Add sysfs ABI documentation (Myron Stowe) [991615]
- [Documentation] MAINTAINERS: include Documentation/acpi (Myron Stowe) [991615]
- [acpi] acpica: Update version to 20130517 (Myron Stowe) [991615]
- [acpi] acpica: _CST repair, handle null package entries (Myron Stowe) [991615]
- [acpi] acpica: Add several repairs for _CST predefined name (Myron Stowe) [991615]
- [acpi] acpica: Move _PRT repair into the standard complex repair module (Myron Stowe) [991615]
- [acpi] scan: Do not bind ACPI drivers to objects with scan handlers (Myron Stowe) [991615]
- [acpi] pm: Rework and clean up acpi_dev_pm_get_state() (Myron Stowe) [991615]
- [acpi] pm: Replace ACPI_STATE_D3 with ACPI_STATE_D3_COLD in device_pm.c (Myron Stowe) [991615]
- [acpi] pm: Rename function acpi_device_power_state() and make it static (Myron Stowe) [991615]
- [acpi] pm: acpi_processor_suspend() can be static (Myron Stowe) [991615]
- [virt] xen/acpi: Register an acpi_suspend_lowlevel callback (Myron Stowe) [991615]
- [x86] acpi/sleep: Provide registration for acpi_suspend_lowlevel (Myron Stowe) [991615]
- [acpi] Remove unused flags in acpi_device_flags (Myron Stowe) [991615]
- [acpi] Remove useless initializers (Myron Stowe) [991615]
- [acpi] battery: Make sure all spaces are in correct places (Myron Stowe) [991615]
- [acpi] add _STA evaluation at do_acpi_find_child() (Myron Stowe) [991615]
- [acpi] ec: access user space with get_user()/put_user() (Myron Stowe) [991615]
- [cpufreq] Simplify userspace governor (Myron Stowe) [991615]
- [acpi] lpss: override SDIO private register space size from ACPI tables (Myron Stowe) [991615]
- [acpi] lpss: mask the UART TX completion interrupt (Myron Stowe) [991615]
- [acpi] lpss: add support for Intel BayTrail (Myron Stowe) [991615]
- [acpi] Do not use CONFIG_ACPI_HOTPLUG_MEMORY_MODULE (Myron Stowe) [991615]
- [cpufreq] x86: make X86_AMD_FREQ_SENSITIVITY select CPU_FREQ_TABLE (Myron Stowe) [991615]
- [cpufreq] powerpc: make CBE_RAS select CPU_FREQ_TABLE (Myron Stowe) [991615]
- [cpufreq] blackfin: enable driver for CONFIG_BFIN_CPU_FREQ (Myron Stowe) [991615]
- [acpi] acpica: Clear events initialized flag upon event component termination (Myron Stowe) [991615]
- [acpi] acpica: Fix possible memory leak in GPE init error path (Myron Stowe) [991615]
- [acpi] acpica: on termination, delete global lock pending lock (Myron Stowe) [991615]
- [acpi] acpica: Update interface to acpi_ut_valid_acpi_name() (Myron Stowe) [991615]
- [acpi] acpica: Do not use extended sleep registers unless HW-reduced bit is set (Myron Stowe) [991615]
- [acpi] acpica: Split table print utilities to a new a separate file (Myron Stowe) [991615]
- [acpi] acpica: Add option to disable loading of SSDTs from the RSDT/XSDT (Myron Stowe) [991615]
- [acpi] acpica: Standardize all switch() blocks (Myron Stowe) [991615]
- [acpi] acpica: Split internal error msg routines to a separate file (Myron Stowe) [991615]
- [acpi] acpica: Split buffer dump routines into separate file (Myron Stowe) [991615]
- [acpi] scan: Simplify ACPI driver probing (Myron Stowe) [991615]
- [base] power/wakeup: Adjust messaging for wake events during suspend (Myron Stowe) [991615]
- [cpuidle] Fix ARCH_NEEDS_CPU_IDLE_COUPLED dependency warning (Myron Stowe) [991615]
- [cpuidle] Comment the driver's framework code (Myron Stowe) [991615]
- [cpuidle] simplify multiple driver support (Myron Stowe) [991615]
- [cpufreq] powerpc: move cpufreq driver to drivers/cpufreq (Myron Stowe) [991615]
- [cpufreq] acpi-cpufreq: Add ACPI processor device IDs to acpi-cpufreq (Myron Stowe) [991615]
- [cpufreq] remove unnecessary cpufreq_cpu_{get,put}() calls (Myron Stowe) [991615]
- [Documentation] MAINTAINERS: Add git tree path for ARM specific updates to cpufreq (Myron Stowe) [991615]
- [cpufreq] rename index as driver_data in cpufreq_frequency_table (Myron Stowe) [991615]
- [Documentation] power: Update .runtime_idle() callback documentation (Myron Stowe) [991615]
- [kernel] power: Rework the "runtime idle" helper routine (Myron Stowe) [991615]
- [kernel] power: print physical addresses consistently with other parts of kernel (Myron Stowe) [991615]
- [cpuidle] improve governor Kconfig options (Myron Stowe) [991615]
- [Documentation] MAINTAINERS: update mailing list for devfreq(DVFS) (Myron Stowe) [991615]
- [devfreq] fix typo "CPU_EXYNOS4.12" twice (Myron Stowe) [991615]
- [devfreq] add comments and Documentation (Myron Stowe) [991615]
- [devfreq] account suspend/resume for stats (Myron Stowe) [991615]
- [mm] memory_hotplug: Move alternative function definitions to header (Myron Stowe) [991615]
- [acpi] processor: Fix potential NULL pointer dereference in acpi_processor_add() (Myron Stowe) [991615]
- [acpi] acpica: Update version to 20130418 (Myron Stowe) [991615]
- [acpi] acpica: Update for "orphan" embedded controller _REG method support (Myron Stowe) [991615]
- [acpi] acpica: Remove unused macros, no functional change (Myron Stowe) [991615]
- [acpi] acpica: Predefined name support, remove unused local variable (Myron Stowe) [991615]
- [acpi] acpica: Add argument typechecking for all predefined ACPI names (Myron Stowe) [991615]
- [acpi] acpica: Add BIOS error interface for predefined name validation support (Myron Stowe) [991615]
- [acpi] acpica: Change an exception code for the ASL UnLoad() operator (Myron Stowe) [991615]
- [acpi] memhotplug: Simplify memory removal (Myron Stowe) [991615]
- [acpi] scan: Add second pass of companion offlining to hot-remove code (Myron Stowe) [991615]
- [base] memory: Drop offline_memory_block() (Myron Stowe) [991615]
- [acpi] processor: Pass processor object handle to acpi_bind_one() (Myron Stowe) [991615]
- [acpi] Drop removal_type field from struct acpi_device (Myron Stowe) [991615]
- [base] memory: Simplify __memory_block_change_state() (Myron Stowe) [991615]
- [acpi] processor: Initialize per_cpu(processors, pr->id) properly (Myron Stowe) [991615]
- [base] cpu: Fix sysfs cpu/online of offlined CPUs (Myron Stowe) [991615]
- [cpufreq] Don't create empty /sys/devices/system/cpu/cpufreq directory (Myron Stowe) [991615]
- [cpufreq] Move get_cpu_idle_time() to cpufreq.c (Myron Stowe) [991615]
- [cpufreq] governors: Move get_governor_parent_kobj() to cpufreq.c (Myron Stowe) [991615]
- [cpufreq] Add EXPORT_SYMBOL_GPL for have_governor_per_policy (Myron Stowe) [991615]
- [pnp] restore automatic resolution of DMA conflicts (Myron Stowe) [991615]
- [net] af_unix: use freezable blocking calls in read (Myron Stowe) [991615]
- [kernel] sigtimedwait: use freezable blocking call (Myron Stowe) [991615]
- [kernel] nanosleep: use freezable blocking call (Myron Stowe) [991615]
- [kernel] futex: use freezable blocking call (Myron Stowe) [991615]
- [fs] select: use freezable blocking call (Myron Stowe) [991615]
- [fs] epoll: use freezable blocking call (Myron Stowe) [991615]
- [kernel] freezer: add new freezable helpers using freezer_do_not_count() (Myron Stowe) [991615]
- [kernel] freezer: convert freezable helpers to static inline where possible (Myron Stowe) [991615]
- [kernel] freezer: convert freezable helpers to freezer_do_not_count() (Myron Stowe) [991615]
- [kernel] freezer: skip waking up tasks with PF_FREEZER_SKIP set (Myron Stowe) [991615]
- [kernel] power: shorten freezer sleep time using exponential backoff (Myron Stowe) [991615]
- [kernel] lockdep: check that no locks held at freeze time (Myron Stowe) [991615]
- [kernel] lockdep: remove task argument from debug_check_no_locks_held (Myron Stowe) [991615]
- [fs] cifs: add unsafe versions of freezable helpers for CIFS (Myron Stowe) [991615]
- [fs] nfs: add unsafe versions of freezable helpers for NFS (Myron Stowe) [991615]
- [base] memory: Introduce offline/online callbacks for memory blocks (Myron Stowe) [991615]
- [acpi] memhotplug: Bind removable memory blocks to ACPI device nodes (Myron Stowe) [991615]
- [acpi] processor: Use common hotplug infrastructure (Myron Stowe) [991615]
- [acpi] hotplug: Use device offline/online for graceful hot-removal (Myron Stowe) [991615]
- [base] cpu: Use generic offline/online for CPU offline/online (Myron Stowe) [991615]
- [base] core: Add offline/online device operations (Myron Stowe) [991615]
- [scsi] bnx2i: Fix bug on some bnx2x devices that don't support iSCSI (Tomas Henzl) [957024]
- [x86] tracing: Add irq_enter/exit() in smp_trace_reschedule_interrupt() (Seiji Aguchi) [741673]
- [x86] trace: Add config option checking to the definitions of mce handlers (Seiji Aguchi) [741673]
- [x86] trace: Do not call local_irq_save() in load_current_idt() (Seiji Aguchi) [741673]
- [x86] trace: Move creation of irq tracepoints from apic.c to irq.c (Seiji Aguchi) [741673]
- [x86] trace: Add irq vector tracepoints (Seiji Aguchi) [741673]
- [x86] trace: Rename variables for debugging (Seiji Aguchi) [741673]
- [x86] trace: Introduce entering/exiting_irq() (Seiji Aguchi) [741673]
- [tracing] Add DEFINE_EVENT_FN() macro (Seiji Aguchi) [741673]
- [fs] pstore: Fail to unlink if a driver has not defined pstore_erase (Steve Best) [996930]
- [powerpc] pseries: Inform the hypervisor we are using EBB regs (Steve Best) [997646]
- [powerpc] perf: Export PERF_EVENT_CONFIG_EBB_SHIFT to userspace (Steve Best) [997646]
- [powerpc] perf: Set PPC_FEATURE2_EBB when we register the power8 PMU (Steve Best) [997646]
- [powerpc] Fix hypervisor facility unavaliable vector number (Steve Best) [995354]
- [powerpc] Fix context switch DSCR on POWER8 (Steve Best) [995354]
- [powerpc] Rework setting up H/FSCR bit definitions (Steve Best) [995354]
- [powerpc] Wire up the HV facility unavailable exception (Steve Best) [995354]
- [powerpc] Rename and flesh out the facility unavailable exception handler (Steve Best) [995354]
- [powerpc] Remove KVMTEST from RELON exception handlers (Steve Best) [995354]
- [powerpc] tm: Fix context switching TAR, PPR and DSCR SPRs (Steve Best) [988340]
- [powerpc] Save the TAR register earlier (Steve Best) [988340]

* Wed Aug 21 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-11.el7]
- [security] Revert: Secure Boot related kernel enforcements (Jarod Wilson) [903815]

* Tue Aug 20 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-10.el7]
- [block] blk-mq: blk-mq should free bios in pass through case (Mike Snitzer) [960150]
- [block] blk-mq: add missing percpu_counter_destroy for mq_usage_counter (Mike Snitzer) [960150]
- [fs] direct-io: only inc_dec inode->i_dio_count for file systems (Mike Snitzer) [960150]
- [lib] percpu_counter: make APIs irq safe (Mike Snitzer) [960150]
- [block] null_blk: multi queue aware block test driver (Mike Snitzer) [960150]
- [kernel] smp: Export __smp_call_function_single() (Mike Snitzer) [960150]
- [block] blk-mq: change sw <-> hw queue mappings on hotplug events (Mike Snitzer) [960150]
- [block] blk-mq: re-initialize queue data structure after CPU hotplug (Mike Snitzer) [960150]
- [block] blk-mq: add queue freeze/unfreeze support (Mike Snitzer) [960150]
- [block] blk-mq: fix timer infinite loop after first timeout event (Mike Snitzer) [960150]
- [block] blk-mq: timeout fixes (Mike Snitzer) [960150]
- [block] blk-mq: cpu hot plug_unplug fixes (Mike Snitzer) [960150]
- [block] blk-mq: flush handling (Mike Snitzer) [960150]
- [block] blk-mq: new multi-queue block IO queueing mechanism (Mike Snitzer) [960150]
- [block] make rq->cmd_flags be 64-bit (Mike Snitzer) [960150]
- [kernel] smp: don't warn about csd->flags having CSD_FLAG_LOCK cleared for !wait (Mike Snitzer) [960150]
- [mm] sched: Allow uaccess in atomic with pagefault_disable() (Michael S. Tsirkin) [988029]
- [mm] sched: Drop voluntary schedule from might_fault() (Michael S. Tsirkin) [988029]
- [x86] uaccess s/might_sleep/might_fault/ (Michael S. Tsirkin) [988029]
- [powerpc] uaccess s/might_sleep/might_fault/ (Michael S. Tsirkin) [988029]
- [misc] asm-generic: uaccess s/might_sleep/might_fault/ (Michael S. Tsirkin) [988029]
- [x86] efi: Disable secure boot if shim is in insecure mode (Lenny Szubowicz) [903815]
- [kernel] modsign: Import certificates from UEFI Secure Boot (Lenny Szubowicz) [903815]
- [kernel] keys: Add a system blacklist keyring (Lenny Szubowicz) [903815]
- [crypto] asymmetric_keys: Add an EFI signature blob parser and key loader (Lenny Szubowicz) [903815]
- [kernel] modsign: Fix including certificate twice when the signing_key.x509 already exists (Lenny Szubowicz) [903815]
- [kernel] keys: Add a 'trusted' flag and a 'trusted only' flag (Lenny Szubowicz) [903815]
- [kernel] modsign: Separate the kernel signature checking keyring from module signing (Lenny Szubowicz) [903815]
- [kernel] modsign: Load *.x509 files into kernel keyring (Lenny Szubowicz) [903815]
- [efi] Add EFI signature data types (Lenny Szubowicz) [903815]
- [kernel] modsign: Always enforce module signing in a Secure Boot environment (Lenny Szubowicz) [903815]
- [kernel] hibernate: Disable in a Secure Boot environment (Lenny Szubowicz) [903815]
- [kernel] kexec: Disable in a secure boot environment (Lenny Szubowicz) [903815]
- [x86] Lock down MSR writing in secure boot (Lenny Szubowicz) [903815]
- [acpi] Ignore acpi_rsdp kernel parameter in a secure boot environment (Lenny Szubowicz) [903815]
- [char] mem: Restrict /dev/mem and /dev/kmem in secure boot setups (Lenny Szubowicz) [903815]
- [platform] asus-wmi: Restrict debugfs interface (Lenny Szubowicz) [903815]
- [acpi] Limit access to custom_method (Lenny Szubowicz) [903815]
- [x86] Lock down IO port access in secure boot environments (Lenny Szubowicz) [903815]
- [pci] Lock down BAR access in secure boot environments (Lenny Szubowicz) [903815]
- [x86] efi: Enable secure boot lockdown automatically when enabled in firmware (Lenny Szubowicz) [903815]
- [kernel] Add a kernel parameter that will force on Secure Boot mode (Lenny Szubowicz) [903815]
- [security] selinux: define mapping for new Secure Boot capability (Lenny Szubowicz) [903815]
- [uapi] Add new secure boot capability (Lenny Szubowicz) [903815]
- [kernel] audit: fix mq_open and mq_unlink to add the MQ root as a hidden parent audit_names record (Jeff Layton) [908885 953186]
- [kernel] audit: log the audit_names record type (Jeff Layton) [908885 953186]
- [kernel] audit: add child record before the create to handle case where create fails (Jeff Layton) [908885 953186]
- [md] dm-raid: silence compiler warning on rebuilds_per_group (Jonathan E Brassow) [970782]
- [md] dm-raid: Fix raid_resume not reviving failed devices in all cases (Jonathan E Brassow) [970782]
- [md] dm-raid: Break-up untidy function (Jonathan E Brassow) [970782]
- [s390] zfcp: block queue limits with data router (Hendrik Brueckner) [976657]
- [scsi] scsi_lib: Fix race between starved list and device removal (Ewan Milne) [986037]
- [md] dm-switch: add switch target (Mike Snitzer) [983188]
- [wireless] disable WiMAX support (John Linville) [915650]
- [fs] gfs2: don't overrun reserved revokes (Benjamin Marzinski) [950622]
- [fs] gfs2: Reserve journal space for quota change in do_grow (Robert S Peterson) [979131]
- [x86] setup: Add cpu_has_hypervisor check to rh_check_supported() (Prarit Bhargava) [986048]
- [x86] sched: Optimize switch_mm() for multi-threaded workloads (Rik van Riel) [990747]
- [crypto] nx: fix concurrency issue (Steve Best) [996565]
- [powerpc] mm: Fix fallthrough bug in hpte_decode (Steve Best) [993326]
- [misc] Kconfig: enable building user namespace with xfs (Dave Chinner) [987255]
- [fs] xfs: add capability check to free eofblocks ioctl (Dave Chinner) [987255]
- [fs] xfs: create internal eofblocks structure with kuid_t types (Dave Chinner) [987255]
- [fs] xfs: convert kuid_t to/from uid_t for internal structures (Dave Chinner) [987255]
- [fs] xfs: ioctl check for capabilities in the current user namespace (Dave Chinner) [987255]
- [fs] xfs: convert kuid_t to/from uid_t in ACLs (Dave Chinner) [987255]
- [fs] xfs: create wrappers for converting kuid_t to/from uid_t (Dave Chinner) [987255]
- [md] raid5: fix interaction of 'replace' and 'recovery' (Jes Sorensen) [978055]
- [md] raid10: remove use-after-free bug (Jes Sorensen) [978055]
- [md] raid1: fix bio handling problems in process_checks() (Jes Sorensen) [978055]
- [md] Remove recent change which allows devices to skip recovery (Jes Sorensen) [978055]
- [md] raid10: fix two problems with RAID10 resync (Jes Sorensen) [978055]
- [md] raid10: fix bug which causes all RAID10 reshapes to move no data (Jes Sorensen) [978055]
- [md] raid5: allow 5-device RAID6 to be reshaped to 4-device (Jes Sorensen) [978055]
- [md] raid10: fix two bugs affecting RAID10 reshape (Jes Sorensen) [978055]
- [md] Remember the last sync operation that was performed (Jes Sorensen) [978055]
- [md] raid0: fix buglet in RAID5 -> RAID0 conversion (Jes Sorensen) [978055]
- [md] raid10: check In_sync flag in 'enough()' (Jes Sorensen) [978055]
- [md] raid10: locking changes for 'enough()' (Jes Sorensen) [978055]
- [md] replace strict_strto*() with kstrto*() (Jes Sorensen) [978055]
- [md] Wait for md_check_recovery before attempting device removal (Jes Sorensen) [978055]
- [md] dm-raid: Add ability to restore transiently failed devices on resume (Jes Sorensen) [978055]
- [net] ipv6: resend MLD report if a link-local address completes DAD (Flavio Leitner) [889455]
- [net] ipv6: introduce per-interface counter for dad-completed ipv6 addresses (Flavio Leitner) [889455]
- [net] ipv6: split duplicate address detection and router solicitation timer (Flavio Leitner) [889455]
- [net] tcp: introduce a per-route knob for quick ack (Amerigo Wang) [984504]
- [net] nlmon: use standard rtnetlink link api for add/del devices (Daniel Borkmann) [957721]
- [net] nlmon: fix comparison in nlmon_is_valid_mtu (Daniel Borkmann) [957721]
- [net] packet: nlmon: virtual netlink monitoring device for packet sockets (Daniel Borkmann) [957721]
- [net] netlink: virtual tap device management (Daniel Borkmann) [957721]
- [net] if_arp: add ARPHRD_NETLINK type (Daniel Borkmann) [957721]

* Tue Aug 13 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-9.el7]
- [kernel] sched: disable autogroups by default (Josh Poimboeuf) [989741]
- [powerpc] pseries: Add backward compatibilty to read old kernel oops-log (Steve Best) [991831]
- [powerpc] pseries: Fix buffer overflow when reading from pstore (Steve Best) [991831]
- [crypto] nx: saves chaining value from co-processor (Steve Best) [972656]
- [crypto] nx: fix limits to sg lists for SHA-2 (Steve Best) [972656]
- [crypto] nx: fix physical addresses added to sg lists (Steve Best) [972656]

* Mon Aug 12 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-8.el7]
- [net] ipv6: ip6_append_data_mtu did not care about pmtudisc and frag_size (Francesco Fusco) [994346] {CVE-2013-4163}
- [net] ipv6: call udp_push_pending_frames when uncorking a socket with AF_INET pending data (Francesco Fusco) [988355] {CVE-2013-4162}
- [kernel] sysctl: range checking in do_proc_dointvec_ms_jiffies_conv (Francesco Fusco) [972393]
- [net] neigh: prevent overflowing params in /proc/sys/net/ipv4/neigh/ (Francesco Fusco) [972393]
- [net] vhost-net: fix use-after-free in vhost_net_flush (Thomas Graf) [984723] {CVE-2013-4127}
- [powerpc] tm: Fix return of active 64bit signals (Steve Best) [731886]
- [powerpc] tm: Fix return of 32bit rt signals to active transactions (Steve Best) [731886]
- [powerpc] tm: Fix restoration of MSR on 32bit signal return (Steve Best) [731886]
- [powerpc] tm: Fix 32 bit non-rt signals (Steve Best) [731886]
- [powerpc] tm: Fix writing top half of MSR on 32 bit signals (Steve Best) [731886]
- [fs] nfs: verify open flags before allowing an atomic open (Jeff Layton) [984823]
- [s390] zfcp: module parameter dbflevel for early debugging (Hendrik Brueckner) [994597]
- [virt] virtio_net: fix the race between channels setting and refill (Jason Wang) [978153]
- [kernel] audit: restore order of tty and ses fields in log output (Richard Guy Briggs) [983157]
- [kernel] time/tick: Make oneshot broadcast robust vs. CPU offlining (Prarit Bhargava) [967464]
- [virt] virtio_net: fix race in RX VQ processing (Jason Wang) [989409]
- [virt] virtio: support unlocked queue poll (Jason Wang) [989409]
- [powerpc] mm: Use the correct SLB(LLP) encoding in tlbie instruction (Steve Best) [993448]
- [net] tuntap: do not zerocopy if iov needs more pages than MAX_SKB_FRAGS (Jason Wang) [982513]
- [net] tuntap: correctly linearize skb when zerocopy is used (Jason Wang) [982513]
- [virt] macvtap: do not zerocopy if iov needs more pages than MAX_SKB_FRAGS (Jason Wang) [990786]
- [virt] macvtap: do not assume 802.1Q when send vlan packets (Jason Wang) [990786]
- [virt] macvtap: fix the missing ret value of TUNSETQUEUE (Jason Wang) [990786]
- [virt] macvtap: correctly linearize skb when zerocopy is used (Jason Wang) [982513]
- [virt] macvtap: Perform GSO on forwarding path (Jason Wang) [895484]
- [virt] macvtap: Let TUNSETOFFLOAD actually controll offload features (Jason Wang) [895484]
- [virt] macvtap: Consistently use rcu functions (Jason Wang) [895484]
- [virt] macvtap: Convert to using rtnl lock (Jason Wang) [895484]
- [virt] macvtap: fix uninitialized return value macvtap_ioctl_set_queue() (Jason Wang) [731550]
- [virt] macvtap: slient sparse warnings (Jason Wang) [731550]
- [virt] macvtap: enable multiqueue flag (Jason Wang) [731550]
- [virt] macvtap: add TUNSETQUEUE ioctl (Jason Wang) [731550]
- [virt] macvtap: eliminate linear search (Jason Wang) [731550]
- [virt] macvtap: introduce macvtap_get_vlan() (Jason Wang) [731550]
- [virt] macvtap: do not add self to waitqueue if doing a nonblock read (Jason Wang) [731550]
- [virt] macvtap: fix a possible race between queue selection and changing queues (Jason Wang) [731550]

* Thu Aug 08 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-7.el7]
- [vfio] type1: Fix leak on error path (Alex Williamson) [984081]
- [vfio] Limit group opens (Alex Williamson) [984081]
- [vfio] type1: Fix missed frees and zero sized removes (Alex Williamson) [984081]
- [vfio] Provide module option to disable vfio_iommu_type1 hugepage support (Alex Williamson) [984081]
- [vfio] hugepage support for vfio_iommu_type1 (Alex Williamson) [984081]
- [vfio] Convert type1 iommu to use rbtree (Alex Williamson) [984081]
- [iommu] Use pa and zx instead of casting (Alex Williamson) [984081]
- [iommu] amd: Only unmap large pages from the first pte (Alex Williamson) [984081]
- [iommu] Fix compiler warning on pr_debug (Alex Williamson) [984081]
- [iommu] amd: Fix memory leak in free_pagetable (Alex Williamson) [984081]
- [iommu] Split iommu_unmaps (Alex Williamson) [984081]
- [iommu] intel, amd: Remove multifunction assumption around grouping (Alex Williamson) [984081]
- [x86] spinlock: make ticket lock increment 2, unconditionally (Rik van Riel) [970737]
- [virt] pvticketlock: When paravirtualizing ticket locks, increment by 2 (Rik van Riel) [970737]
- [scsi] isci: Fix a race condition in the SSP task management path (David Milburn) [990201]
- [netdrv] bnx2x: Wait for MCP validity during AER (Michal Schmidt) [797460]
- [virt] virtio_scsi: Fix virtqueue affinity setup (Asias He) [971826]
- [fs] nfs: fix open(O_RDONLY|O_TRUNC) in NFS4.0 (Jeff Layton) [987615]
- [watchdog] hpwdt: Add check for UEFI bits (Linda Knippers) [985195]
- [powerpc] mm/numa: VPHN topology change updates all siblings (Steve Best) [973594]
- [powerpc] powernv: Fix iommu initialization again (Steve Best) [979523]
- [firmware] efivars: If pstore_register fails, free unneeded pstore buffer (Lenny Szubowicz) [983597]
- [acpi] Eliminate console msg if pstore.backend excludes ERST (Lenny Szubowicz) [983597]
- [fs] pstore: Return unique error if backend registration excluded by kernel param (Lenny Szubowicz) [983597]

* Tue Aug 06 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-6.el7]
- [fs] locks: move file_lock_list to a set of percpu hlist_heads and convert file_lock_lock to an lglock (Jeff Layton) [976876]
- [fs] seq_file: add seq_list_*_percpu helpers (Jeff Layton) [976876]
- [fs] locks: give the blocked_hash its own spinlock (Jeff Layton) [976876]
- [fs] locks: add a new "lm_owner_key" lock operation (Jeff Layton) [976876]
- [fs] locks: turn the blocked_list into a hashtable (Jeff Layton) [976876]
- [fs] locks: convert fl_link to a hlist_node (Jeff Layton) [976876]
- [fs] locks: avoid taking global lock if possible when waking up blocked waiters (Jeff Layton) [976876]
- [fs] locks: protect most of the file_lock handling with i_lock (Jeff Layton) [976876]
- [fs] locks: encapsulate the fl_link list handling (Jeff Layton) [976876]
- [fs] locks: make "added" in __posix_lock_file a bool (Jeff Layton) [976876]
- [fs] locks: comment cleanups and clarifications (Jeff Layton) [976876]
- [fs] locks: make generic_add_lease and generic_delete_lease static (Jeff Layton) [976876]
- [fs] cifs: use posix_unblock_lock instead of locks_delete_block (Jeff Layton) [976876]
- [fs] locks: drop the unused filp argument to posix_unblock_lock (Jeff Layton) [976876]
- [scsi] ipr: IOA Status Code(IOASC) update (Steve Best) [731129]
- [scsi] ipr: qc_fill_rtf() method should not store alternate status register (Steve Best) [731129]
- [scsi] ipr: possible irq lock inversion dependency detected (Steve Best) [731129]
- [fs] nfsd: when dentry_open returns an error do not propagate as struct file (Steve Dickson) [987090]
- [net] sunrpc: underflow issue in decode_write_list() (Steve Dickson) [987090]
- [fs] nfsd: fix minorversion support interface (Steve Dickson) [987090]
- [fs] lockd: protect nlm_blocked access in nlmsvc_retry_blocked (Steve Dickson) [987090]
- [fs] nfsd: support minorversion 1 by default (Steve Dickson) [987090]
- [fs] nfsd: allow destroy_session over destroyed session (Steve Dickson) [987090]
- [net] sunrpc: fix failures to handle -1 uid's (Steve Dickson) [987090]
- [net] sunrpc: Don't schedule an upcall on a replaced cache entry (Steve Dickson) [987090]
- [net] sunrpc: xpt_auth_cache should be ignored when expired (Steve Dickson) [987090]
- [net] sunrpc/cache: ensure items removed from cache do not have pending upcalls (Steve Dickson) [987090]
- [net] sunrpc/cache: use cache_fresh_unlocked consistently and correctly (Steve Dickson) [987090]
- [net] sunrpc/cache: remove races with queuing an upcall (Steve Dickson) [987090]
- [fs] nfsd: return delegation immediately if lease fails (Steve Dickson) [987090]
- [fs] nfsd: do not throw away 4.1 lock state on last unlock (Steve Dickson) [987090]
- [fs] nfsd: delegation-based open reclaims should bypass permissions (Steve Dickson) [987090]
- [net] sunrpc: don't error out on small tcp fragment (Steve Dickson) [987090]
- [net] sunrpc: fix handling of too-short rpc's (Steve Dickson) [987090]
- [fs] nfsd: minor read_buf cleanup (Steve Dickson) [987090]
- [fs] nfsd: fix decoding of compounds across page boundaries (Steve Dickson) [987090]
- [fs] nfsd: clean up nfs4_open_delegation (Steve Dickson) [987090]
- [fs] nfsd: Don't give out read delegations on creates (Steve Dickson) [987090]
- [fs] nfsd: allow client to send no cb_sec flavors (Steve Dickson) [987090]
- [fs] nfsd: fail attempts to request gss on the backchannel (Steve Dickson) [987090]
- [fs] nfsd: implement minimal SP4_MACH_CRED (Steve Dickson) [987090]
- [net] sunrpc: store gss mech in svc_cred (Steve Dickson) [987090]
- [net] sunrpc: introduce init_svc_cred (Steve Dickson) [987090]
- [fs] nfsd: avoid undefined signed overflow (Steve Dickson) [987090]
- [net] sunrpc: the cache_detail in cache_is_valid is unused any more (Steve Dickson) [987090]
- [net] sunrpc: server back channel needs no rpcbind method (Steve Dickson) [987090]
- [fs] nfsd: fix compile in !CONFIG_NFSD_V4_SECURITY_LABEL case (Steve Dickson) [987090]
- [fs] nfsd: Server implementation of MAC Labeling (Steve Dickson) [987090]
- [fs] nfsd: Add NFS v4.2 support to the NFS server (Steve Dickson) [987090]
- [security] fix cap_inode_getsecctx returning garbage (Steve Dickson) [987090]
- [fs] nfsd: store correct client minorversion for >=4.2 (Steve Dickson) [987090]
- [fs] nfsd: get rid of the unused functions in vfs (Steve Dickson) [987090]
- [fs] nfs: Fix brainfart in attribute length calculation (Steve Dickson) [987090]
- [fs] nfs: Fix a regression against the FreeBSD server (Steve Dickson) [987090]
- [net] sunrpc/rpc_pipe: rpc_dir_inode_operations can be static (Steve Dickson) [987090]
- [fs] nfs: Allow nfs_updatepage to extend a write under additional circumstances (Steve Dickson) [987090]
- [fs] nfs: Make nfs_readdir revalidate less often (Steve Dickson) [987090]
- [fs] nfs: Make nfs_attribute_cache_expired() non-static (Steve Dickson) [987090]
- [net] sunrpc/rpc_pipe: set dentry operations at d_alloc time (Steve Dickson) [987090]
- [fs] nfs: set verifier on existing dentries in nfs_prime_dcache (Steve Dickson) [987090]
- [fs] nfs: Set NFS_CS_MIGRATION for NFSv4 mounts (Steve Dickson) [987090]
- [fs] nfs: Refactor nfs4_init_session and nfs4_init_channel_attrs (Steve Dickson) [987090]
- [fs] nfs: use pnfs_device maxcount for the objectlayout gdia_maxcount (Steve Dickson) [987090]
- [fs] nfs: use pnfs_device maxcount for the blocklayout gdia_maxcount (Steve Dickson) [987090]
- [fs] nfs: Fix gdia_maxcount calculation to fit in ca_maxresponsesize (Steve Dickson) [987090]
- [fs] nfs: Improve legacy idmapping fallback (Steve Dickson) [987090]
- [fs] nfs: end back channel session draining (Steve Dickson) [987090]
- [fs] nfs: Apply v4.1 capabilities to v4.2 (Steve Dickson) [987090]
- [fs] nfs: Clean up layout segment comparison helper names (Steve Dickson) [987090]
- [fs] nfs: layout segment comparison helpers should take 'const' parameters (Steve Dickson) [987090]
- [fs] nfs: Move the DNS resolver into the NFSv4 module (Steve Dickson) [987090]
- [net] sunrpc/rpc_pipefs: only set rpc_dentry_ops if d_op isn't already set (Steve Dickson) [987090]
- [fs] nfs: SETCLIENTID add the format string for the NETID (Steve Dickson) [987090]
- [fs] nfs: Add in v4.2 callback operation (Steve Dickson) [987090]
- [fs] nfs: Make callbacks minor version generic (Steve Dickson) [987090]
- [fs] nfs: Add Kconfig entry for Labeled NFS V4 client (Steve Dickson) [987090]
- [fs] nfs: Extend NFS xattr handlers to accept the security namespace (Steve Dickson) [987090]
- [fs] nfs: Client implementation of Labeled-NFS (Steve Dickson) [987090]
- [fs] nfs: Add label lifecycle management (Steve Dickson) [987090]
- [fs] nfs: Add labels to client function prototypes (Steve Dickson) [987090]
- [fs] nfs: Extend fattr bitmaps to support all 3 words (Steve Dickson) [987090]
- [fs] nfs: Introduce new label structure (Steve Dickson) [987090]
- [fs] nfs: Add label recommended attribute and NFSv4 flags (Steve Dickson) [987090]
- [fs] nfs: Added NFS v4.2 support to the NFS client (Steve Dickson) [987090]
- [security] selinux: Add new labeling type native labels (Steve Dickson) [987090]
- [security] lsm: Add flags field to security_sb_set_mnt_opts for in kernel mount data (Steve Dickson) [987090]
- [security] Add Hook to test if the particular xattr is part of a MAC model (Steve Dickson) [987090]
- [security] Add hook to calculate context based on a negative dentry (Steve Dickson) [987090]
- [fs] nfs: Close another NFSv4 recovery race (Steve Dickson) [987090]
- [fs] nfs: Move dentry instantiation into the NFSv4-specific atomic open code (Steve Dickson) [987090]
- [fs] nfs: Refactor _nfs4_open_and_get_state to set ctx->state (Steve Dickson) [987090]
- [fs] nfs: pass the nfs_open_context to nfs4_do_open (Steve Dickson) [987090]
- [fs] nfs: Remove redundant check for FMODE_EXEC in nfs_finish_open (Steve Dickson) [987090]
- [net] sunrpc: Remove redundant call to rpc_set_running() in __rpc_execute() (Steve Dickson) [987090]
- [net] sunrpc: Remove unused functions rpc_task_set/has_priority (Steve Dickson) [987090]
- [net] sunrpc: Remove the unused helpers task_for_each() and task_for_first() (Steve Dickson) [987090]
- [net] sunrpc: Remove unused function rpc_queue_empty (Steve Dickson) [987090]
- [net] sunrpc: Fix a potential race in rpc_execute (Steve Dickson) [987090]
- [fs] nfs: Simplify setting the layout header credential (Steve Dickson) [987090]
- [fs] nfs: Enable state protection (Steve Dickson) [987090]
- [fs] nfs: Use layout credentials for get_deviceinfo calls (Steve Dickson) [987090]
- [fs] nfs: Ensure that test_stateid and free_stateid use correct credentials (Steve Dickson) [987090]
- [fs] nfs: Ensure that reclaim_complete uses the right credential (Steve Dickson) [987090]
- [fs] nfs: Ensure that layoutreturn uses the correct credential (Steve Dickson) [987090]
- [fs] nfs: Ensure that layoutget is called using the layout credential (Steve Dickson) [987090]
- [fs] nfs: Add NFSv4.2 protocol constants (Steve Dickson) [987090]

* Fri Aug 02 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-5.el7]
- [fs] cifs: fix bad error handling in crypto code (Jeff Layton) [988398]
- [fs] cifs: Fix a deadlock when a file is reopened (Sachin Prabhu) [988398]
- [fs] cifs: Reopen the file if reconnect durable handle failed (Sachin Prabhu) [988398]
- [fs] cifs: Fix minor endian error in durable handle patch series (Sachin Prabhu) [988398]
- [fs] cifs: Reconnect durable handles for SMB2 (Sachin Prabhu) [988398]
- [fs] cifs: Make SMB2_open use cifs_open_parms struct (Sachin Prabhu) [988398]
- [fs] cifs: Introduce cifs_open_parms struct (Sachin Prabhu) [988398]
- [fs] cifs: Request durable open for SMB2 opens (Sachin Prabhu) [988398]
- [fs] cifs: Simplify SMB2 create context handling (Sachin Prabhu) [988398]
- [fs] cifs: Simplify SMB2_open code path (Sachin Prabhu) [988398]
- [fs] cifs: Respect create_options in smb2_open_file (Sachin Prabhu) [988398]
- [fs] cifs: Fix lease context buffer parsing (Sachin Prabhu) [988398]
- [fs] cifs: use sensible file nlink values if unprovided (Sachin Prabhu) [988398]
- [fs] cifs: Limit allocation of crypto mechanisms to dialect which requires (Sachin Prabhu) [988398]
- [fs] cifs: Don't pass inode to ->d_hash() and ->d_compare() (Sachin Prabhu) [988398]
- [fs] cifs: fill TRANS2_QUERY_FILE_INFO ByteCount fields (Sachin Prabhu) [988398]
- [fs] cifs: fix SMB2 signing enablement in cifs_enable_signing (Sachin Prabhu) [988398]
- [fs] cifs: Fix build warning (Sachin Prabhu) [988398]
- [fs] cifs: SMB3 Signing enablement (Sachin Prabhu) [988398]
- [fs] cifs: Do not set DFS flag on SMB2 open (Sachin Prabhu) [988398]
- [fs] cifs: fix static checker warning (Sachin Prabhu) [988398]
- [fs] cifs: try to handle the MUST SecurityFlags sanely (Sachin Prabhu) [988398]
- [fs] cifs: When server doesn't provide SecurityBuffer on SMB2Negotiate pick default (Sachin Prabhu) [988398]
- [fs] cifs: Handle big endianness in NTLM (ntlmv2) authentication (Sachin Prabhu) [988398]
- [fs] cifs: revalidate directories instiantiated via FIND_* in order to handle DFS referrals (Sachin Prabhu) [988398]
- [fs] cifs: SMB2 FSCTL and IOCTL worker function (Sachin Prabhu) [988398]
- [fs] cifs: Charge at least one credit, if server says that it supports multicredit (Sachin Prabhu) [988398]
- [fs] cifs: Remove typo (Sachin Prabhu) [988398]
- [fs] cifs: Some missing share flags (Sachin Prabhu) [988398]
- [fs] cifs: using strlcpy instead of strncpy (Sachin Prabhu) [988398]
- [fs] cifs: Update headers to update various SMB3 ioctl definitions (Sachin Prabhu) [988398]
- [fs] cifs: Update cifs version number (Sachin Prabhu) [988398]
- [fs] cifs: Add ability to dipslay SMB3 share flags and capabilities for debugging (Sachin Prabhu) [988398]
- [fs] cifs: Add some missing SMB3 and SMB3.02 flags (Sachin Prabhu) [988398]
- [fs] cifs: Add SMB3.02 dialect support (Sachin Prabhu) [988398]
- [fs] cifs: Fix endian error in SMB2 protocol negotiation (Sachin Prabhu) [988398]
- [fs] cifs: clean up the SecurityFlags write handler (Sachin Prabhu) [988398]
- [fs] cifs: update the default global_secflags to include "raw" NTLMv2 (Sachin Prabhu) [988398]
- [fs] move sectype to the cifs_ses instead of TCP_Server_Info (Sachin Prabhu) [988398]
- [fs] cifs: track the enablement of signing in the TCP_Server_Info (Sachin Prabhu) [988398]
- [fs] add new fields to smb_vol to track the requested security flavor (Sachin Prabhu) [988398]
- [fs] cifs: add new fields to cifs_ses to track requested security flavor (Sachin Prabhu) [988398]
- [fs] cifs: track the flavor of the NEGOTIATE reponse (Sachin Prabhu) [988398]
- [fs] cifs: add new "Unspecified" securityEnum value (Sachin Prabhu) [988398]
- [fs] cifs: factor out check for extended security bit into separate function (Sachin Prabhu) [988398]
- [fs] cifs: move handling of signed connections into separate function (Sachin Prabhu) [988398]
- [fs] cifs: break out lanman NEGOTIATE handling into separate function (Sachin Prabhu) [988398]
- [fs] cifs: break out decoding of security blob into separate function (Sachin Prabhu) [988398]
- [fs] cifs: remove the cifs_ses->flags field (Sachin Prabhu) [988398]
- [fs] cifs: throw a warning if negotiate or sess_setup ops are passed NULL server or session pointers (Sachin Prabhu) [988398]
- [fs] cifs: make decode_ascii_ssetup void return (Sachin Prabhu) [988398]
- [fs] cifs: remove useless memset in LANMAN auth code (Sachin Prabhu) [988398]
- [fs] cifs: remove protocolEnum definition (Sachin Prabhu) [988398]
- [fs] cifs: add a "nosharesock" mount option to force new sockets to server to be created (Sachin Prabhu) [988398]
- [fs] fuse: readdirplus cleanup (Niels de Vos) [988312]
- [fs] fuse: readdirplus change attributes once (Niels de Vos) [988312]
- [fs] fuse: readdirplus fix instantiate (Niels de Vos) [988312]
- [fs] fuse: readdirplus sanity checks (Niels de Vos) [988312]
- [fs] fuse: fix readdirplus dentry leak (Niels de Vos) [988312]
- [powerpc] hw_brk: Fix off by one error when validating DAWR region end (Steve Best) [843485]
- [powerpc] hw_brk: Fix clearing of extraneous IRQ (Steve Best) [843485]
- [powerpc] hw_brk: Fix setting of length for exact mode breakpoints (Steve Best) [843485]
- [powerpc] perf: Add power8 EBB support (Steve Best) [969176]
- [powerpc] perf: Core EBB support for 64-bit book3s (Steve Best) [969176]
- [powerpc] perf: Don't enable if we have zero events (Steve Best) [969176]
- [powerpc] powerpc/perf: Use existing out label in power_pmu_enable() (Steve Best) [969176]
- [powerpc] perf: Freeze PMC5/6 if we're not using them (Steve Best) [969176]
- [powerpc] powerpc/perf: Rework disable logic in pmu_disable() (Steve Best) [969176]
- [powerpc] perf: Check that events only include valid bits on Power8 (Steve Best) [969176]
- [ipc] sem: rename try_atomic_semop() to perform_atomic_semop(), docu update (Rik van Riel) [881820]
- [ipc] sem: replace shared sem_otime with per-semaphore value (Rik van Riel) [881820]
- [ipc] sem: always use only one queue for alter operations (Rik van Riel) [881820]
- [ipc] sem: separate wait-for-zero and alter tasks into seperate queues (Rik van Riel) [881820]
- [ipc] sem: cacheline align the semaphore structures (Rik van Riel) [881820]
- [fs] gfs2: Add atomic_open support (Steven Whitehouse) [983098]
- [fs] gfs2: Only do one directory search on create (Steven Whitehouse) [983098]
- [fs] pstore: Add hsize argument in write_buf call of pstore_ftrace_call (Steve Best) [947161]
- [powerpc] pseries: Support compression of oops text via pstore (Steve Best) [947161]
- [powerpc] pseries: Re-organise the oops compression code (Steve Best) [947161]
- [powerpc] pstore: Pass header size in the pstore write callback (Steve Best) [947161]
- [powerpc] pseries: Read common partition via pstore (Steve Best) [947161]
- [powerpc] pseries: Read of-config partition via pstore (Steve Best) [947161]
- [powerpc] pseries: Distinguish between a os-partition and non-os partition (Steve Best) [947161]
- [powerpc] pseries: Read rtas partition via pstore (Steve Best) [947161]
- [powerpc] pseries: Read/Write oops nvram partition via pstore (Steve Best) [947161]
- [powerpc] pseries: Introduce generic read function to read nvram-partitions (Steve Best) [947161]
- [powerpc] pseries: Add version and timestamp to oops header (Steve Best) [947161]
- [powerpc] pseries: Remove syslog prefix in uncompressed oops text (Steve Best) [947161]

* Wed Jul 31 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-4.el7]
- [x86] signals: Merge EFLAGS bit clearing into a single statement (Jiri Olsa) [986216]
- [x86] signals: Clear RF EFLAGS bit for signal handler (Jiri Olsa) [986216]
- [x86] signals: Propagate RF EFLAGS bit through the signal restore call (Jiri Olsa) [986216]
- [kernel] perf: Fix perf_lock_task_context() vs RCU (Jiri Olsa) [986216]
- [kernel] perf: Remove WARN_ON_ONCE() check in __perf_event_enable() for valid scenario (Jiri Olsa) [986216]
- [kernel] perf: Clone child context from parent context pmu (Jiri Olsa) [986216]
- [kernel] perf: Fix interrupt handler timing harness (Jiri Olsa) [986216]
- [kernel] perf: Drop sample rate when sampling is too slow (Jiri Olsa) [986216]
- [kernel] hw_breakpoint: Introduce "struct bp_cpuinfo" (Jiri Olsa) [986216]
- [kernel] hw_breakpoint: Simplify *register_wide_hw_breakpoint() (Jiri Olsa) [986216]
- [kernel] hw_breakpoint: Introduce cpumask_of_bp() (Jiri Olsa) [986216]
- [kernel] hw_breakpoint: Simplify the "weight" usage in toggle_bp_slot() paths (Jiri Olsa) [986216]
- [kernel] hw_breakpoint: Simplify list/idx mess in toggle_bp_slot() paths (Jiri Olsa) [986216]
- [kernel] perf: Add simple Haswell PMU support (Jiri Olsa) [986216]
- [kernel] perf: Add const qualifier to perf_pmu_register's 'name' arg (Jiri Olsa) [986216]
- [kernel] perf: Fix hypervisor branch sampling permission check (Jiri Olsa) [986216]
- [kernel] perf: Check branch sampling priv level in generic code (Jiri Olsa) [986216]
- [kernel] perf: Add sysfs entry to adjust multiplexing interval per PMU (Jiri Olsa) [986216]
- [kernel] perf: Use hrtimers for event multiplexing (Jiri Olsa) [986216]
- [kernel] perf: Fix hw breakpoints overflow period sampling (Jiri Olsa) [986216]
- [tools] perf/tests: Check proper prev_state size for sched_switch tp (Jiri Olsa) [984998]
- [tools] perf/tests: Omit end of the symbol check failure for test 1 (Jiri Olsa) [984998]
- [tools] perf/script: Fix broken include in Context.xs (Jiri Olsa) [984998]
- [tools] perf: Fix -ldw/-lelf link test when static linking (Jiri Olsa) [984998]
- [tools] perf: Fix perf version generation (Jiri Olsa) [984998]
- [tools] perf/stat: Fix per-socket output bug for uncore events (Jiri Olsa) [984998]
- [tools] perf/symbols: Fix vdso list searching (Jiri Olsa) [984998]
- [tools] perf/evsel: Fix missing increment in sample parsing (Jiri Olsa) [984998]
- [tools] perf: Update symbol_conf.nr_events when processing attribute events (Jiri Olsa) [984998]
- [tools] perf: Fix new_term() missing free on error path (Jiri Olsa) [984998]
- [tools] perf: Fix parse_events_terms() segfault on error path (Jiri Olsa) [984998]
- [tools] perf/evsel: Fix count parameter to read call in event_format__new (Jiri Olsa) [984998]
- [tools] perf: Fix -x/--exclude-other option for report command (Jiri Olsa) [984998]
- [tools] perf/evlist: Enhance perf_evlist__start_workload() (Jiri Olsa) [984998]
- [tools] perf/record: Remove -f/--force option (Jiri Olsa) [984998]
- [tools] perf/record: Remove -A/--append option (Jiri Olsa) [984998]
- [tools] perf/stat: Avoid sending SIGTERM to random processes (Jiri Olsa) [984998]
- [tools] perf: Include termios.h explicitly (Jiri Olsa) [984998]
- [tools] perf/bench: Fix memory allocation fail check in mem{set, cpy} workloads (Jiri Olsa) [984998]
- [tools] perf: Fix build errors with O and DESTDIR make vars set (Jiri Olsa) [984998]
- [tools] perf: Fix output directory of Documentation/ (Jiri Olsa) [984998]
- [tools] perf: Get only verbose output with V=1 (Jiri Olsa) [984998]
- [tools] perf: Add missing liblk.a dependency for python/perf.so (Jiri Olsa) [984998]
- [tools] perf: Remove '?=' Makefile STRIP assignment (Jiri Olsa) [984998]
- [tools] perf: Replace multiple line assignment with multiple statements (Jiri Olsa) [984998]
- [tools] perf: Replace tabs with spaces for all non-commands statements (Jiri Olsa) [984998]
- [tools] perf: Add NO_BIONIC variable to confiure bionic setup (Jiri Olsa) [984998]
- [tools] perf: Switch to full path C include directories (Jiri Olsa) [984998]
- [tools] perf: Merge all *LDFLAGS* make variable into LDFLAGS (Jiri Olsa) [984998]
- [tools] perf: Merge all *CFLAGS* make variable into CFLAGS (Jiri Olsa) [984998]
- [tools] perf/evlist: Reset SIGTERM handler in workload child process (Jiri Olsa) [984998]
- [tools] perf: Remove cwdlen from struct perf_session (Jiri Olsa) [984998]
- [tools] perf: Remove frozen from perf_header struct (Jiri Olsa) [984998]
- [tools] perf/tests: Fix exclude_guest|exclude_host checking for attr tests (Jiri Olsa) [984998]
- [tools] perf/tests: Fix attr test for record -d option (Jiri Olsa) [984998]
- [tools] perf: Final touches for CHK config move (Jiri Olsa) [984998]
- [tools] perf: Move paths config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libnuma check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move stdlib check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libbfd check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libpython check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libperl check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move gtk2 check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move slang check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libaudit check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libunwind check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libdw check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move libelf check config into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move compiler and linker flags check into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move programs check into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Move arch check into config/Makefile (Jiri Olsa) [984998]
- [tools] perf: Add automated make test suite (Jiri Olsa) [984998]
- [tools] perf: Save parent pid in thread struct (Jiri Olsa) [984998]
- [tools] perf/stats: Fix divide by 0 in variance (Jiri Olsa) [984998]
- [tools] perf/kvm: Handle realloc failures (Jiri Olsa) [984998]
- [tools] perf/evsel: Fix printing of perf_event_paranoid message (Jiri Olsa) [984998]
- [tools] perf/test: Fix typo (Jiri Olsa) [984998]
- [tools] perf/hists: Rename hist_entry__add_pair arguments (Jiri Olsa) [984998]
- [tools] perf/diff: Use internal rb tree for hists__precompute (Jiri Olsa) [984998]
- [tools] perf/report: Add report.percent-limit config variable (Jiri Olsa) [984998]
- [tools] perf/top: Add --percent-limit option (Jiri Olsa) [984998]
- [tools] perf/report: Add --percent-limit option (Jiri Olsa) [984998]
- [tools] perf/report: Don't bother locking when adding hist entries (Jiri Olsa) [984998]
- [tools] perf/hists: Move locking to its call-sites (Jiri Olsa) [984998]
- [tools] perf/top: Get rid of *_threaded() functions (Jiri Olsa) [984998]
- [tools] perf/top: Fix percent output when no samples collected (Jiri Olsa) [984998]
- [tools] perf/top: Fix -E option behavior (Jiri Olsa) [984998]
- [tools] perf/record: handle death by SIGTERM (Jiri Olsa) [984998]
- [tools] perf: Handle JITed code in shared memory (Jiri Olsa) [984998]
- [tools] perf/tests: Fix compile errors in bp_signal files (Jiri Olsa) [984998]
- [tools] perf: Fix tab vs spaces issue in Makefile ifdef/endif (Jiri Olsa) [984998]
- [tools] perf/hists browser: Use sort__has_sym (Jiri Olsa) [984998]
- [tools] perf/top: Use sort__has_sym (Jiri Olsa) [984998]
- [tools] perf/sort: Cleanup sort__has_sym setting (Jiri Olsa) [984998]
- [tools] perf/sort: Reorder HISTC_SRCLINE index (Jiri Olsa) [984998]
- [tools] perf/archive: Fix typo on Documentation (Jiri Olsa) [984998]
- [tools] perf/sort: Consolidate sort_entry__setup_elide() (Jiri Olsa) [984998]
- [tools] perf/sort: Separate out memory-specific sort keys (Jiri Olsa) [984998]
- [tools] perf/sort: Factor out common code in sort_dimension__add() (Jiri Olsa) [984998]
- [tools] perf/sort: Introduce sort__mode variable (Jiri Olsa) [984998]
- [tools] perf/report: Fix alignment of symbol column when -v is given (Jiri Olsa) [984998]
- [tools] perf/hists: Free unused mem info of a matched hist entry (Jiri Olsa) [984998]
- [tools] perf/hists: Fix an invalid memory free on he->branch_info (Jiri Olsa) [984998]
- [tools] perf: Fix bug in isupper() and islower() (Jiri Olsa) [984998]
- [mm] thp: define HPAGE_PMD_* constants as BUILD_BUG() if !THP (Steve Best) [947166]
- [powerpc] mm: Fix build warnings with CONFIG_TRANSPARENT_HUGEPAGE disabled (Steve Best) [947166]
- [powerpc] mm: Optimize hugepage invalidate (Steve Best) [947166]
- [powerpc] thp: Enable THP on PPC64 (Steve Best) [947166]
- [powerpc] mm: split hugepage when using subpage protection (Steve Best) [947166]
- [powerpc] mm: disable assert_pte_locked for collapse_huge_page (Steve Best) [947166]
- [powerpc] mm: Prevent gcc to re-read the pagetables (Steve Best) [947166]
- [powerpc] mm: Make linux pagetable walk safe with THP enabled (Steve Best) [947166]
- [powerpc] thp: Add code to handle HPTE faults for hugepages (Steve Best) [947166]
- [powerpc] mm: Update gup_pmd_range to handle transparent hugepages (Steve Best) [947166]
- [powerpc] kvm: Handle transparent hugepage in KVM (Steve Best) [947166]
- [powerpc] mm: Replace find_linux_pte with find_linux_pte_or_hugepte (Steve Best) [947166]
- [powerpc] mm: Update find_linux_pte_or_hugepte to handle transparent hugepages (Steve Best) [947166]
- [powerpc] mm: move find_linux_pte_or_hugepte and gup_hugepte to common code (Steve Best) [947166]
- [powerpc] thp: Implement transparent hugepages for ppc64 (Steve Best) [947166]
- [powerpc] thp: Double the PMD table size for THP (Steve Best) [947166]
- [powerpc] mm: handle hugepage size correctly when invalidating hpte entries (Steve Best) [947166]
- [mm] thp: deposit the transpare huge pgtable before set_pmd (Steve Best) [947166]
- [mm] thp: don't use HPAGE_SHIFT in transparent hugepage code (Steve Best) [947166]
- [mm] thp: withdraw the pgtable after pmdp related operations (Steve Best) [947166]
- [mm] thp: add pmd args to pgtable deposit and withdraw APIs (Steve Best) [947166]
- [mm] thp: use the correct function when updating access flags (Steve Best) [947166]

* Fri Jul 26 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-3.el7]
- [powerpc] mm/numa: Do not update sysfs cpu registration from invalid context (Steve Best) [967447]
- [misc] MAINTAINERS: Add ACPI folks for ACPI-related things under drivers/pci (Myron Stowe) [984759]
- [pci] Add CircuitCo vendor ID and subsystem ID (Myron Stowe) [984759]
- [pci] Use pdev->pm_cap instead of pci_find_capability(.., PCI_CAP_ID_PM) (Myron Stowe) [984759]
- [pci] Return early on allocation failures to unindent mainline code (Myron Stowe) [984759]
- [pci] Simplify IOV implementation and fix reference count races (Myron Stowe) [984759]
- [pci] Drop redundant setting of bus->is_added in virtfn_add_bus() (Myron Stowe) [984759]
- [pci] pci-acpi: Use correct power state strings in messages (Myron Stowe) [984759]
- [pci] Fix comment typo for pcie_pme_remove() (Myron Stowe) [984759]
- [pci] Rename pci_release_bus_bridge_dev() to pci_release_host_bridge_dev() (Myron Stowe) [984759]
- [pci] Fix refcount issue in pci_create_root_bus() error recovery path (Myron Stowe) [984759]
- [pci] Convert alloc_pci_dev(void) to pci_alloc_dev(bus) (Myron Stowe) [984759]
- [pci] Hide remove and rescan sysfs interfaces for SR-IOV virtual functions (Myron Stowe) [984759]
- [pci] Add pcibios_release_device() (Myron Stowe) [984759]
- [iommu] irq_remapping: Conserve interrupt resources when using multiple-MSIs (Myron Stowe) [984759]
- [i2c] i2c-piix4: Add AMD CZ SMBus device ID (Myron Stowe) [984759]
- [ata] ahci: Add AMD CZ SATA device ID (Myron Stowe) [984759]
- [pci] Put Hudson-2 device IDs together (Myron Stowe) [984759]
- [pci] Replace strict_strtoul() with kstrtoul() (Myron Stowe) [984759]
- [pci] Finish SR-IOV VF setup before adding the device (Myron Stowe) [984759]
- [pci] Fix comment typo for PCI_EXP_LNKCAP_CLKPM (Myron Stowe) [984759]
- [acpi] pci_root: Use dev_printk(), acpi_handle_print(), pr_xxx() when possible (Myron Stowe) [984759]
- [acpi] pci_root: Remove unused global list acpi_pci_roots (Myron Stowe) [984759]
- [acpi] pci_root: Introduce "handle" local for economy of expression (Myron Stowe) [984759]
- [acpi] pci_root: Combine duplicate adjacent "if" tests (Myron Stowe) [984759]
- [pci] Allocate only as many MSI vectors as requested by driver (Myron Stowe) [984759]
- [pci] Replace printks with appropriate pr_*() (Myron Stowe) [984759]
- [pci] Fix kerneldoc for pci_disable_link_state() (Myron Stowe) [984759]
- [x86] pci: Increase info->res_num before checking pci_use_crs (Myron Stowe) [984759]
- [pci] Fix INTC comment typo for pci_swizzle_interrupt_pin() (Myron Stowe) [984759]
- [pci] Convert ioapic.c to module_pci_driver (Myron Stowe) [984759]
- [pci] Introduce pci_alloc_dev(struct pci_bus*) to replace alloc_pci_dev() (Myron Stowe) [984759]
- [pci] Introduce pci_bus_{get|put}() to manage PCI bus reference count (Myron Stowe) [984759]
- [pci] Unset resource if initial BAR value is invalid (Myron Stowe) [984759]
- [pci] Consolidate calls to pcibios_bus_to_resource() in __pci_read_base() (Myron Stowe) [984759]
- [pci] Add 0x prefix to BAR register position in __pci_read_base() (Myron Stowe) [984759]
- [pci] aspm: Warn when driver asks to disable ASPM, but we can't do it (Myron Stowe) [984759]
- [powerpc] pci: Use PCI_UNKNOWN for unknown power state (Myron Stowe) [984759]
- [acpi] pci_root: Check acpi_resource_to_address64() return value (Myron Stowe) [984759]
- [pci] Work around Ivytown NTB BAR size issue (Myron Stowe) [984759]
- [net] sunrpc: Fix another issue with rpc_client_register() (Jeff Layton) [924649]
- [net] sunrpc: Fix a deadlock in rpc_client_register() (Jeff Layton) [924649]
- [net] sunrpc: PipeFS MOUNT notification optimization for dying clients (Jeff Layton) [924649]
- [net] sunrpc: split client creation routine into setup and registration (Jeff Layton) [924649]
- [net] sunrpc: fix races on PipeFS UMOUNT notifications (Jeff Layton) [924649]
- [net] sunrpc: fix races on PipeFS MOUNT notifications (Jeff Layton) [924649]

* Fri Jul 19 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-2.el7]
- [scsi] sd: fix crash when UA received on DIF enabled device (Ewan Milne) [979440]
- [md] dm-cache: add call to mark_tech_preview (Mike Snitzer) [982752]
- [fs] nfs: have NFSv3 try server-specified auth flavors in turn (Jeff Layton) [977649]
- [fs] nfs: have nfs_mount fake up a auth_flavs list when the server didn't provide it (Jeff Layton) [977649]
- [fs] nfs: move server_authlist into nfs_try_mount_request (Jeff Layton) [977649]
- [fs] nfs: refactor "need_mount" code out of nfs_try_mount (Jeff Layton) [977649]
- [pci] ear: Reset link for devices below Root Port or Downstream Port (Myron Stowe) [797485]
- [acpi] apei: Force fatal AER severity when component has been reset (Myron Stowe) [797485]
- [pci] aer: Remove "extern" from function declarations (Myron Stowe) [797485]
- [pci] aer: Move AER severity defines to aer.h (Myron Stowe) [797485]
- [pci] aer: Set dev->__aer_firmware_first only for matching devices (Myron Stowe) [797485]
- [pci] aer: Factor out HEST device type matching (Myron Stowe) [797485]
- [pci] aer: Don't parse HEST table for non-PCIe devices (Myron Stowe) [797485]

* Tue Jul 09 2013 Jarod Wilson <jarod@redhat.com> [3.10.0-1.el7]
- [x86] fix !CONFIG_HYPERVISOR_GUEST compile (Andrew Jones)
- [s390x] crash: Fuzzy live dump for Linux on System z (Hendrik Brueckner) [805120]
- [xen] xenfv: fix hangs when kdumping (Andrew Jones) [845471]
- [libata] export ata_port port_no attribute via /sys (David Milburn) [951181]
- [s390x] kdump: Use 4 GiB for KEXEC_AUTO_THRESHOLD (Hendrik Brueckner) [953044]
- [x86] hpet: allow user controlled mmap for user processes (Prarit Bhargava) [788727]
- [mm] add memory tracking hooks (James Paradis) [725860]
- [kernel] clocksource, fix !CONFIG_CLOCKSOURCE_WATCHDOG compile (Prarit Bhargava) [914709]
- [x86] disable clocksource watchdog (Prarit Bhargava) [914709]
- [kdump] x86, fix kdump and unsupported HW check (Prarit Bhargava) [923256]
- [x86] support single cpu on guests only (Prarit Bhargava) [873806]
- [kernel] Mark power5, power6, !Intel, and !AMD systems as unsupported (Prarit Bhargava) [870129]
- [kernel] Backport RH specific TAINT flags (Prarit Bhargava) [870129]
- [s390x] zfcpdump: Add user space tool (Hendrik Brueckner) [825189]
- [kdump] crashkernel=auto fixes and cleanup (Dave Young) [804077]
- [fedora] /dev/crash driver (Kyle McMartin) [808839]
- [kdump] forward port crashkernel auto reservation code (Dave Young) [804077]
- [block] Change scheduler to CFQ for ATA/SATA (Vivek Goyal) [811016]
- [kernel] kbuild: AFTER_LINK (Roland McGrath)
- [ppc64] disable INFINIBAND_EHCA temporarily, it ftbfs (Kyle McMartin)
- [kernel] Add RHEL_{MAJOR,MINOR,RELEASE} to top level Makefile (Kyle McMartin)

* Mon Jun 03 2013 Kyle McMartin <kyle@redhat.com>
- Trimmed changelog for rhel7.git, see rhpkg git for earlier history.

###
# The following Emacs magic makes C-c C-e use UTC dates.
# Local Variables:
# rpm-change-log-uses-utc: t
# End:
###
