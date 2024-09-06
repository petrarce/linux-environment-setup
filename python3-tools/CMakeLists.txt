project(PythonTools)
cmake_minimum_required(VERSION 3.18)

set( RES_DEB_FILE "${CMAKE_CURRENT_BINARY_DIR}/python3-tools.deb" )
file(GLOB_RECURSE PKG_FILES LIST_DIRECTORIES false  "pkg/*")
add_custom_command(OUTPUT "${RES_DEB_FILE}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/deb/"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/pkg" "${CMAKE_CURRENT_BINARY_DIR}/deb/"
    COMMAND /usr/bin/dpkg -b "${CMAKE_CURRENT_BINARY_DIR}/deb" "${RES_DEB_FILE}"

    DEPENDS ${PKG_FILES}
)

add_custom_target( python3-tools-deb ALL
    DEPENDS "${RES_DEB_FILE}"
)

install(
    FILES "${RES_DEB_FILE}"
    DESTINATION .
)