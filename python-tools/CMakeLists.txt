project(PythonTools)
cmake_minimum_required(VERSION 3.18)

add_custom_target(python-tools-build-deb ALL
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_BINARY_DIR}/deb/"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/python-tools" "${CMAKE_BINARY_DIR}/deb/usr/share/python-tools"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/DEBIAN/" "${CMAKE_BINARY_DIR}/deb/DEBIAN"
    COMMAND /usr/bin/dpkg -b ${CMAKE_BINARY_DIR}/deb/ python-tools.deb)
