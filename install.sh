#!/bin/bash

mkdir -p build && cd build
cmake ..
make
cp libgo_scoring.so ..
cd ..
