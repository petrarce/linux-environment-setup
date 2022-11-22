#!/bin/bash

set -e
set -x

TARGET_DIR=${HOME}
CURRENT_DATE=`date +%Y-%m-%d-%H:%M:%S`
LOCAL_DIR=`pwd`

if [ -d "${1}" ]; then
	TARGET_DIR=${1}
fi

if [ -d ${TARGET_DIR}/environment ]; then
	mv ${TARGET_DIR}/environment ${TARGET_DIR}/environment.${CURRENT_DATE}.old
fi
install -d ${TARGET_DIR}/environment
install -m 700 ${LOCAL_DIR}/environment/* ${TARGET_DIR}/environment


for CONFIG_FILE_PATH in environment/*; do

	CONFIG_FILE=`basename ${CONFIG_FILE_PATH}`
	pushd ${TARGET_DIR}
	pwd
	if [ -f  .${CONFIG_FILE} ]; then
		mv .${CONFIG_FILE} .${CONFIG_FILE}.${CURRENT_DATE}.old
	fi
	ln -sf ${TARGET_DIR}/environment/${CONFIG_FILE}  .${CONFIG_FILE}
	popd

done

set +x