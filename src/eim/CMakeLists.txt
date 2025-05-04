SET(EIM_SOURCES eim.cpp)

ADD_EXECUTABLE(eim ${EIM_SOURCES})

TARGET_LINK_LIBRARIES(eim PUBLIC yaml-cpp::yaml-cpp platform_folders)
