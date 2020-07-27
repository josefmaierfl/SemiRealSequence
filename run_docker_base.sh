#!/bin/bash

MAIN_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ ! -d ${RES_SV_DIR} ]; then
  mkdir ${RES_SV_DIR}
fi

if [ $# -eq 0 ]; then
  echo "Arguments are required"
  exit 1
fi
FIRST_ARG="$1"
if [ "${FIRST_ARG}" == "shutdown" ]; then
  echo "Shutting down after calculations finished"
elif [ "${FIRST_ARG}" == "live" ]; then
  echo "Keeping system alive after calculations finished"
else
  echo "First argument must be shutdown or live"
  exit 1
fi
shift 1

IMG_PATH_SYS="${MAIN_DIR}/images"
IMG_PATH_DOCKER="/app/images"

DATA_PATH_SYS="${MAIN_DIR}/data"
DATA_PATH_DOCKER="/app/data"

CONFIG_PATH_SYS="${MAIN_DIR}/config"
CONFIG_PATH_DOCKER="/app/config"

EXE_SEQUENCE="/app/start_SemiRealSequence.sh"
EXE_GTM="/app/start_gen_GTM.sh"
EXE_TEST="/app/start_test.sh"
EXE_LOAD="/app/start_loading.sh"
EXE_USE="${EXE_SEQUENCE}"

NR_ARGS=0
for (( i = 1; i <= "$#"; i++ )); do
  if [ "${!i}" == "EXE" ]; then
    i2="$((${i} + 1))"
    EXE_VAL="${!i2}"
    if [ "${EXE_VAL}" == "gtm" ]; then
      echo "Starting Docker to calculate or annotate GTM"
      EXE_USE="${EXE_GTM}"
    elif [ "${EXE_VAL}" == "test" ]; then
      echo "Starting Docker to test SemiRealSequence"
      EXE_USE="${EXE_TEST}"
    elif [ "${EXE_VAL}" == "load" ]; then
      echo "Starting Docker to load generated sequence, GTM, or annotation data"
      EXE_USE="${EXE_LOAD}"
    elif [ "${EXE_VAL}" == "sequence" ]; then
      echo "Starting Docker to generate new sequences"
    else
      echo "Unknown argument ${EXE_VAL} following argument EXE"
      exit 1
    fi
    NR_ARGS="$((${NR_ARGS} + 2))"
  elif [ "${!i}" == "IMGPATH" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'image path' after IMGPATH required"
      exit 1
    fi
    IMG_VAL="${!i2}"
    if [ ! -d ${IMG_VAL} ]; then
      echo "Path ${IMG_VAL} does not exist"
      exit 1
    fi
    IMG_PATH_SYS="${IMG_VAL}"
    NR_ARGS="$((${NR_ARGS} + 2))"
  elif [ "${!i}" == "DATAPATH" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'data path' after DATAPATH required"
      exit 1
    fi
    DATA_VAL="${!i2}"
    if [ ! -d ${DATA_VAL} ]; then
      echo "Path ${DATA_VAL} does not exist"
      exit 1
    fi
    DATA_PATH_SYS="${DATA_VAL}"
    NR_ARGS="$((${NR_ARGS} + 2))"
  elif [ "${!i}" == "CONFIGPATH" ]; then
    i2="$((${i} + 1))"
    if [ $# -lt "${i2}" ]; then
      echo "Argument 'configuration files path' after CONFIGPATH required"
      exit 1
    fi
    CONFIG_VAL="${!i2}"
    if [ ! -d ${CONFIG_VAL} ]; then
      echo "Path ${CONFIG_VAL} does not exist"
      exit 1
    fi
    CONFIG_PATH_SYS="${CONFIG_VAL}"
    NR_ARGS="$((${NR_ARGS} + 2))"
  fi
done

if [ "${NR_ARGS}" -gt 0 ]; then
  shift ${NR_ARGS}
fi

if [ ! -d ${DATA_PATH_SYS} ]; then
  mkdir ${DATA_PATH_SYS}
fi

if [ ! -d ${CONFIG_PATH_SYS} ]; then
  mkdir ${CONFIG_PATH_SYS}
fi

# -c $(echo "${@:2}")
xhost +local:root
#docker run -v ${IMG_PATH_SYS}:${IMG_PATH_DOCKER}:ro -v ${DATA_PATH_SYS}:${DATA_PATH_DOCKER} -v ${CONFIG_PATH_SYS}:${CONFIG_PATH_DOCKER} -it -v /tmp/.X11-unix/:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY SemiRealSequence:1.0 /bin/bash
docker run -v ${IMG_PATH_SYS}:${IMG_PATH_DOCKER}:ro -v ${DATA_PATH_SYS}:${DATA_PATH_DOCKER} -v ${CONFIG_PATH_SYS}:${CONFIG_PATH_DOCKER} -it -v /tmp/.X11-unix/:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY SemiRealSequence:1.0 ${EXE_USE} "$@"
xhost -local:root

# Shut down if asked for
if [ "${FIRST_ARG}" == "shutdown" ]; then
    echo "Shutting down"
    sudo shutdown -h now
fi
