#pragma once
#ifndef MXSCRIPT_NUMERIC_HPP
#define MXSCRIPT_NUMERIC_HPP

#include "_typedef.hpp"
#include "boolean.hpp"
#include "macro.hpp"
#include "object.h"
#include "string.hpp"
#include "typeinfo.h"

namespace mxs_runtime {

    // Forward declarations
    class MXInteger;
    class MXFloat;
    class MXBoolean;

    extern MXS_API const MXTypeInfo g_integer_type_info;

    /**
     * @brief Base class for all numeric types.
     */
    class MXNumeric : public MXObject {
    public:
        explicit MXNumeric(const MXTypeInfo *info, bool is_static = false);
        virtual auto to_string() const -> std::string = 0;
        auto repr() const -> inner_string override { return to_string(); }
    };

    /**
     * @brief Represents a 64-bit integer.
     */
    class MXInteger : public MXNumeric {
    public:
        const inner_integer value;
        explicit MXInteger(inner_integer v);
        auto to_string() const -> std::string override;
        auto get_value() const -> inner_integer { return value; }

        // --- Operator Overrides ---
        auto op_add(const MXObject &other) -> MXObject * override;
        auto op_sub(const MXObject &other) -> MXObject * override;
        auto op_mul(const MXObject &other) -> MXObject * override;
        auto op_div(const MXObject &other) -> MXObject * override;

        auto op_eq(const MXObject &other) -> MXObject * override;
        auto op_ne(const MXObject &other) -> MXObject * override;
        auto op_lt(const MXObject &other) -> MXObject * override;
        auto op_le(const MXObject &other) -> MXObject * override;
        auto op_gt(const MXObject &other) -> MXObject * override;
        auto op_ge(const MXObject &other) -> MXObject * override;
        auto op_is(const MXObject &other) -> MXObject * override;
    };

    /**
     * @brief Represents a 64-bit float (double).
     */
    class MXFloat : public MXNumeric {
    public:
        const inner_float value;
        explicit MXFloat(inner_float v);
        auto to_string() const -> std::string override;

        // --- Operator Overrides ---
        auto op_add(const MXObject &other) -> MXObject * override;
        auto op_sub(const MXObject &other) -> MXObject * override;
        auto op_mul(const MXObject &other) -> MXObject * override;
        auto op_div(const MXObject &other) -> MXObject * override;

        auto op_eq(const MXObject &other) -> MXObject * override;
        auto op_ne(const MXObject &other) -> MXObject * override;
        auto op_lt(const MXObject &other) -> MXObject * override;
        auto op_le(const MXObject &other) -> MXObject * override;
        auto op_gt(const MXObject &other) -> MXObject * override;
        auto op_ge(const MXObject &other) -> MXObject * override;
        auto op_is(const MXObject &other) -> MXObject * override;
        // TODO: other operators not yet implemented
    };


}// namespace mxs_runtime
#ifdef __cplusplus
extern "C"
#endif
{
//======================================================================
// C API for Runtime Object Creation
//======================================================================
MXS_API mxs_runtime::MXInteger *MXCreateInteger(mxs_runtime::inner_integer value);
MXS_API mxs_runtime::MXFloat *MXCreateFloat(mxs_runtime::inner_float value);


//======================================================================
// C API for Dynamic Dispatch ("Polymorphic Path")
//======================================================================

// --- Arithmetic ---
MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_mul(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_div(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right);

// --- Comparison ---
MXS_API mxs_runtime::MXObject *
mxs_op_eq(mxs_runtime::MXObject *left,
          mxs_runtime::MXObject *right);// Corresponds to `==`
MXS_API mxs_runtime::MXObject *mxs_op_ne(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_lt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_le(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_gt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_ge(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *
mxs_op_is(mxs_runtime::MXObject *left,
          mxs_runtime::MXObject *right);// Corresponds to `is`

// --- Logical ---
MXS_API mxs_runtime::MXObject *mxs_op_and(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *mxs_op_or(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right);
MXS_API mxs_runtime::MXObject *
mxs_op_not(mxs_runtime::MXObject *operand);// Unary operator

MXS_API mxs_runtime::MXObject *mxs_int_absolute(mxs_runtime::MXObject *integer_obj);
#ifdef __cplusplus
}
#endif
#endif// MXSCRIPT_NUMERIC_HPP
