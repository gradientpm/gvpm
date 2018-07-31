# Tested only on Windows and Linux (Ubuntu 10.10)
cmake_minimum_required(VERSION 2.8.3 FATAL_ERROR)
include(GenerateExportHeader)

# Call the FindBoost module again to set up the components. At this point it is
# assumed that the call will succeed
find_package(PythonLibs REQUIRED)

FIND_PACKAGE(Boost 1.61.0 REQUIRED)
IF(Boost_FOUND)
	SET(Boost_USE_STATIC_LIBS OFF)
	SET(Boost_USE_MULTITHREADED ON)
	SET(Boost_USE_STATIC_RUNTIME OFF)
	FIND_PACKAGE(Boost 1.61.0 COMPONENTS python)
ENDIF()

include_directories(
  ${PYTHON_INCLUDE_PATH} 
  ${Boost_INCLUDE_DIRS}
)
link_directories(
  ${Boost_LIBRARY_DIRS}
)

# Add openmp for the //
find_package(OpenMP)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
endif()

# Building library
add_library (io SHARED sources/io.cpp)
target_link_libraries (io
  ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
set_target_properties (io PROPERTIES OUTPUT_NAME io PREFIX "")
install(TARGETS io
  RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime
  LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime
  ARCHIVE DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime)

add_library (fast SHARED sources/fast.cpp)
target_link_libraries (fast
  ${Boost_LIBRARIES} ${PYTHON_LIBRARIES})
set_target_properties (fast PROPERTIES OUTPUT_NAME fast PREFIX "")
install(TARGETS fast
  RUNTIME DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime
  LIBRARY DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime
  ARCHIVE DESTINATION ${CMAKE_SOURCE_DIR}/rgbe/ COMPONENT Runtime)
  

  
  
