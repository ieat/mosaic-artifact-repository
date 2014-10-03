#!/bin/bash

ARCH=`uname -s`
DIR=

if [ $ARCH == "Linux" ]; then
   DIR=`readlink -f "$( dirname "$0" )"`
elif [ $ARCH == "Darwin" ]; then
   CMD="import os, sys; print os.path.realpath(\"$( dirname $0 )\")"
   DIR=`python -c "$CMD"`
fi

. $DIR/bin/activate
python $DIR/runtime/artifact-repository.py