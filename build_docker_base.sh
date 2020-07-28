#!/usr/bin/env bash

BUILD_ANNOTATION=0
if [ $# -ne 0 ]; then
  if [ "$1" == "annotate" ]; then
    BUILD_ANNOTATION=1
  fi
fi
export BUILD_ANNOTATION

docker image build --build-arg BUILD_ANNOTATION -t semi_real_sequence:1.0 `pwd`
