#pragma once
#ifndef MXSCRIPT_FFI_HPP
#define MXSCRIPT_FFI_HPP

#include "macro.hpp"
#include "object.h"

namespace mxs_runtime { }

extern "C" {
MXS_API mxs_runtime::MXObject *mxs_ffi_call(mxs_runtime::MXObject *lib_name_obj,
                                            mxs_runtime::MXObject *func_name_obj,
                                            int argc, mxs_runtime::MXObject **argv);
}

#endif// MXSCRIPT_FFI_HPP
