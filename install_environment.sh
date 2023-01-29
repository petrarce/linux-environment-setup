#!/bin/bash
# This scripts creates symlincs in ${HOME}
# to files, that reside in the envirenment/
# directory. In case if link in ${HOME} already
# ecists it rewrites the link with force operation
# otherwice backup of current file is created with 
# timestamp

set -x

DATE=`date +%Y-%m-%d_%H-%M-%S`
for file in environment/*; do
	newFile="${HOME}/.`basename ${file}`"
	test -L ${newFile}
	if [ "$?" == "1" ]; then
		cp ${newFile} ${newFile}.${DATE}.bkp
	fi
	ln -sf  `pwd`/${file} ${newFile}
done
set +x