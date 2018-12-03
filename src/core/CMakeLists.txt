SET(core_src
    buffer.h
    command.h
    file_buffer.h
    buffer.cxx
    file_buffer.cxx
    eim_context.h
    buffer_manager.h
    buffer_session.h
    command_manager.h
    )

ADD_LIBRARY(core STATIC
    ${core_src}
    )

TARGET_COMPILE_DEFINITIONS(core PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(core PRIVATE
  )
TARGET_LINK_LIBRARIES(core
  ${CMAKE_DL_LIBS}
  )
