SET(test_core_src
  "test_buffer.cxx"
  )

ADD_EXECUTABLE(test_buffer
    ${test_core_src}
    )

TARGET_COMPILE_DEFINITIONS(test_buffer PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(test_buffer PRIVATE
  "../src/core"
  )
TARGET_LINK_LIBRARIES(test_buffer
  core
  ${CMAKE_DL_LIBS}
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
  "../src/core"
  )
TARGET_LINK_LIBRARIES(test_file_buffer
  core
  ${CMAKE_DL_LIBS}
  )

add_test(NAME test_file_buffer
  COMMAND test_file_buffer ${CMAKE_CURRENT_SOURCE_DIR}/test_file_buffer.cxx
  )
