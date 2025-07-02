# CMake最低版本要求
cmake_minimum_required(VERSION 3.10)

# 定义项目名称
project(mx_runtime CXX C)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- 设置输出目录 ---
# 获取项目根目录 (runtime目录的上一级)
get_filename_component(PROJECT_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/.." REALPATH)
# 将所有二进制文件（.so）输出到 <project_root>/bin
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_ROOT}/bin")
# 将所有静态库文件（.a）输出到 <project_root>/bin
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_ROOT}/bin")

# --- 为了让clangd工作，生成compile_commands.json到构建目录 ---
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# --- 查找所有源文件 ---
# 查找顶层目录的.c文件
file(GLOB TOP_LEVEL_SOURCES "*.c")
# 递归查找impl目录下的所有.cpp文件
file(GLOB_RECURSE IMPL_SOURCES "impl/*.cpp")

# --- 定义要构建的目标 ---
# 将所有源文件编译成一个名为 "runtime" 的共享库 (最终生成 <project_root>/bin/libruntime.so)
add_library(runtime SHARED
    ${TOP_LEVEL_SOURCES}
    ${IMPL_SOURCES}
)

# --- 设置头文件搜索路径 ---
# 让编译器在编译时能找到 include/ 和顶层目录的头文件
target_include_directories(runtime PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${CMAKE_CURRENT_SOURCE_DIR}"
)

# 设置所有目标都需要-fPIC选项（共享库必需）
set_target_properties(runtime PROPERTIES POSITION_INDEPENDENT_CODE ON)