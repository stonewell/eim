project(QEimPlatform)

cmake_minimum_required(VERSION 3.0)

set(QEIMPLATFORM_VERSION "0.1.0")

set(QT_MIN_VERSION "6.2.0")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(LIBQGNOMEPLATFORM_SUFFIX "6")

set(CMAKE_AUTOMOC ON)

find_package(QT NAMES Qt6 COMPONENTS Core Gui Widgets REQUIRED)

find_package(Qt${QT_VERSION_MAJOR} ${QT_MIN_VERSION} CONFIG REQUIRED COMPONENTS
    Core
    Gui
    Widgets
)

find_package(Qt${QT_VERSION_MAJOR}Gui ${QT_MIN_VERSION} CONFIG REQUIRED Private)

add_subdirectory(theme)
