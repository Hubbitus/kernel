#! /bin/sh
# This script was created in a effort to make patch management a bit easier.
# It list all the patches in the current tree and identifies if they are
# present in the kernel.spec, PatchList.txt, both files or neither.
#
# eg. ./check-patchlist.sh [optional flag]

function usage(){
    echo "List all the patches currently in the tree. It also helps identify"
    echo "if the patch is present in kernel.spec or PatchList.txt.          "
    echo "-h, --help                                                        "
    echo "-t, --tracked       patches in both kernel.spec and PatchList.txt "
    echo "-p, --patchlist     patches added to PatchList.txt.               "
    echo "-s, --specfile      patches added to kernel.spec.                 "
    echo "-n, --not-tracked   patches in the tree but not  in PatchList.txt "
    echo "                     or kernel.spec                               "
}

BASEDIR=$(dirname "$( cd $(dirname $BASH_SOURCE[0]) && pwd)")
pushd $BASEDIR > /dev/null

function list_all(){
    echo "===========Legend==========================="
    echo ".   In kernel.spec                          "
    echo "*   In PatchList.txt                        "
    echo "+   In PatchList.txt & Kernel.spec          "
    echo "-   Neither in PatchList.txt nor kernel.spec"
    echo "============================================"
    for patch in $(ls *.patch); do
	if [ ! -z "$(grep $patch PatchList.txt)" ] && [ ! -z "$(grep $patch kernel.spec)" ]
	then
	    echo "+ ${patch}" # Patches in kernel.spec and PatchList.txt

	elif [ ! -z "$(grep $patch PatchList.txt)" ] && [ -z "$(grep $patch kernel.spec)" ]
	then
	     echo "* ${patch}" # Patches in PatchList.txt but not in kernel.spec

	elif [ -z "$(grep $patch PatchList.txt)" ] && [ ! -z "$(grep $patch kernel.spec)" ]
	then
	    echo ". ${patch}" # Patches in kernel.spec but not in PatchList.txt

	else
	    echo "- ${patch}" # Neither in PatchList.txt nor kernel.spec

	fi
    done
}

function list_present_not_added(){
    for patch in $(ls *.patch); do
	if [ -z "$(grep $patch PatchList.txt)" ] && [ -z "$(grep $patch kernel.spec)" ]
	then
	    echo $patch
	fi
    done
}

function list_present_added(){
    for patch in $(ls *.patch); do
	if [ ! -z "$(grep $patch PatchList.txt)" ] && [ ! -z "$(grep $patch kernel.spec)" ]
	then
	    echo $patch
	fi
    done
}

function list_patchList(){
    for patch in $(ls *.patch); do
	if [ ! -z "$(grep $patch PatchList.txt)" ] && [ -z "$(grep $patch kernel.spec)" ]
	then
	    echo $patch
	fi
    done

}
function list_specfile(){
    for patch in $(ls *.patch); do
	if [ -z "$(grep $patch PatchList.txt)" ] && [ ! -z "$(grep $patch kernel.spec)" ]
	then
	    echo $patch
	fi
    done
}

if [ -z "$@" ]; then
    list_all
else

    for opt in "$@"; do
	case $opt in
	    -t|--tracked)
		list_present_added
		;;
	    -s|--specfile)
		list_specfile
		;;
	    -h|--help)
		usage
		;;
	    -n|--not-added)
		list_present_not_added
		;;
	    -p|--patchlist)
		list_patchList
		;;
	    *)
		usage
		;;
	esac
    done
fi

popd > /dev/null
