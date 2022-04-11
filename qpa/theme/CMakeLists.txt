
set(theme_SRCS
    platformplugin.cpp
    qeimplatformtheme.cpp
)

add_library(qeimplatformtheme MODULE ${theme_SRCS})
target_link_libraries(qeimplatformtheme
    Qt${QT_VERSION_MAJOR}::Gui
  )
target_include_directories(qeimplatformtheme
    PRIVATE
    ${QT_QPA_INCLUDEDIR})

install(TARGETS qeimplatformtheme DESTINATION ${QT_PLUGINS_DIR}/platformthemes)
