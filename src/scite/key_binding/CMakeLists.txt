SET(key_binding_src
  key_binding.cxx key_binding.h
    )

ADD_LIBRARY(key_binding STATIC
  ${key_binding_src}
  )

TARGET_INCLUDE_DIRECTORIES(key_binding PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}
  )

TARGET_LINK_LIBRARIES(key_binding PRIVATE
    scintilla_interface
)
