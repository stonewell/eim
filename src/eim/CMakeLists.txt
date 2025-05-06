SET(EIM_SOURCES eim.cpp
                command_line_options.h command_line_options.cpp)

ADD_EXECUTABLE(eim ${EIM_SOURCES})

TARGET_LINK_LIBRARIES(eim PRIVATE
  platform_folders
  spdlog
  CLI11::CLI11
  tomlplusplus::tomlplusplus
)
