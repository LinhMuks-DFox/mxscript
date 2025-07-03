#pragma once
#ifndef MXSCRIPT_NUMERIC_HPP
#define MXSCRIPT_NUMERIC_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.hpp"
#include "string.hpp"
namespace mxs_runtime {

    class MXNumeric : public MXObject {
    public:
        explicit MXNumeric(const RTTI* rtti, bool is_static = false);
        virtual auto to_string() const -> std::string = 0;
        auto repr() const -> inner_string override { return to_string(); }
    };

    class MXInteger : public MXNumeric {
    public:
        const inner_integer value;
        explicit MXInteger(inner_integer v);
        auto to_string() const -> inner_string override;
    };

    class MXFloat : public MXNumeric {
    public:
        const inner_float value;
        explicit MXFloat(inner_float v);
        auto to_string() const -> inner_string override;
    };

    MXS_API MXInteger *MXCreateInteger(inner_integer value);
    MXS_API MXFloat *MXCreateFloat(inner_float value);

}// namespace mxs_runtime

#endif// MXSCRIPT_NUMERIC_HPP
