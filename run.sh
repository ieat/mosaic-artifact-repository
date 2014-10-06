#!/bin/bash
# Copyright 2014, Institute e-Austria, Timisoara, Romania
#    http://www.ieat.ro/
# Developers:
#  * Silviu Panica, silviu.panica@e-uvt.ro
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


ARCH=`uname -s`
DIR=

if [ $ARCH == "Linux" ]; then
   DIR=`readlink -f "$( dirname "$0" )"`
elif [ $ARCH == "Darwin" ]; then
   CMD="import os, sys; print os.path.realpath(\"$( dirname $0 )\")"
   DIR=`python -c "$CMD"`
fi

_python_bin=`find $DIR -name python | grep bin/python$ | tail -1`

${_python_bin} $DIR/runtime/artifact-repository.py
