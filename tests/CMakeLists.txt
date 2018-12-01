SET(test_core_src
  "test_buffer.cxx"
  )

ADD_EXECUTABLE(test_core
    ${test_core_src}
    )

TARGET_COMPILE_DEFINITIONS(test_core PRIVATE
  )
TARGET_INCLUDE_DIRECTORIES(test_core PRIVATE
  "../src/core"
  )
TARGET_LINK_LIBRARIES(test_core
  core
  ${CMAKE_DL_LIBS}
  )

add_test(NAME test_core
  COMMAND test_core
  )
