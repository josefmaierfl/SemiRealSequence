#!/bin/bash

root_dir=`pwd`
virtsequ_dir=${root_dir}/generateVirtualSequence
build_dir=${virtsequ_dir}/build

BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=OFF"
BUILD_GTM_INTERFACE="-DENABLE_GTM_INTERFACE=ON"
BUILD_EXAMPLES="-DOPTION_BUILD_EXAMPLES=ON"
BUILD_TESTS="-DOPTION_BUILD_TESTS=ON"
BUILD_CMD_INTERFACE="-DENABLE_CMD_INTERFACE=ON"
BUILD_SHARED_LIBS="-DBUILD_SHARED_LIBS=ON"
ANNOTATE_INSTALL=0
if [ $# -ne 0 ]; then
  for (( i = 1; i <= "$#"; i++ )); do
    if [ "${!i}" == "annotate" ]; then
      BUILD_ANNOTATION="-DUSE_MANUAL_ANNOTATION=ON"
      ANNOTATE_INSTALL="$((${ANNOTATE_INSTALL} + 1))"
    elif [ "${!i}" == "install" ]; then
      BUILD_EXAMPLES="-DOPTION_BUILD_EXAMPLES=OFF"
      BUILD_TESTS="-DOPTION_BUILD_TESTS=OFF"
      BUILD_CMD_INTERFACE="-DENABLE_CMD_INTERFACE=OFF"
      BUILD_SHARED_LIBS="-DBUILD_SHARED_LIBS=OFF"
      ANNOTATE_INSTALL="$((${ANNOTATE_INSTALL} + 2))"
    fi
  done
fi

if [ ${ANNOTATE_INSTALL} -eq 2 ]; then
  BUILD_GTM_INTERFACE="-DENABLE_GTM_INTERFACE=OFF"
fi

# Build project generateVirtualSequence
mkdir ${build_dir}
cd ${build_dir}
cmake ../ -DCMAKE_BUILD_TYPE=Release ${BUILD_ANNOTATION} ${BUILD_GTM_INTERFACE} ${BUILD_TESTS} ${BUILD_EXAMPLES} ${BUILD_CMD_INTERFACE} ${BUILD_SHARED_LIBS}
if [ $? -ne 0 ]; then
    exit 1
fi
make -j "$(nproc)"
if [ $? -ne 0 ]; then
    exit 1
fi
if [ ${ANNOTATE_INSTALL} -ge 2 ]; then
  make install
  if [ $? -ne 0 ]; then
      exit 1
  fi
fi
