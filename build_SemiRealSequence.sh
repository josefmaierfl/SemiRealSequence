#!/bin/bash

root_dir=`pwd`
virtsequ_dir=${root_dir}/generateVirtualSequence
build_dir=${virtsequ_dir}/build

BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=OFF"
BUILD_GTM_INTERFACE="-DENABLE_GTM_INTERFACE=OFF"
if [ $# -ne 0 ]; then
  if [ "$1" == "annotate" ]; then
    BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=ON"
    BUILD_GTM_INTERFACE="-DENABLE_GTM_INTERFACE=ON"
  fi
fi

# Build project generateVirtualSequence
mkdir ${build_dir}
cd ${build_dir}
cmake ../ -DCMAKE_BUILD_TYPE=Release ${BUILD_ANNOTATION} -DOPTION_BUILD_TESTS=OFF -DOPTION_BUILD_EXAMPLES=OFF -DENABLE_CMD_INTERFACE=OFF ${BUILD_GTM_INTERFACE} -DBUILD_SHARED_LIBS=OFF
if [ $? -ne 0 ]; then
    exit 1
fi
make -j "$(nproc)"
if [ $? -ne 0 ]; then
    exit 1
fi
