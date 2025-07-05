#pragma once
#ifndef BUILT_IN_HPP
#define BUILT_IN_HPP

#include "boolean.hpp"
#include "container.hpp"
#include "functions.hpp"
#include "nil.hpp"
#include "numeric.hpp"
#include "object.h"
#include "string.hpp"

#ifdef __cplusplus
extern "C" {
#endif

MXS_API mxs_runtime::MXObject *printf_wrapper(mxs_runtime::MXObject *format,
                                              mxs_runtime::MXObject *packed_argv);
MXS_API mxs_runtime::MXObject *modern_print_wrapper(mxs_runtime::MXObject *packed_argv);

#ifdef __cplusplus
}
#endif

#endif
