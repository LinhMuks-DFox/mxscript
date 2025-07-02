#pragma once
#ifndef MXSCRIPT_FLOAT_HPP
#define MXSCRIPT_FLOAT_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"

namespace mxs_runtime {
    class MXFloat : public MXObject {
    public:
        const inner_float value;
        explicit MXFloat(inner_float v);
    };
}

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXFloat* MXCreateFloat(mxs_runtime::inner_float value);
#ifdef __cplusplus
}
#endif

#endif // MXSCRIPT_FLOAT_HPP
