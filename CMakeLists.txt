cmake_minimum_required(VERSION 3.0)
project(go_ai)

include(conanbuildinfo.cmake)
conan_basic_setup()

set(CMAKE_CXX_STANDARD 11)

set(SCORE_ESTIMATOR_SOURCE_FILES
        score-estimator/estimator.cc
        src/scoring/go_estimator.cpp)

set(SCORE_ESTIMATOR_INCLUDES
        score-estimator/estimator.h
        src/scoring/go_estimator.h)

add_library(go_scoring SHARED ${SCORE_ESTIMATOR_SOURCE_FILES})
