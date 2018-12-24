SET(scite_cocoa_src gui_cocoa.cxx)

SET(scite_cocoa_gui_src
    AppDelegate.h AppDelegate.mm
    main.m
    MainMenu.xib
    Info.plist.in)

ADD_LIBRARY(scite_cocoa OBJECT
  ${scite_cocoa_src}
  ${scite_cocoa_gui_src}
  )

FIND_LIBRARY(CoreFoundation_LIBRARY CoreFoundation)
FIND_LIBRARY(Cocoa_LIBRARY Cocoa)

TARGET_LINK_LIBRARIES(scite_cocoa PUBLIC
   scintilla_interface
   ${CoreFoundation_LIBRARY}
   ${Cocoa_LIBRARY}
)
TARGET_INCLUDE_DIRECTORIES(scite_cocoa PRIVATE
   "../../../third_party/scite/src"
)

SET_PROPERTY(TARGET scite_cocoa APPEND_STRING PROPERTY
              COMPILE_FLAGS "-fobjc-arc -Wno-unused-parameter -Wno-deprecated-declarations")
