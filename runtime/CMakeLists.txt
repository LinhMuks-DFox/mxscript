cmake_minimum_required(VERSION 3.10)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE INTERNAL "")
project(mx_runtime CXX C)

# ----------- C++23 ----------
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ----------- Clang + libc++ ----------
if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  message(STATUS "Detected Clang, adding libc++ flags")
  add_compile_options(-stdlib=libc++)
  add_link_options(-stdlib=libc++)
endif()


# ----------- 输出目录 ----------
get_filename_component(PROJECT_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." REALPATH)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_ROOT}/bin")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_ROOT}/bin")

# ----------- 源文件 ----------
# add_library(runtime SHARED ${IMPL_SOURCES})
file(GLOB_RECURSE IMPL_SOURCES "impl/*.cpp")
add_library(runtime SHARED ${IMPL_SOURCES})
# list(APPEND IMPL_SOURCES "impl/object.cpp")
# list(APPEND IMPL_SOURCES "src/ffi.cpp")


target_include_directories(runtime PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${CMAKE_CURRENT_SOURCE_DIR}"
)
set_target_properties(runtime PROPERTIES POSITION_INDEPENDENT_CODE ON)

# ----------- clangd ----------
# set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
message(STATUS "CMAKE_EXPORT_COMPILE_COMMANDS value after set: ${CMAKE_EXPORT_COMPILE_COMMANDS}")