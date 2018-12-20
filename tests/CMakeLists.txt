SET(test_core_src
  "test_buffer.cxx"
  )

ADD_EXECUTABLE(test_buffer
    ${test_core_src}
    )

TARGET_COMPILE_DEFINITIONS(test_buffer PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(test_buffer PRIVATE
  )
TARGET_LINK_LIBRARIES(test_buffer
  core
  )

add_test(NAME test_buffer
  COMMAND test_buffer
  )

ADD_EXECUTABLE(test_file_buffer
    "test_file_buffer.cxx"
    )
TARGET_COMPILE_DEFINITIONS(test_file_buffer PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(test_file_buffer PRIVATE
  )
TARGET_LINK_LIBRARIES(test_file_buffer
  core
  cmds
)

add_test(NAME test_file_buffer
  COMMAND test_file_buffer ${CMAKE_CURRENT_SOURCE_DIR}/test_file_buffer.cxx
  )

ADD_EXECUTABLE(test_get_buf_cmd
    "test_get_buffer_cmd.cxx"
    )
TARGET_COMPILE_DEFINITIONS(test_get_buf_cmd PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(test_get_buf_cmd PRIVATE
  )
TARGET_LINK_LIBRARIES(test_get_buf_cmd
  core
  cmds
)

add_test(NAME test_get_buf_cmd
  COMMAND test_get_buf_cmd ${CMAKE_CURRENT_SOURCE_DIR}/test_get_buffer_cmd.cxx
  )
