SET(core_src
    buffer.h
    command.h
    file_buffer.h
    buffer.cxx
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
