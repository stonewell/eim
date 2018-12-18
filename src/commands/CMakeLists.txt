SET(cmds_src cmd_base.h
  get_buffer_cmd.cxx
    )

ADD_LIBRARY(cmds OBJECT
    ${cmds_src}
    )

TARGET_COMPILE_DEFINITIONS(cmds PRIVATE
)

TARGET_INCLUDE_DIRECTORIES(cmds PRIVATE
)

TARGET_LINK_LIBRARIES(cmds
  PUBLIC core
  PUBLIC json
)
