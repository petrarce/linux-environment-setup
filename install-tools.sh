#!/bin/bash

declare -a TOOLS_FROM_REPOSITORIES=(
	git 
	# sublime-text 
	tmux
	tree
	libnotify-bin
	curl
	strace
	#build tools
	cmake
	cmake-curses-gui 
	#boost dependences
	libboost-all-dev
	#Qt dependences
	libqt5core5a libqt5gui5
	#heaptrack dependences
	libunwind-dev
	mesa-common-dev 
	libglu1-mesa-dev
	libzstd-dev
	extra-cmake-modules
	libkchart-dev
	#libkf5 for heaptrack
	libkf5coreaddons-dev 
	libkf5i18n-dev 
	libkf5itemmodels-dev 
	libkf5threadweaver-dev 
	libkf5configwidgets-dev 
	libkf5kio-dev
	#gettext for kf5
	gettext

	# sound
	pavucontrol-qt
	software-properties-common
)

declare -a TOOLS_FROM_SOURCE=(
	#heaptrack

)


function buildTool(){
	local toolName="${1}"
	local gitRepoPath="${2}"
	local revision="${3}"

	git clone "${gitRepoPath}" "${toolName}"
	pushd "${toolName}"

	mkdir build
	cmake \
		-B "${PWD}/build" \
		-S "${PWD}" \
		-DCMAKE_INSTALL_PREFIX="${InstallPathPrefix_DIR}" \
		-DQt5_DIR="${QtInstallation_DIR}" \

	popd

	popd
}

QtInstallation_DIR=""
InstallPathPrefix_DIR="${HOME}/utils"


set -x
VAR_ARGS=$(getopt -o q:i: -l qt-dir:install-path-prefix: -- "$@")
eval ${VAR_ARGS}

while true; do
	case "$1" in
		-q | --qt-dir) 
			QtInstallation_DIR="$(realpath $2)"; shift 2;;
		-i | --install-path-prefix)
			InstallPathPrefix_DIR="$2"; shift 2;; 
		*) break;;
	esac
done

sudo apt-get install ${TOOLS_FROM_REPOSITORIES[@]}
