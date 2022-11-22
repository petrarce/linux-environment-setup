#!/bin/bash

TARGET_DIR=/tmp

for i in environment/*; do 
	echo $i; 
	if [ -f  /tmp/.$i ]; then
		mv /tmp/.$i /tmp/.$i.old
		ln -s ${PWD}/environment/$i  ${TARGET_DIR}/.$i
	fi
done