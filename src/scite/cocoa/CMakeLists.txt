SET(scite_cocoa_src
    gui_cocoa.cxx
    scite_cocoa.cxx scite_cocoa.h
    scite_cocoa.mm
    )

SET(scite_cocoa_gui_src
    AppDelegate.h AppDelegate.mm
    main.m
    MainMenu.xib
    Info.plist.in
    SciTEWindow.mm SciTEWindow.h)

ADD_LIBRARY(scite_cocoa OBJECT
  ${scite_cocoa_src}
  ${scite_cocoa_gui_src}
  )

FIND_LIBRARY(CoreFoundation_LIBRARY CoreFoundation)
FIND_LIBRARY(Cocoa_LIBRARY Cocoa)
FIND_LIBRARY(CoreAnimation_LIBRARY QuartzCore)

TARGET_LINK_LIBRARIES(scite_cocoa PUBLIC
   scintilla_interface
   ${CoreFoundation_LIBRARY}
   ${Cocoa_LIBRARY}
   ${CoreAnimation_LIBRARY}
)
TARGET_INCLUDE_DIRECTORIES(scite_cocoa PRIVATE
   "../../../third_party/scite/src"
   "../../../third_party/scintilla/cocoa"
)

SET_PROPERTY(TARGET scite_cocoa APPEND_STRING PROPERTY
              COMPILE_FLAGS "-fobjc-arc -Wno-unused-parameter -Wno-deprecated-declarations")
