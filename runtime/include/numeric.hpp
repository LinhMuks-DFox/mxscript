#pragma once
#ifndef MXSCRIPT_NUMERIC_HPP
#define MXSCRIPT_NUMERIC_HPP

#include "object.hpp"
#include "_typedef.hpp"
#include "macro.hpp"

namespace mxs_runtime {

class MXInteger : public MXObject {
public:
    const inner_integer value;
    explicit MXInteger(inner_integer v);
};

class MXFloat : public MXObject {
public:
    const inner_float value;
    explicit MXFloat(inner_float v);
};

MXS_API MXInteger* MXCreateInteger(inner_integer value);
MXS_API MXFloat* MXCreateFloat(inner_float value);

} // namespace mxs_runtime

#endif // MXSCRIPT_NUMERIC_HPP
