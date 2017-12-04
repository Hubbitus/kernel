# Makefile for source rpm: kernel
SPECFILE := kernel.spec

# we only check the .sign signatures
UPSTREAM_CHECKS = sign

.PHONY: help
help:
%:
	@echo "Try fedpkg $@ or something like that"
	@exit 1

prep: config-files
	fedpkg -v prep

noarch:
	fedpkg -v local --arch=noarch

# 'make local' also needs to build the noarch firmware package
local:
	fedpkg -v local

extremedebug:
	@perl -pi -e 's/# CONFIG_DEBUG_PAGEALLOC is not set/CONFIG_DEBUG_PAGEALLOC=y/' config-nodebug

config-files:
	@./build_configs.sh

debug:
	@perl -pi -e 's/^%define debugbuildsenabled 1/%define debugbuildsenabled 0/' kernel.spec
	@rpmdev-bumpspec -c "Reenable debugging options." kernel.spec

release:
	@perl -pi -e 's/^%define debugbuildsenabled 0/%define debugbuildsenabled 1/' kernel.spec
	@rpmdev-bumpspec -c "Disable debugging options." kernel.spec

nodebuginfo:
	@perl -pi -e 's/^%define with_debuginfo %\{\?_without_debuginfo: 0\} %\{\?\!_without_debuginfo: 1\}/%define with_debuginfo %\{\?_without_debuginfo: 0\} %\{\?\!_without_debuginfo: 0\}/' kernel.spec

nodebug: release
	@perl -pi -e 's/^%define debugbuildsenabled 1/%define debugbuildsenabled 0/' kernel.spec

ifeq ($(MAKECMDGOALS),me a sandwich)
.PHONY: me a sandwich
me a:
	@:

sandwich:
	@[ `id -u` -ne 0 ] && echo "What? Make it yourself." || echo Okay.
endif
