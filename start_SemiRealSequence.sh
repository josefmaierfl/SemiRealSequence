#!/usr/bin/env bash

EXE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/generateVirtualSequence/build"
cd ${EXE_DIR}

IMG_PREF="--img_pref /"
CONF_FILE_PRE="/app/config/"
OPTS="--img_path /app/images --store_path /app/data"

IMG_PREF_FOUND=0
SKIP_NEXT=0
for (( i = 1; i <= "$#"; i++ )); do
  if [ "${SKIP_NEXT}" -eq 1 ]; then
    SKIP_NEXT=0
  elif [ "${!i}" == "--img_pref" ]; then
    IMG_PREF_FOUND=1
    OPTS="${OPTS} --img_pref"
  elif [ "${!i}" == "--conf_file" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'configuration file name' after --conf_file required"
      exit 1
    fi
    CONF_VAL="${CONF_FILE_PRE}${!i2}"
    if [ ! -f ${CONF_VAL} ]; then
      echo "File ${CONF_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --conf_file ${CONF_VAL}"
    SKIP_NEXT=1
  else
    OPTS="${OPTS} ${!i}"
  fi
done

if [ "${IMG_PREF_FOUND}" -eq 0 ]; then
  OPTS="${OPTS} ${IMG_PREF}"
fi

./virtualSequenceLib-CMD-interface "${OPTS}"
