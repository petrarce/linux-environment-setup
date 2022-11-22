#!/bin/bash

set -e
set -x
TARGET_DIR=${HOME}

LOCALDIR=`pwd`

for CONFIG_FILE_PATH in environment/*; do

	FONCIF_FILE=`basename ${CONFIG_FILE_PATH}`
	pushd ${TARGET_DIR}
	pwd
	if [ -f  .${FONCIF_FILE} ]; then
		mv .${FONCIF_FILE} .${FONCIF_FILE}.old
	fi
	ln -sf ${LOCALDIR}/${CONFIG_FILE_PATH}  .${FONCIF_FILE}
	popd

done

set +x