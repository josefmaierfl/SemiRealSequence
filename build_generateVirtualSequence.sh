#!/bin/bash

root_dir=`pwd`
virtsequ_dir=${root_dir}/generateVirtualSequence
build_dir=${virtsequ_dir}/build

BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=OFF"
if [ $# -ne 0 ]; then
  if [ "$1" -eq 1 ]; then
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
make install

copy_dir0=${root_dir}/tmp/generateVirtualSequence
copy_dir=${copy_dir0}/build
mkdir -p ${copy_dir}
find ${build_dir} -type f \( -executable -o -name \*.so \) -exec cp {} ${copy_dir} \;
cp ${virtsequ_dir}/downloadImageNet.py ${copy_dir0}
