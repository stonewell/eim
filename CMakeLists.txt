CMAKE_MINIMUM_REQUIRED(VERSION 3.30)

CMAKE_POLICY(
  SET CMP0048 NEW
)
CMAKE_POLICY(
  SET CMP0058 NEW
)

PROJECT (eim
  VERSION 1.0.0
)

INCLUDE(ExternalProject)

OPTION(ENABLE_TESTS "Enable tests" OFF)
if (${ENABLE_TESTS})
  enable_testing()
endif()

IF(APPLE)
  SET(CMAKE_MACOSX_RPATH 1)
  SET(CMAKE_PREFIX_PATH /usr/local)
ENDIF()

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE "DEBUG")
  #SET(CMAKE_BUILD_TYPE "RELEASE")
  #SET(CMAKE_BUILD_TYPE "RELWITHDEBINFO")
  #SET(CMAKE_BUILD_TYPE "MINSIZEREL")
ENDIF()

SET(CMAKE_EXPORT_COMPILE_COMMANDS ON)

SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_CURRENT_SOURCE_DIR}/cmake/Modules/")

if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  set(warnings -Wall -Wextra -Werror -Wno-cast-function-type -Wno-ignored-qualifiers)
  set(no_undefined -Wl,--no-undefined)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
  set(warnings -Wall -Wextra -Werror -Wno-inconsistent-missing-override)
  set(no_undefined -Wl,-undefined,error)
elseif ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
  set(warnings /W4 /WX /EHsc)
  set(no_undefined "")
endif()

SET(CXX_STANDARD_REQUIRED ON)
SET(CXX_EXTENSION NO)

SET(PROJECT_C_FLAGS -fPIC ${warnings}
    CACHE STRING "Flags used by the compiler during all build types." FORCE)
SET(PROJECT_CXX_FLAGS -fPIC ${warnings} -std=c++20
    CACHE STRING "Flags used by the compiler during all build types." FORCE)
SET(PROJECT_LINK_FLAGS ${no_undefined}
    CACHE STRING "Flags used by the linker during all build types." FORCE)

FIND_PACKAGE(Git QUIET)
if(GIT_FOUND AND EXISTS "${PROJECT_SOURCE_DIR}/.git")
  # Update submodules as needed
  option(GIT_SUBMODULE "Check submodules during build" ON)
  if(GIT_SUBMODULE)
    message(STATUS "Submodule update")
    execute_process(COMMAND ${GIT_EXECUTABLE} submodule update --init --recursive
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
      RESULT_VARIABLE GIT_SUBMOD_RESULT)
    if(NOT GIT_SUBMOD_RESULT EQUAL "0")
      message(FATAL_ERROR "git submodule update --init failed with ${GIT_SUBMOD_RESULT}, please checkout submodules")
    endif()
  endif()
endif()

FIND_PACKAGE(Threads REQUIRED)

# download CPM.cmake
FILE(
  DOWNLOAD
  https://github.com/cpm-cmake/CPM.cmake/releases/download/v0.40.8/CPM.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/cmake/CPM.cmake
  EXPECTED_HASH SHA256=78ba32abdf798bc616bab7c73aac32a17bbd7b06ad9e26a6add69de8f3ae4791
)
INCLUDE(${CMAKE_CURRENT_BINARY_DIR}/cmake/CPM.cmake)

INCLUDE(FetchContent)

# Add boost dependency
SET(AddBoost.cmake_VERSION 3.7.3)
CPMAddPackage(
  NAME AddBoost.cmake
  VERSION "${AddBoost.cmake_VERSION}"
  URL "https://github.com/Arniiiii/AddBoost.cmake/archive/refs/tags/${AddBoost.cmake_VERSION}.tar.gz"
)

SET(TRY_BOOST_VERSION "1.88.0")

CPMAddPackage("gh:sago007/PlatformFolders#4.2.0")
CPMAddPackage("gh:CLIUtils/CLI11@2.5.0")
CPMAddPackage("gh:marzer/tomlplusplus@3.4.0")

CPMAddPackage(
  NAME spdlog
  GIT_REPOSITORY https://github.com/gabime/spdlog.git
  GIT_TAG v1.x
  OPTIONS
    "SPDLOG_USE_STD_FORMAT ON"
    "SPDLOG_BUILD_PIC ON"
)

ADD_SUBDIRECTORY(src)
