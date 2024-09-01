project(PythonTools)
cmake_minimum_required(VERSION 3.18)

set( RES_DEB_FILE "${CMAKE_CURRENT_BINARY_DIR}/python-tools.deb" )
add_custom_command(OUTPUT "${RES_DEB_FILE}"
    COMMAND ${CMAKE_COMMAND} -E make_directory "${CMAKE_CURRENT_BINARY_DIR}/deb/"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/DEBIAN" "${CMAKE_CURRENT_BINARY_DIR}/deb/DEBIAN"
    COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_CURRENT_SOURCE_DIR}/usr/" "${CMAKE_CURRENT_BINARY_DIR}/deb/usr"
    COMMAND /usr/bin/dpkg -b "${CMAKE_CURRENT_BINARY_DIR}/deb" "${RES_DEB_FILE}"

    DEPENDS
        ./usr/shares/python-tools/Finances/FinanceRoutines.py
        ./usr/shares/python-tools/Finances/__init__.py
        ./usr/shares/python-tools/PyPlotTools/Printers.py
        ./usr/shares/python-tools/git-replace.py
        ./usr/shares/python-tools/LinalgTools/Transforms.py
        ./DEBIAN/control
)

add_custom_target( python-tools-deb ALL
    DEPENDS "${RES_DEB_FILE}"
)

install(
    FILES "${RES_DEB_FILE}"
    DESTINATION .
)