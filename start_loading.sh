#!/usr/bin/env bash

EXE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/generateVirtualSequence/build"
cd ${EXE_DIR}

SEQU_FOLDER_PRE="/app/data/"
IMG_FOLDER_PRE="/app/images/"
OPTS=""

SKIP_NEXT=0
for (( i = 1; i <= "$#"; i++ )); do
  if [ "${SKIP_NEXT}" -eq 1 ]; then
    SKIP_NEXT=0
  elif [ "${!i}" == "--sequPath" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'sequence folder name' after --sequPath required"
      exit 1
    fi
    SEQU_VAL="${SEQU_FOLDER_PRE}${!i2}"
    if [ ! -d ${SEQU_VAL} ]; then
      echo "Directory ${SEQU_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --sequPath ${SEQU_VAL}"
    SKIP_NEXT=1
  elif [ "${!i}" == "--matchPath" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument '[sequence folder name]/[matches folder name]' after --matchPath required"
      exit 1
    fi
    SEQU_VAL="${SEQU_FOLDER_PRE}${!i2}"
    if [ ! -d ${SEQU_VAL} ]; then
      echo "Directory ${SEQU_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --matchPath ${SEQU_VAL}"
    SKIP_NEXT=1
  elif [ "${!i}" == "--file" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'file name of matches' after --file required"
      exit 1
    fi
    SEQU_VAL="${SEQU_FOLDER_PRE}${!i2}"
    if [ ! -f ${SEQU_VAL} ]; then
      echo "File ${SEQU_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --file ${SEQU_VAL}"
    SKIP_NEXT=1
  elif [ "${!i}" == "--fileRt" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'file name of 3D data' after --fileRt required"
      exit 1
    fi
    SEQU_VAL="${SEQU_FOLDER_PRE}${!i2}"
    if [ ! -f ${SEQU_VAL} ]; then
      echo "File ${SEQU_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --fileRt ${SEQU_VAL}"
    SKIP_NEXT=1
  elif [ "${!i}" == "--gtm_file" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'GTM file name' after --gtm_file required"
      exit 1
    fi
    SEQU_VAL="${IMG_FOLDER_PRE}${!i2}"
    if [ ! -f ${SEQU_VAL} ]; then
      echo "File ${SEQU_VAL} does not exist"
      exit 1
    fi
    OPTS="${OPTS} --gtm_file ${SEQU_VAL}"
    SKIP_NEXT=1
  else
    OPTS="${OPTS} ${!i}"
  fi
done

./loadData "${OPTS}"
