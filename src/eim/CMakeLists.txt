SET(EIM_SOURCES eim.cpp
                command_line_options.h command_line_options.cpp
                context.h context.cpp
                plugin_manager.h plugin_manager.cpp)

ADD_EXECUTABLE(eim ${EIM_SOURCES})

TARGET_LINK_LIBRARIES(eim PRIVATE
  platform_folders
  spdlog
  CLI11::CLI11
  tomlplusplus::tomlplusplus
  Boost::dll
)
TARGET_COMPILE_OPTIONS(eim PRIVATE ${PROJECT_CXX_FLAGS})
TARGET_LINK_OPTIONS(eim PRIVATE ${PROJECT_LINK_FLAGS})
