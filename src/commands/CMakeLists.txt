SET(cmds_src cmd_base.h
  get_buffer_cmd.cxx
    )

ADD_LIBRARY(cmds STATIC
    ${cmds_src}
    )

TARGET_COMPILE_DEFINITIONS(cmds PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(cmds PRIVATE
  ../core
  )
TARGET_LINK_LIBRARIES(cmds
  ${CMAKE_DL_LIBS}
  json
  )
