#ifndef MX_MACRO
#define MX_MACRO
#pragma once
#ifndef MXSCRIPT_EXPORT_HPP
#define MXSCRIPT_EXPORT_HPP

#ifdef _WIN32
#ifdef MXS_BUILD_DLL// 这个宏应该在编译动态库时由编译器定义
#define MXS_API __declspec(dllexport)
#else
#define MXS_API __declspec(dllimport)
#endif
#else// For GCC/Clang on Linux/macOS
#define MXS_API __attribute__((visibility("default")))
#endif

#endif// MXSCRIPT_EXPORT_HPP
#endif//MX_MACRO