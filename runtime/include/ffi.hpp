#pragma once
#ifndef MXSCRIPT_FFI_HPP
#define MXSCRIPT_FFI_HPP

#include "macro.hpp"
#include "object.h"

namespace mxs_runtime {
    class MXObject;
}

extern "C" {
MXS_API mxs_runtime::MXObject *mxs_variadic_print(mxs_runtime::MXObject *fmt,
                                                  mxs_runtime::MXObject *args);
}

#endif// MXSCRIPT_FFI_HPP
