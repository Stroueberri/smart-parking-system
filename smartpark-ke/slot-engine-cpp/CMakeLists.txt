cmake_minimum_required(VERSION 3.16)
project(SmartParkSlotEngine VERSION 2.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Source files
set(SOURCES
    src/MinHeap.cpp
    src/Graph.cpp
    src/DoublyLinkedList.cpp
    src/BarrierStateMachine.cpp
)

# Main microservice executable
add_executable(slot_engine src/main.cpp ${SOURCES})

# Windows socket library link
if(WIN32)
    target_link_libraries(slot_engine PRIVATE ws2_32)
endif()

# Unit test executable
add_executable(test_slot_engine tests/test_slot_engine.cpp ${SOURCES})
if(WIN32)
    target_link_libraries(test_slot_engine PRIVATE ws2_32)
endif()

enable_testing()
add_test(NAME SlotEngineUnitTests COMMAND test_slot_engine)
