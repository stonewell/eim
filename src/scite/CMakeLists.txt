SET(scite_src
../../third_party/scite/src/Cookie.cxx
../../third_party/scite/src/Cookie.h
../../third_party/scite/src/Credits.cxx
../../third_party/scite/src/EditorConfig.cxx
../../third_party/scite/src/EditorConfig.h
../../third_party/scite/src/ExportHTML.cxx
../../third_party/scite/src/ExportPDF.cxx
../../third_party/scite/src/ExportRTF.cxx
../../third_party/scite/src/ExportTEX.cxx
../../third_party/scite/src/ExportXML.cxx
../../third_party/scite/src/Extender.h
../../third_party/scite/src/FilePath.cxx
../../third_party/scite/src/FilePath.h
../../third_party/scite/src/FileWorker.cxx
../../third_party/scite/src/FileWorker.h
../../third_party/scite/src/GUI.h
../../third_party/scite/src/IFaceTable.cxx
../../third_party/scite/src/IFaceTable.h
../../third_party/scite/src/JobQueue.cxx
../../third_party/scite/src/JobQueue.h
../../third_party/scite/src/LuaExtension.cxx
../../third_party/scite/src/LuaExtension.h
../../third_party/scite/src/MatchMarker.cxx
../../third_party/scite/src/MatchMarker.h
../../third_party/scite/src/MultiplexExtension.cxx
../../third_party/scite/src/MultiplexExtension.h
../../third_party/scite/src/Mutex.h
../../third_party/scite/src/PropSetFile.cxx
../../third_party/scite/src/PropSetFile.h
../../third_party/scite/src/SciTE.h
../../third_party/scite/src/SciTEBase.cxx
../../third_party/scite/src/SciTEBase.h
../../third_party/scite/src/SciTEBuffers.cxx
../../third_party/scite/src/SciTEIO.cxx
../../third_party/scite/src/SciTEKeys.h
../../third_party/scite/src/SciTEProps.cxx
../../third_party/scite/src/ScintillaWindow.cxx
../../third_party/scite/src/ScintillaWindow.h
../../third_party/scite/src/StringHelpers.cxx
../../third_party/scite/src/StringHelpers.h
../../third_party/scite/src/StringList.cxx
../../third_party/scite/src/StringList.h
../../third_party/scite/src/StripDefinition.h
../../third_party/scite/src/StyleDefinition.cxx
../../third_party/scite/src/StyleDefinition.h
../../third_party/scite/src/StyleWriter.cxx
../../third_party/scite/src/StyleWriter.h
../../third_party/scite/src/Utf8_16.cxx
../../third_party/scite/src/Utf8_16.h
../../third_party/scite/src/Worker.h
../../third_party/scite/src/scite_lua_win.h
)

SET(lua_src
../../third_party/scite/lua/src/lapi.c
../../third_party/scite/lua/src/lapi.h
../../third_party/scite/lua/src/lauxlib.c
../../third_party/scite/lua/src/lauxlib.h
../../third_party/scite/lua/src/lbaselib.c
../../third_party/scite/lua/src/lbitlib.c
../../third_party/scite/lua/src/lcode.c
../../third_party/scite/lua/src/lcode.h
../../third_party/scite/lua/src/lcorolib.c
../../third_party/scite/lua/src/lctype.c
../../third_party/scite/lua/src/lctype.h
../../third_party/scite/lua/src/ldblib.c
../../third_party/scite/lua/src/ldebug.c
../../third_party/scite/lua/src/ldebug.h
../../third_party/scite/lua/src/ldo.c
../../third_party/scite/lua/src/ldo.h
../../third_party/scite/lua/src/ldump.c
../../third_party/scite/lua/src/lfunc.c
../../third_party/scite/lua/src/lfunc.h
../../third_party/scite/lua/src/lgc.c
../../third_party/scite/lua/src/lgc.h
../../third_party/scite/lua/src/linit.c
../../third_party/scite/lua/src/liolib.c
../../third_party/scite/lua/src/llex.c
../../third_party/scite/lua/src/llex.h
../../third_party/scite/lua/src/llimits.h
../../third_party/scite/lua/src/lmathlib.c
../../third_party/scite/lua/src/lmem.c
../../third_party/scite/lua/src/lmem.h
../../third_party/scite/lua/src/loadlib.c
../../third_party/scite/lua/src/lobject.c
../../third_party/scite/lua/src/lobject.h
../../third_party/scite/lua/src/lopcodes.c
../../third_party/scite/lua/src/lopcodes.h
../../third_party/scite/lua/src/loslib.c
../../third_party/scite/lua/src/lparser.c
../../third_party/scite/lua/src/lparser.h
../../third_party/scite/lua/src/lprefix.h
../../third_party/scite/lua/src/lstate.c
../../third_party/scite/lua/src/lstate.h
../../third_party/scite/lua/src/lstring.c
../../third_party/scite/lua/src/lstring.h
../../third_party/scite/lua/src/lstrlib.c
../../third_party/scite/lua/src/ltable.c
../../third_party/scite/lua/src/ltable.h
../../third_party/scite/lua/src/ltablib.c
../../third_party/scite/lua/src/ltm.c
../../third_party/scite/lua/src/ltm.h
../../third_party/scite/lua/src/lua.h
../../third_party/scite/lua/src/lua.hpp
../../third_party/scite/lua/src/luaconf.h
../../third_party/scite/lua/src/lualib.h
../../third_party/scite/lua/src/lundump.c
../../third_party/scite/lua/src/lundump.h
../../third_party/scite/lua/src/lutf8lib.c
../../third_party/scite/lua/src/lvm.c
../../third_party/scite/lua/src/lvm.h
../../third_party/scite/lua/src/lzio.c
../../third_party/scite/lua/src/lzio.h
)

ADD_LIBRARY(scite_objs OBJECT
  ${scite_src}
  )

ADD_LIBRARY(lua_objs OBJECT
  ${lua_src}
)

ADD_EXECUTABLE(scite
    $<TARGET_OBJECTS:scite_objs>
    $<TARGET_OBJECTS:lua_objs>
)

TARGET_COMPILE_DEFINITIONS(scite_objs PRIVATE
  "__unix__"
)
TARGET_INCLUDE_DIRECTORIES(scite_objs PRIVATE
  "../../third_party/scite/lua/src"
)

TARGET_LINK_LIBRARIES(scite_objs PUBLIC
   scintilla_interface
)

IF (APPLE)
ADD_SUBDIRECTORY(cocoa)

TARGET_LINK_LIBRARIES(scite PRIVATE
  scite_cocoa
)
ENDIF()