#!/bin/bash
# This scripts creates symlincs in ${HOME}
# to files, that reside in the envirenment/
# directory. In case if link in ${HOME} already
# ecists it rewrites the link with force operation
# otherwice backup of current file is created with 
# timestamp
set -e

function print_usage() {
  echo " -i, --install       -    if set the deb packages constructed by the app will be installed systemwide."
  echo " -h, --help          -    print this message"

}


VAR_ARGS=$(getopt -o "o:inh" -l "output-dir:install,no-backup,help" -- "$@")
if [ "$?" != "0" ]; then
  print_usage
  exit 1
fi
eval set -- "${VAR_ARGS}"

INSTALL_SYSTEMWIDE="false"
while true; do
	case "$1" in
    -i | --install) INSTALL_SYSTEMWIDE="true"; shift 1;;
    -h | --help) print_usage; exit 1;;
		*) break;;
	esac
done


# build deb packages and install them on the local system
cmake -B /tmp/build-pkgs . && cmake --build /tmp/build-pkgs && cmake --install /tmp/build-pkgs --prefix /tmp/build-pkgs/install
INSTALL_CMD="deb-local"
if [ "${INSTALL_SYSTEMWIDE}" == "true" ]; then
  INSTALL_CMD="sudo apt-get"
fi
for i in /tmp/build-pkgs/install/*.deb; do
  ${INSTALL_CMD} install $i
done
