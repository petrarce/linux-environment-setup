#!/bin/bash
# This scripts creates symlincs in ${HOME}
# to files, that reside in the envirenment/
# directory. In case if link in ${HOME} already
# ecists it rewrites the link with force operation
# otherwice backup of current file is created with 
# timestamp
set -e
function updateFile() {
	local source="${1}"
	local destination="${2}"

	if [ ! -f "${source}" ]; then
		echo "ERRIR: Cannot update ${destination}: ${source} doesnt exist." 1>&2
	fi 

	if [ -f "${destination}" ] && [ "${NO_BACKUP}" == "1" ]; then
		cp -L "${destination}" "${destination}_$(date +%H-%M-%S_%y-%m-%d).bkp"
		echo "Backed up ${destination} at ${destination}$(date).bkp"
	fi
	echo "update  ${destination} with ${source}"
	if [ ! -d "$(dirname \"${destination}\")" ]; then
		mkdir -p "$(dirname ${destination})"
	fi
	ln -sf "${source}" "${destination}"
}

function print_usage() {
  echo " -o, --output-dir    -    target directory wgere symlinks should be created"
  echo " -n, --no-backup     -    do not create the backup of previous version of the file, whic is going to be substituted"
  echo " -h, --help          -    print this message"

}


VAR_ARGS=$(getopt -o o:nh -l output-dir:no-backup,help -- "$@")
if [ "$?" != "0" ]; then
  print_usage
  exit 1
fi
eval set -- "${VAR_ARGS}"

OUTPUT_DIR=$(realpath "${HOME}")
NO_BACKUP="1"
while true; do
	case "$1" in
		-o | --output-dir) OUTPUT_DIR=$(realpath "$2"); shift 2;;
		-n | --no-baskup) NO_BACKUP="0"; shift 1;;
    -h | --help) print_usage; exit 1;;
		*) break;;
	esac
done

if [ ! -d "${OUTPUT_DIR}" ]; then
	echo "Output directory doesn't exist" 1>&2
fi 

while IFS= read -r -d '' file; do 
	updateFile $(realpath "${file}") $(echo "${file}" | sed -e "s,^.*environment,"${OUTPUT_DIR}",g");
done <	<(find "${PWD}/environment/" -type f -print0)

# build deb packages and install them on the local system
cmake -B /tmp/build-pkgs . && cmake --build /tmp/build-pkgs && cmake --install /tmp/build-pkgs --prefix /tmp/build-pkgs/install
for i in /tmp/build-pkgs/install/*.deb; do
  deb-local install $i
done
