cmake_minimum_required(VERSION 3.6)
project(go_ai)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        src/cpp/main.cpp
        src/references/gym_example.py
        src/references/qlearn.py
        src/references/test.py
        src/scoring/data.py
        src/scoring/scoring.py
        src/ai.py
        src/main.py)

add_executable(go_ai ${SOURCE_FILES})