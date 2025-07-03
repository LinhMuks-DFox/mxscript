#pragma once
#ifndef MXSCRIPT_NUMERIC_HPP
#define MXSCRIPT_NUMERIC_HPP

#include "_typedef.hpp"
#include "macro.hpp"
#include "object.h"
#include "string.hpp"
#include "typeinfo.h"
#include "boolean.hpp"

namespace mxs_runtime {

    // Forward declarations
    class MXInteger;
    class MXFloat;
    class MXBoolean;

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
        // ... other methods ...

        // --- Operator Declarations for VTable ---
        auto add(const MXObject& other) const -> MXObject*;
        auto sub(const MXObject& other) const -> MXObject*;
        auto mul(const MXObject& other) const -> MXObject*;
        auto div(const MXObject& other) const -> MXObject*;

        auto op_eq(const MXObject& other) const -> MXObject*;
        auto op_ne(const MXObject& other) const -> MXObject*;
        auto op_lt(const MXObject& other) const -> MXObject*;
        auto op_le(const MXObject& other) const -> MXObject*;
        auto op_gt(const MXObject& other) const -> MXObject*;
        auto op_ge(const MXObject& other) const -> MXObject*;
    };

    /**
     * @brief Represents a 64-bit float (double).
     */
    class MXFloat : public MXNumeric {
    public:
        const inner_float value;
        explicit MXFloat(inner_float v);
        // ... other methods ...

        // --- Operator Declarations for VTable ---
        auto add(const MXObject& other) const -> MXObject*;
        auto sub(const MXObject& other) const -> MXObject*;
        auto mul(const MXObject& other) const -> MXObject*;
        auto div(const MXObject& other) const -> MXObject*;

        auto op_eq(const MXObject& other) const -> MXObject*;
        auto op_ne(const MXObject& other) const -> MXObject*;
        auto op_lt(const MXObject& other) const -> MXObject*;
        auto op_le(const MXObject& other) const -> MXObject*;
        auto op_gt(const MXObject& other) const -> MXObject*;
        auto op_ge(const MXObject& other) const -> MXObject*;
    };


} // namespace mxs_runtime
#ifdef __cplusplus
extern "C"
#endif
{
   //======================================================================
    // C API for Runtime Object Creation
    //======================================================================
    MXS_API MXInteger *MXCreateInteger(inner_integer value);
    MXS_API MXFloat *MXCreateFloat(inner_float value);

    //======================================================================
    // C API for Static Dispatch ("Fast Path")
    //======================================================================

    // --- Arithmetic ---
    MXS_API MXObject *integer_add_integer(MXObject *left, MXObject *right);
    // ... other arithmetic functions ...

    // --- Comparison (returns MXBoolean) ---
    MXS_API MXObject *integer_eq_integer(MXObject *left, MXObject *right);
    MXS_API MXObject *integer_gt_integer(MXObject *left, MXObject *right);
    // ... other integer/float comparison combinations ...

    // --- Logical (on MXBoolean objects) ---
    MXS_API MXObject *boolean_and_boolean(MXObject *left, MXObject *right);
    MXS_API MXObject *boolean_or_boolean(MXObject *left, MXObject *right);
    MXS_API MXObject *boolean_not(MXObject *operand);


    //======================================================================
    // C API for Dynamic Dispatch ("Polymorphic Path")
    //======================================================================

    // --- Arithmetic ---
    MXS_API MXObject *mxs_op_add(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_sub(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_mul(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_div(MXObject *left, MXObject *right);

    // --- Comparison ---
    MXS_API MXObject *mxs_op_eq(MXObject *left, MXObject *right); // Corresponds to `==`
    MXS_API MXObject *mxs_op_ne(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_lt(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_le(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_gt(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_ge(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_is(MXObject *left, MXObject *right); // Corresponds to `is`

    // --- Logical ---
    MXS_API MXObject *mxs_op_and(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_or(MXObject *left, MXObject *right);
    MXS_API MXObject *mxs_op_not(MXObject *operand); // Unary operator
#ifdef __cplusplus
}
#endif
#endif // MXSCRIPT_NUMERIC_HPP