#include "numeric.hpp"
#include "allocator.hpp"
#include "typeinfo.h"
#include <format>
#include <string>

#define CHECK_INT(obj)                                                                   \
    if (!(obj) || (obj)->type_info != &mxs_runtime::g_integer_type_info) {               \
        return new mxs_runtime::MXError("TypeError", "Argument must be an Integer.");    \
    }

#define CHECK_FLOAT(obj)                                                                 \
    if (!(obj) || std::string((obj)->get_type_name()) != "Float") {                      \
        return new mxs_runtime::MXError("TypeError", "Argument must be a Float.");       \
    }

namespace mxs_runtime {


    static const MXTypeInfo g_numeric_type_info{ "Numeric", nullptr };
    MXS_API const MXTypeInfo g_integer_type_info{ "Integer", &g_numeric_type_info };
    static const MXTypeInfo g_float_type_info{ "Float", &g_numeric_type_info };

    MXNumeric::MXNumeric(const MXTypeInfo *info, bool is_static)
        : MXObject(info, is_static) { }

    MXInteger::MXInteger(inner_integer v)
        : MXNumeric(&g_integer_type_info, false), value(v) { }

    auto MXInteger::to_string() const -> inner_string { return std::format("{}", value); }

    MXFloat::MXFloat(inner_float v) : MXNumeric(&g_float_type_info, false), value(v) { }

    auto MXFloat::to_string() const -> inner_string { return std::format("{}", value); }

    auto MXInteger::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value + r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) + r.value);
        }
        return new MXError("TypeError: unsupported '+' operands");
    }

    auto MXInteger::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value - r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) - r.value);
        }
        return new MXError("TypeError: unsupported '-' operands");
    }

    auto MXInteger::op_mul(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateInteger(value * r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(static_cast<inner_float>(value) * r.value);
        }
        return new MXError("TypeError: unsupported '*' operands");
    }

    auto MXInteger::op_div(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            if (r.value == 0) return new MXError("ZeroDivisionError");
            return MXCreateInteger(value / r.value);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            if (r.value == 0.0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(static_cast<inner_float>(value) / r.value);
        }
        return new MXError("TypeError: unsupported '/' operands");
    }

    auto MXInteger::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) == r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '==' operands");
    }

    auto MXInteger::op_ne(const MXObject &other) -> MXObject * {
        auto *res = op_eq(other);
        if (auto *b = dynamic_cast<MXBoolean *>(res)) {
            return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                            : const_cast<MXBoolean *>(&MX_TRUE);
        }
        return res;
    }

    auto MXInteger::op_lt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value < r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) < r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<' operands");
    }

    auto MXInteger::op_le(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value <= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) <= r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<=' operands");
    }

    auto MXInteger::op_gt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value > r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) > r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>' operands");
    }

    auto MXInteger::op_ge(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value >= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return static_cast<inner_float>(value) >= r.value
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>=' operands");
    }

    auto MXInteger::op_is(const MXObject &other) -> MXObject * {
        return MXObject::op_is(other);
    }

    auto MXFloat::op_add(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value + r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value + static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '+' operands");
    }

    auto MXFloat::op_sub(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value - r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value - static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '-' operands");
    }

    auto MXFloat::op_mul(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return MXCreateFloat(value * r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return MXCreateFloat(value * static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '*' operands");
    }

    auto MXFloat::op_div(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            if (r.value == 0.0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(value / r.value);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            if (r.value == 0) return new MXError("ZeroDivisionError");
            return MXCreateFloat(value / static_cast<inner_float>(r.value));
        }
        return new MXError("TypeError: unsupported '/' operands");
    }

    auto MXFloat::op_eq(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return r.value == value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value == static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '==' operands");
    }

    auto MXFloat::op_ne(const MXObject &other) -> MXObject * {
        auto *res = op_eq(other);
        if (auto *b = dynamic_cast<MXBoolean *>(res)) {
            return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                            : const_cast<MXBoolean *>(&MX_TRUE);
        }
        return res;
    }

    auto MXFloat::op_lt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value < r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value < static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<' operands");
    }

    auto MXFloat::op_le(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value <= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value <= static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '<=' operands");
    }

    auto MXFloat::op_gt(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value > r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value > static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>' operands");
    }

    auto MXFloat::op_ge(const MXObject &other) -> MXObject * {
        if (other.type_info == &g_float_type_info) {
            const auto &r = static_cast<const MXFloat &>(other);
            return value >= r.value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
        }
        if (other.type_info == &g_integer_type_info) {
            const auto &r = static_cast<const MXInteger &>(other);
            return value >= static_cast<inner_float>(r.value)
                           ? const_cast<MXBoolean *>(&MX_TRUE)
                           : const_cast<MXBoolean *>(&MX_FALSE);
        }
        return new MXError("TypeError: unsupported '>=' operands");
    }

    auto MXFloat::op_is(const MXObject &other) -> MXObject * {
        return MXObject::op_is(other);
    }

    MXObject *integer_add_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateInteger(l->value + r->value);
    }

    MXObject *integer_add_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(static_cast<inner_float>(l->value) + r->value);
    }

    MXObject *float_add_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateFloat(l->value + static_cast<inner_float>(r->value));
    }

    MXObject *float_add_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(l->value + r->value);
    }

    MXObject *integer_sub_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateInteger(l->value - r->value);
    }

    MXObject *integer_sub_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(static_cast<inner_float>(l->value) - r->value);
    }

    MXObject *float_sub_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateFloat(l->value - static_cast<inner_float>(r->value));
    }

    MXObject *float_sub_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(l->value - r->value);
    }

    MXObject *integer_mul_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateInteger(l->value * r->value);
    }

    MXObject *integer_mul_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(static_cast<inner_float>(l->value) * r->value);
    }

    MXObject *float_mul_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return MXCreateFloat(l->value * static_cast<inner_float>(r->value));
    }

    MXObject *float_mul_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return MXCreateFloat(l->value * r->value);
    }

    MXObject *integer_div_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        if (r->value == 0) return new MXError("ZeroDivisionError");
        return MXCreateInteger(l->value / r->value);
    }

    MXObject *integer_div_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        if (r->value == 0.0) return new MXError("ZeroDivisionError");
        return MXCreateFloat(static_cast<inner_float>(l->value) / r->value);
    }

    MXObject *float_div_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        if (r->value == 0) return new MXError("ZeroDivisionError");
        return MXCreateFloat(l->value / static_cast<inner_float>(r->value));
    }

    MXObject *float_div_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        if (r->value == 0.0) return new MXError("ZeroDivisionError");
        return MXCreateFloat(l->value / r->value);
    }

    MXObject *integer_eq_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value == r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_eq_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return static_cast<inner_float>(l->value) == r->value
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_eq_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value == static_cast<inner_float>(r->value)
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_eq_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return l->value == r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_ne_integer(MXObject *left, MXObject *right) {
        auto *res = integer_eq_integer(left, right);
        auto *b = static_cast<MXBoolean *>(res);
        return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                        : const_cast<MXBoolean *>(&MX_TRUE);
    }

    MXObject *integer_ne_float(MXObject *left, MXObject *right) {
        auto *res = integer_eq_float(left, right);
        auto *b = static_cast<MXBoolean *>(res);
        return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                        : const_cast<MXBoolean *>(&MX_TRUE);
    }

    MXObject *float_ne_integer(MXObject *left, MXObject *right) {
        auto *res = float_eq_integer(left, right);
        auto *b = static_cast<MXBoolean *>(res);
        return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                        : const_cast<MXBoolean *>(&MX_TRUE);
    }

    MXObject *float_ne_float(MXObject *left, MXObject *right) {
        auto *res = float_eq_float(left, right);
        auto *b = static_cast<MXBoolean *>(res);
        return b->value ? const_cast<MXBoolean *>(&MX_FALSE)
                        : const_cast<MXBoolean *>(&MX_TRUE);
    }

    // greater than
    MXObject *integer_gt_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value > r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_gt_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return static_cast<inner_float>(l->value) > r->value
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_gt_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value > static_cast<inner_float>(r->value)
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_gt_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return l->value > r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_lt_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value < r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_lt_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return static_cast<inner_float>(l->value) < r->value
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_lt_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value < static_cast<inner_float>(r->value)
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_lt_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return l->value < r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                   : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_ge_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value >= r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_ge_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return static_cast<inner_float>(l->value) >= r->value
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_ge_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value >= static_cast<inner_float>(r->value)
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_ge_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return l->value >= r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_le_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value <= r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *integer_le_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXInteger *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return static_cast<inner_float>(l->value) <= r->value
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_le_integer(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXInteger *>(right);
        return l->value <= static_cast<inner_float>(r->value)
                       ? const_cast<MXBoolean *>(&MX_TRUE)
                       : const_cast<MXBoolean *>(&MX_FALSE);
    }

    MXObject *float_le_float(MXObject *left, MXObject *right) {
        auto *l = static_cast<MXFloat *>(left);
        auto *r = static_cast<MXFloat *>(right);
        return l->value <= r->value ? const_cast<MXBoolean *>(&MX_TRUE)
                                    : const_cast<MXBoolean *>(&MX_FALSE);
    }
}// namespace mxs_runtime

#ifdef __cplusplus
extern "C" {
#endif
MXS_API mxs_runtime::MXObject *integer_add_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_add_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_add_float(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_add_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_add_integer(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_add_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_add_float(mxs_runtime::MXObject *left,
                                               mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_add_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_sub_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_sub_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_sub_float(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_sub_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_sub_integer(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_sub_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_sub_float(mxs_runtime::MXObject *left,
                                               mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_sub_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_mul_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_mul_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_mul_float(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_mul_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_mul_integer(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_mul_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_mul_float(mxs_runtime::MXObject *left,
                                               mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_mul_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_div_integer(mxs_runtime::MXObject *left,
                                                   mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_div_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_div_float(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_div_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_div_integer(mxs_runtime::MXObject *left,
                                                 mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_div_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_div_float(mxs_runtime::MXObject *left,
                                               mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_div_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_eq_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_eq_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_eq_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_eq_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_eq_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_eq_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_eq_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_eq_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_ne_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_ne_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_ne_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_ne_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_ne_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_ne_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_ne_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_ne_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_gt_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_gt_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_gt_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_gt_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_gt_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_gt_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_gt_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_gt_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_lt_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_lt_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_lt_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_lt_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_lt_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_lt_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_lt_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_lt_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_ge_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_ge_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_ge_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_ge_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_ge_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_ge_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_ge_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_ge_float(left, right);
}

MXS_API mxs_runtime::MXObject *integer_le_integer(mxs_runtime::MXObject *left,
                                                  mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_INT(right);
    return mxs_runtime::integer_le_integer(left, right);
}

MXS_API mxs_runtime::MXObject *integer_le_float(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_INT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::integer_le_float(left, right);
}

MXS_API mxs_runtime::MXObject *float_le_integer(mxs_runtime::MXObject *left,
                                                mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_INT(right);
    return mxs_runtime::float_le_integer(left, right);
}

MXS_API mxs_runtime::MXObject *float_le_float(mxs_runtime::MXObject *left,
                                              mxs_runtime::MXObject *right) {
    CHECK_FLOAT(left);
    CHECK_FLOAT(right);
    return mxs_runtime::float_le_float(left, right);
}

MXS_API mxs_runtime::MXObject *mxs_op_add(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_add(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_sub(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_sub(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_mul(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_mul(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_div(mxs_runtime::MXObject *left,
                                          mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_div(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_eq(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_eq(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_ne(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_ne(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_lt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_lt(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_le(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_le(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_gt(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_gt(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_ge(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_ge(*right);
}

MXS_API mxs_runtime::MXObject *mxs_op_is(mxs_runtime::MXObject *left,
                                         mxs_runtime::MXObject *right) {
    if (!left || !right) return new mxs_runtime::MXError("TypeError", "Invalid operand");
    return left->op_is(*right);
}

MXS_API mxs_runtime::inner_integer mxs_get_integer_value(mxs_runtime::MXObject *obj) {
    if (!obj || obj->type_info != &mxs_runtime::g_integer_type_info) { return 0; }
    auto *i = static_cast<mxs_runtime::MXInteger *>(obj);
    return i->value;
}

MXS_API mxs_runtime::MXObject *mxs_int_absolute(mxs_runtime::MXObject *integer_obj) {
    using namespace mxs_runtime;
    if (!integer_obj || integer_obj->type_info != &g_integer_type_info) {
        return new MXError("TypeError", "Argument must be an Integer.");
    }
    auto val = static_cast<MXInteger *>(integer_obj)->value;
    if (val < 0) val = -val;
    return MXCreateInteger(val);
}

auto MXCreateInteger(mxs_runtime::inner_integer value) -> mxs_runtime::MXInteger * {
    auto *obj = new mxs_runtime::MXInteger(value);
    return obj;
}

auto MXCreateFloat(mxs_runtime::inner_float value) -> mxs_runtime::MXFloat * {
    auto *obj = new mxs_runtime::MXFloat(value);
    return obj;
}
#ifdef __cplusplus
}// extern "C"
#endif