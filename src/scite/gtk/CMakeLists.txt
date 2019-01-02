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

FIND_PACKAGE(PkgConfig)
PKG_CHECK_MODULES(GLIB glib-2.0)
PKG_CHECK_MODULES(GMODULE gmodule-2.0)
PKG_CHECK_MODULES(GTK3 REQUIRED gtk+-3.0)

SET(platform_include_dirs
  "../../../third_party/scintilla/gtk"
  ${GTK3_INCLUDE_DIRS}
  ${GLIB_INCLUDE_DIRS}
  )

SET(platform_compile_definition
  GTK
  PIXMAP_PATH=""
  )

SET(platform_link_library
  ${GLB_LIBRARIES}
  ${GTK3_LIBRARIES}
  )

ADD_LIBRARY(scite_gtk OBJECT
  ${scite_gtk_src}
  )

TARGET_INCLUDE_DIRECTORIES(scite_gtk PRIVATE
  ${platform_include_dirs}
   "../../../third_party/scite/src"
  )
TARGET_COMPILE_DEFINITIONS(scite_gtk PUBLIC
  ${platform_compile_definition}
  )

TARGET_LINK_LIBRARIES(scite_gtk PUBLIC
   scintilla_interface
   ${GTK3_LIBRARIES}
   ${GLIB_LIBRARIES}
   ${GMODULE_LIBRARIES}
)

SET_PROPERTY(TARGET scite_gtk APPEND_STRING PROPERTY
              COMPILE_FLAGS "-Wno-unused-parameter -Wno-deprecated-declarations -Wno-missing-field-initializers")
