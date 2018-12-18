SET(core_src
    buffer.h buffer.cxx
    command.h
    file_buffer.h file_buffer.cxx
    eim_context.h eim_context.cxx
    buffer_manager.h buffer_manager.cxx
    buffer_session.h
    command_manager.h command_manager.cxx
    buffer_session_manager.h
    )

ADD_LIBRARY(core STATIC
    ${core_src}
    )

IF ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
  SET(addtion_libs "stdc++fs")
ELSE()
  SET(addtion_libs "")
ENDIF()

TARGET_COMPILE_DEFINITIONS(core PRIVATE
)
TARGET_INCLUDE_DIRECTORIES(core PRIVATE
)
TARGET_INCLUDE_DIRECTORIES(core INTERFACE
  ${CMAKE_CURRENT_SOURCE_DIR}
)

TARGET_LINK_LIBRARIES(core
  PUBLIC ${addtion_libs}
)
