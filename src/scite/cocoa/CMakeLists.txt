SET(scite_cocoa_src gui_cocoa.cxx)

ADD_LIBRARY(scite_cocoa STATIC
  ${scite_cocoa_src}
  )

TARGET_LINK_LIBRARIES(scite_cocoa PRIVATE
   scintilla_interface
)
TARGET_INCLUDE_DIRECTORIES(scite_cocoa PRIVATE
   "../../../third_party/scite/src"
)

SET_PROPERTY(TARGET scite_cocoa APPEND_STRING PROPERTY
              COMPILE_FLAGS "-fobjc-arc -Wno-unused-parameter -Wno-deprecated-declarations")
