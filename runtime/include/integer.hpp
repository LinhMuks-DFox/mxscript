#pragma once
#ifndef MXSCRIPT_INTEGER_HPP
#define MXSCRIPT_INTEGER_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {
    class MXInteger : public MXObject {
    public:
        const inner_integer value;
        explicit MXInteger(inner_integer v);
    };
}

// C API
#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXInteger* MXCreateInteger(mxs_runtime::inner_integer value);
#ifdef __cplusplus
}
#endif

#endif // MXSCRIPT_INTEGER_HPP
