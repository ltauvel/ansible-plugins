#!/bin/bash

# Get current file path
if uname | grep -iq 'darwin'; then
  BASE_DIR=$(cd $(dirname $(stat -f ${BASH_SOURCE:-$0})); PWD)
else
  BASE_DIR=$(dirname $(readlink -f ${BASH_SOURCE:-$0}))
fi


if [ -f $BASE_DIR/install.yml ]; then
  YML_PATH=$BASE_DIR/install.yml
fi

ansible-playbook $YML_PATH