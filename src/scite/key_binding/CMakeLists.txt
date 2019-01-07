SET(key_binding_src
  key_binding.cxx key_binding.h
  key_binding_cmds.cxx key_binding_cmds.h
    )

ADD_LIBRARY(key_binding STATIC
  ${key_binding_src}
  )

TARGET_INCLUDE_DIRECTORIES(key_binding PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}
  "../../../third_party/scite/src"
  )

TARGET_LINK_LIBRARIES(key_binding PRIVATE
    scintilla_interface
)
