SET(EIM_SOURCES eim.cpp)

ADD_EXECUTABLE(eim ${EIM_SOURCES})

TARGET_LINK_LIBRARIES(eim PRIVATE
  platform_folders
  spdlog
  CLI11::CLI11
  tomlplusplus::tomlplusplus
)
