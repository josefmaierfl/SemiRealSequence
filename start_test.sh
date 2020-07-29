#!/usr/bin/env bash

EXE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/generateVirtualSequence/build"
cd ${EXE_DIR}

IMG_PREF=("--img_pref" "/")
OPTS=("--img_path" "/app/images" "--store_path" "/app/data")

IMG_PREF_FOUND=0
for (( i = 1; i <= "$#"; i++ )); do
  if [ "${!i}" == "--img_pref" ]; then
    IMG_PREF_FOUND=1
  fi
done

if [ "${IMG_PREF_FOUND}" -eq 0 ]; then
  OPTS+=("${IMG_PREF[@]}")
fi

if [ $# -ne 0 ]; then
  OPTS+=("$@")
fi

./generateVirtualSequenceLib-test ${OPTS[@]}
