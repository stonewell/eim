SET(scite_gtk_src
  ../../../third_party/scite/gtk/DirectorExtension.h
  ../../../third_party/scite/gtk/GUIGTK.cxx
  ../../../third_party/scite/gtk/Widget.cxx
  ../../../third_party/scite/gtk/DirectorExtension.cxx
  ../../../third_party/scite/gtk/GTKMutex.cxx
  ../../../third_party/scite/gtk/pixmapsGNOME.h
  ../../../third_party/scite/gtk/SciIcon.h
  ../../../third_party/scite/gtk/SciTEGTK.cxx
  ../../../third_party/scite/gtk/Widget.h)

SET(platform_compile_definition
  GTK
  SCI_LEXER
  PIXMAP_PATH=""
  )

ADD_LIBRARY(scite_gtk OBJECT
  ${scite_gtk_src}
  )

TARGET_INCLUDE_DIRECTORIES(scite_gtk PRIVATE
   "../../../third_party/scite/src"
  )
TARGET_COMPILE_DEFINITIONS(scite_gtk PUBLIC
  ${platform_compile_definition}
  )

TARGET_LINK_LIBRARIES(scite_gtk PUBLIC
   scintilla_interface
)

SET_PROPERTY(TARGET scite_gtk APPEND_STRING PROPERTY
              COMPILE_FLAGS "-pedantic -fPIC -Wno-unused-parameter -Wno-deprecated-declarations -Wno-missing-field-initializers")
