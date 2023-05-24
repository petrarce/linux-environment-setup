#!/bin/bash
# This scripts creates symlincs in ${HOME}
# to files, that reside in the envirenment/
# directory. In case if link in ${HOME} already
# ecists it rewrites the link with force operation
# otherwice backup of current file is created with 
# timestamp

function updateFile() {
	local source="${1}"
	local destination="${2}"

	if [ ! -f "${source}" ]; then
		echo "ERRIR: Cannot update ${destination}: ${source} doesnt exist." 1>&2
	fi 

	if [ -f "${destination}" ]; then
		echo "update  ${destination} with ${source}"
		cp -L "${destination}" "${destination}$(date).bkp"
		echo "Backed up ${destination} at ${destination}$(date).bkp"
	fi
	ln -sf "${source}" "${destination}"
}

VAR_ARGS=$(getopt -o o: -l output-dir: -- "$@")
echo "${VAR_ARGS}"
eval set -- "${VAR_ARGS}"

OUTPUT_DIR=$(realpath "${HOME}")
while true; do
	case "$1" in
		-o | --output-dir) OUTPUT_DIR=$(realpath "$2"); shift 2;;
		*) break;;
	esac
done

if [ ! -d "${OUTPUT_DIR}" ]; then
	echo "Output directory doesn't exist" 1>&2
fi 

while IFS= read -r -d '' file; do 
	updateFile $(realpath "${file}") $(echo "${file}" | sed -e "s,^.*environment,"${OUTPUT_DIR}",g");
done <	<(find "${PWD}/environment/" -type f -print0)
