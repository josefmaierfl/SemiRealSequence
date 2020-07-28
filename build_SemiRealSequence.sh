#!/bin/bash

root_dir=`pwd`
virtsequ_dir=${root_dir}/generateVirtualSequence
build_dir=${virtsequ_dir}/build

BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=OFF"
if [ $# -ne 0 ]; then
  if [ "$1" == "annotate" ]; then
    BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=ON"
  fi
fi

# Build project generateVirtualSequence
mkdir ${build_dir}
cd ${build_dir}
cmake ../ -DCMAKE_BUILD_TYPE=Release ${BUILD_ANNOTATION}
if [ $? -ne 0 ]; then
    exit 1
fi
make -j "$(nproc)"
if [ $? -ne 0 ]; then
    exit 1
fi
